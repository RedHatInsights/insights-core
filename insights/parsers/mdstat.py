"""
Mdstat - file ``/proc/mdstat``
==============================
"""
import re

from insights import parser, CommandParser
from insights.parsers import ParseException, SkipException
from insights.specs import Specs


@parser(Specs.mdstat)
class Mdstat(CommandParser):
    """
    Represents the information in the ``/proc/mdstat`` file.  Several
    examples of possible data containe in the file can be found on the
    `MDstat kernel.org wiki page <https://raid.wiki.kernel.org/index.php/Mdstat>`_.

    In particular, the discussion here will focus on initial extraction of information
    form lines such as::

        Personalities : [raid1] [raid6] [raid5] [raid4]
        md1 : active raid1 sdb2[1] sda2[0]
              136448 blocks [2/2] [UU]

        md2 : active raid1 sdb3[1] sda3[0]
              129596288 blocks [2/2] [UU]

        md3 : active raid5 sdl1[9] sdk1[8] sdj1[7] sdi1[6] sdh1[5] sdg1[4] sdf1[3] sde1[2] sdd1[1] sdc1[0]
              1318680576 blocks level 5, 1024k chunk, algorithm 2 [10/10] [UUUUUUUUUU]

        unused devices: <none>

    The data contained in ``mdstat`` is represented with three top level members -
    ``personalities``, ``components`` and ``mds``.

    Attributes:
        personalities (list): A list of RAID levels the kernel currently supports.
        components (list): A list containing a dict of md component device information.
            Each of these dicts contains the following keys

            - ``device_name`` : string - name of the array device
            - ``active`` : boolean - ``True`` if the array is active, ``False``
              if it is inactive.
            - ``component_name`` : string - name of the component device
            - ``raid`` : string - with the raid level, e.g., "raid1" for "md1"
            - ``role`` : int - raid role number
            - ``device_flag`` : str - device component status flag.  Known values
              include 'F' (failed device), 'S', and 'W'
            - ``up`` : boolean - ``True`` if the component device is up
            - ``auto_read_only`` : boolean - ``True`` if the array device is
              "auto-read-only"
            - ``blocks`` : the number of blocks in the device
            - ``level`` : the current RAID level, if found in the status line
            - ``chunk`` : the device chunk size, if found in the status line
            - ``algorithm`` : the current conflict resolution algorithm, if found
              in the status line
        mds (dict): A dictionary keyed on the MD device name.
            Each dict contains the following keys

            - ``name``: Name of the MD device
            - ``active``: Whether the MD device is active
            - ``raid``: The RAID type string
            - ``devices``: a list of the devices in this
            - ``blocks``, ``level``, ``chunk`` and ``algorithm`` - the same
              information given above per component device (if found)

    Examples:
        >>> type(mdstat)
        <class 'insights.parsers.mdstat.Mdstat'>
        >>> mdstat.personalities
        ['raid1', 'raid6', 'raid5', 'raid4']
        >>> len(mdstat.components)
        14
        >>> mdstat.components[0]['device_name']
        'md1'
        >>> sdb2 = mdstat.components[0]
        >>> sdb2['component_name']
        'sdb2'
        >>> sdb2['active']
        True
        >>> sdb2['raid']
        'raid1'
        >>> sdb2['role']
        1
        >>> sdb2['up']
        True
        >>> sorted(mdstat.mds.keys())
        ['md1', 'md2', 'md3']
        >>> mdstat.mds['md1']['active']
        True
        >>> len(mdstat.mds['md1']['devices'])
        2
        >>> mdstat.mds['md1']['devices'][0]['component_name']
        'sdb2'
    """
    def parse_content(self, content):
        if not content:
            raise SkipException("Empty output.")

        self.mds = {}
        self.components = []
        self.personalities = []

        current_components = None
        in_component = False

        for line in content:
            line = line.strip()
            if line.startswith('Personalities'):
                # If the line doesn't have any raid types then md raid isn't active.
                if line == "Personalities :":
                    raise SkipException("No parseable md devices present.")

                in_component = False
                self.personalities = parse_personalities(line)
            # Starting a component array stanza.
            elif line.startswith("md"):
                in_component = True
                current_components = parse_array_start(line)
            # Catch any blank lines, this signals
            # the end of the component array stanza.
            elif not line:
                if in_component:
                    self.components.extend(current_components)
                    current_components = None
                in_component = False
            else:
                if in_component:
                    parse_array_status(line, current_components)
                    upstring = parse_upstring(line)
                    if upstring:
                        apply_upstring(upstring, current_components)

        # Map component devices into MDs dictionary by device name.
        for comp in self.components:
            devname = comp['device_name']
            if devname not in self.mds:
                #     md2 : active raid1 sdb3[1] sda3[0]
                #           129596288 blocks [2/2] [UU]
                self.mds[devname] = {
                    'name': devname, 'active': comp['active'],
                    'raid': comp['raid'], 'blocks': comp['blocks'],
                    'devices': []
                }
                for opt in ['level', 'chunk', 'algorithm']:
                    if opt in comp:
                        self.mds[devname][opt] = comp[opt]
            self.mds[devname]['devices'].append(dict(
                (k, comp[k]) for k in comp if k in ['component_name', 'role', 'up']
            ))

        # Keep self.data just for backwards compatibility.
        self.data = {
            'personalities': self.personalities,
            'components': self.components
        }


