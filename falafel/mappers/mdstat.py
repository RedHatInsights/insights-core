"""
mdstat
======
"""
import re
from falafel.core.plugins import mapper
from falafel.core import MapperOutput


@mapper("mdstat")
class Mdstat(MapperOutput):
    """
    Represents the information in the ``/proc/mdstat`` file.  Several
    examples of possible data containe in the file can be found on the
    `MDstat kernel.org wiki page<https://raid.wiki.kernel.org/index.php/Mdstat>`_.

    In particular, the discussion here will focus on initial extraction of information
    form lines such as:

        Personalities : [raid1] [raid6] [raid5] [raid4]
        md1 : active raid1 sdb2[1] sda2[0]
              136448 blocks [2/2] [UU]

        md2 : active raid1 sdb3[1] sda3[0]
              129596288 blocks [2/2] [UU]

        md3 : active raid5 sdl1[9] sdk1[8] sdj1[7] sdi1[6] sdh1[5] sdg1[4] sdf1[3] sde1[2] sdd1[1] sdc1[0]
              1318680576 blocks level 5, 1024k chunk, algorithm 2 [10/10] [UUUUUUUUUU]

    The data contained in ``mdstat`` is represented with two top level members

    Attributes
    ----------

    personalities : list
        A list of RAID levels the kernel currently supports

    components : list of dicts
        A list containing a dict of md component device information
        Each of these dicts contains the following keys

        - device_name: string - name of the array device
        - active: boolean - ``True`` if the array is active, ``False``
          if it is inactive.
        - component_name: string - name of the component device
        - raid: string - with the raid level, e.g., "raid1" for "md1"
        - role: int - raid role number
        - device_flag: str - device component status flag.  Known values
          include 'F' (failed device), 'S', and 'W'
        - up: boolean - ``True`` if the component device is up
        - auto_read_only: boolean - ``True`` if the array device is
          "auto-read-only"
    """

    def __init__(self, data, path):
        super(Mdstat, self).__init__(data, path)
        self.components = self.data["components"]
        self.personalities = self.data["personalities"]

    @staticmethod
    def parse_content(content):
        data = {'personalities': [], 'components': []}

        current_components = None
        in_component = False

        for line in content:
            line = line.strip()
            if line.startswith('Personalities'):
                in_component = False
                data['personalities'] = parse_personalities(line)
            elif line.startswith("md"):  # Starting a component array stanza
                in_component = True
                current_components = parse_array_start(line)
            elif not line:  # blank line, ending a component array stanza
                if in_component:
                    data['components'].extend(current_components)
                    current_components = None
                in_component = False
            else:
                if in_component:
                    upstring = parse_upstring(line)
                    if upstring:
                        apply_upstring(upstring, current_components)
        return data


def parse_personalities(personalities_line):
    """Parse the "personalities" line of ``/proc/mdstat``.

    Lines are expected to be like:

        Personalities : [linear] [raid0] [raid1] [raid5] [raid4] [raid6]

    If they do not have this format, an error will be raised since it
    would be considered an unexpected parsing error.

    Parameters
    ----------

    personalities_line : str
        A single "Personalities" line from an ``/proc/mdstat`` files.

    Returns
    -------
        A list of raid "personalities" listed on the line.
    """
    tokens = personalities_line.split()
    assert tokens.pop(0) == "Personalities"
    assert tokens.pop(0) == ":"

    personalities = []
    for token in tokens:
        assert token.startswith('[') and token.endswith(']')
        personalities.append(token.strip('[]'))

    return personalities


def parse_array_start(md_line):
    """Parse the initial line of a device array stanza in
    ``/proc/mdstat``.

    Lines are expected to be like:

        md2 : active raid1 sdb3[1] sda3[0]

    If they do not have this format, an error will be raised since it
    would be considered an unexpected parsing error.

    Parameters
    ----------

    md_line : str
        A single line from the start of a device array stanza from a
        ``/proc/mdstat`` file.

    Returns
    -------
        A list of dictionaries, one dictionrary for each component
        device making up the array.
    """
    components = []
    tokens = md_line.split()
    device_name = tokens.pop(0)
    assert device_name.startswith("md")
    assert tokens.pop(0) == ":"

    active_string = tokens.pop(0)
    active = False
    if active_string == "active":
        active = True
    else:
        assert active_string == "inactive"

    raid_read_only_token = tokens.pop(0)
    auto_read_only = False
    raid = None
    if raid_read_only_token == "(auto-read-only)":
        auto_read_only = True
        raid = tokens.pop(0)
    else:
        raid = raid_read_only_token

    for token in tokens:
        subtokens = re.split(r"\[|]", token)
        assert len(subtokens) > 1
        comp_name = subtokens[0]
        assert comp_name

        role = int(subtokens[1])

        device_flag = None
        if len(subtokens) > 2:
            device_flag = subtokens[2]
            if device_flag:
                device_flag = device_flag.strip('()')

        component_row = {"device_name": device_name,
                         "raid": raid,
                         "active": active,
                         "auto_read_only": auto_read_only,
                         "component_name": comp_name,
                         "role": role,
                         "device_flag": device_flag}
        components.append(component_row)
    return components


def parse_upstring(line):
    """Parse the subsequent lines of a  device array stanza in ``/proc/mdstat`` for the "up" indictor
    string.

    Lines are expected to be like:

        129596288 blocks [2/2] [UU]

    or

        1318680576 blocks level 5, 1024k chunk, algorithm 2 [10/10] [UUU_UUUUUU]

    In particular, this method searchs for the string like ``[UU]`` which
    indicates whether component devices or up, ``U`` or down, ``_``.

    Parameters
    ----------

    line : str
        A single line from a device array stanza.

    Returns
    -------
        The string containing a series of ``U``s and ``_``s if found in
        the string, and ``None`` if the uptime string is not found.
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

    Parameters
    ----------

    upstring : str
        String sequence of ``U``s and ``_``s as determined by the
        ``parse_upstring`` method

    component_list : list
        List of dictionaries output from the ``parse_array_start`` method.
    """
    assert len(upstring) == len(component_list)

    def add_up_key(comp_dict, up_indicator):
        assert up_indicator == 'U' or up_indicator == "_"
        comp_dict['up'] = True if up_indicator == 'U' else False

    map(add_up_key, component_list, upstring)