def parse_personalities(personalities_line):
    """
    Parse the "personalities" line of ``/proc/mdstat``.

    Sample of personalities_line::

        Personalities : [linear] [raid0] [raid1] [raid5] [raid4] [raid6]

    Args:
        personalities_line (str): A single "Personalities" line from an
        ``/proc/mdstat`` files.

    Returns:
        list: A list of raid "personalities" listed on the line.

    Raises:
        ParseException: If the format isn't like the sample above.
    """
    personalities = []

    if "Personalities :" not in personalities_line:
        raise ParseException("Incorrectly formatted personalities line.")

    tokens = personalities_line.split()
    for token in tokens[2:]:
        if token.startswith('[') and token.endswith(']'):
            personalities.append(token.strip('[]'))
        else:
            raise ParseException("Incorrectly formatted personalities line.")

    return personalities


def parse_array_start(md_line):
    """
    Parse the initial line of a device array stanza in ``/proc/mdstat``.

    Sample of md_line::

        md2 : active raid1 sdb3[1] sda3[0]

    Args:
        md_line (str): A single line from the start of a device array stanza.

    Returns:
        list: A list of dictionaries, one dictionary for each component
            device making up the array.

    Raises:
        ParseException: If the format isn't like the sample above.
    """
    auto_read_only = False
    components = []
    device_flag = None
    raid = None

    # Split the line to create tokens, and
    # set device_name to the first token.
    tokens = md_line.split()
    device_name = tokens.pop(0)

    if not device_name.startswith("md") or ":" not in tokens:
        raise ParseException("The md line isn't as expected.")

    # Remove the : symbol.
    tokens.pop(0)

    active_string = tokens.pop(0)
    if active_string == "active":
        active = True
    elif active_string == "inactive":
        active = False
    else:
        raise ParseException("The raid isn't marked as active or inactive.")

    # Only active raids have the auto-read-only
    # entry or the raid level.
    if active:
        raid_read_only_token = tokens.pop(0)
        if raid_read_only_token == "(auto-read-only)":
            auto_read_only = True
            raid = tokens.pop(0)
        else:
            raid = raid_read_only_token

    for token in tokens:
        # Token should be sda1[0] or sda1[0](S) for
        # example, and subtokens should be
        # ['sda1', '0'] or ['sda1', '0', '(S)'].
        subtokens = re.split(r"[\[\]]", token)

        if len(subtokens) <= 1:
            raise ParseException("The len of subtokens '{s_tokens}' is incorrect.".format(s_tokens=subtokens))

        comp_name = subtokens[0]
        role = int(subtokens[1])

        if len(subtokens) > 2:
            device_flag = subtokens[2].strip('()')

        components.append({
            "device_name": device_name,
            "raid": raid,
            "active": active,
            "auto_read_only": auto_read_only,
            "component_name": comp_name,
            "role": role,
            "device_flag": device_flag
        })

    return components


def parse_array_status(line, components):
    """
    Parse the array status line, e.g.::

        1318680576 blocks level 5, 1024k chunk, algorithm 2 [10/10] [UUUUUUUUUU]

    This retrieves the following pieces of information:

    * ``blocks`` - (int) number of blocks in the whole MD device (always present)
    * ``level`` - (int) if found, the present RAID level
    * ``chunksize`` - (str) if found, the size of the data chunk in kilobytes
    * ``algorithm`` - (int) if found, the current algorithm in use.

    Because of the way data is stored per-component and not per-array, this
    then puts the above keys into each of the component dictionaries in the
    list we've been given.

    Sample data::

        1250241792 blocks super 1.2 level 5, 64k chunk, algorithm 2 [5/5] [UUUUUU]
        1465151808 blocks level 5, 64k chunk, algorithm 2 [4/3] [UUU_]
        136448 blocks [2/2] [UU]
        6306 blocks super external:imsm<Paste>

    Args:
        line (str): The array status line to parse.
        components (list): A list of component dicts.
    """
    status_line_re = r'(?P<blocks>\d+) blocks' + \
        r'(?: super (?P<super>\S+))?' + \
        r'(?: level (?P<level>\d+),)?' + \
        r'(?: (?P<chunk>\d+k) chunk,)?' + \
        r'(?: algorithm (?P<algorithm>\d+))?'
    # Since we're only called once per line, unless there's a good way to
    # cache this regular expression in compiled form we're going to have to
    # compile it each time.
    status_line_rex = re.compile(status_line_re)
    match = status_line_rex.search(line)
    if match:
        attributes = {'blocks': int(match.group('blocks'))}
        if match.group('level'):
            attributes['level'] = int(match.group('level'))
        if match.group('chunk'):
            attributes['chunk'] = match.group('chunk')
        if match.group('algorithm'):
            attributes['algorithm'] = int(match.group('algorithm'))
        for comp in components:
            comp.update(attributes)


def parse_upstring(line):
    """
    Parse the subsequent lines of a device array stanza in ``/proc/mdstat``
    for the "up" indicator string. The up indicator is "U" and down indicator
    is "_".

    Samples of line::

        129596288 blocks [2/2] [UU]
        1318680576 blocks level 5, 1024k chunk, algorithm 2 [10/10] [UUU_UUUUUU]

    Parameters
        line (str): A single line from a device array stanza.

    Returns:
        str: The string containing a series of ``U`` and ``_`` characters if
        found in the string, and ``None`` if the up string is not found.
    """
    UP_STRING_REGEX = r"\[(U|_)+]"

    match = re.search(UP_STRING_REGEX, line)
    if match:
        return match.group().strip('[]')
    else:
        return None


def apply_upstring(upstring, component_list):
    """Update the dictionaries resulting from ``parse_array_start`` with
    the "up" key based on the upstring returned from ``parse_upstring``.

    The function assumes that the upstring and component_list parameters
    passed in are from the same device array stanza of a
    ``/proc/mdstat`` file.

    The function modifies component_list in place, adding or updating
    the value of the "up" key to True if there is a corresponding ``U``
    in the upstring string, or to False if there is a corresponding
    ``_``.

    If there the number of rows in component_list does not match the
    number of characters in upstring, an ``AssertionError`` is raised.

    Args:
        upstring (str): String sequence of ``U``s and ``_``s as determined
            by the ``parse_upstring`` method.
        component_list (list): List of dictionaries output from the
            ``parse_array_start`` method.
    """
    def add_up_key(comp, up_char):
        if up_char not in ['U', '_']:
            raise ParseException("Invalid character for up_indicator '{word}'.".format(word=up_char))

        comp['up'] = up_char == 'U'

    if len(upstring) != len(component_list):
        raise ParseException("Length of upstring and component_list doesn't match.")

    for comp_dict, up_indicator in zip(component_list, upstring):
        add_up_key(comp_dict, up_indicator)
