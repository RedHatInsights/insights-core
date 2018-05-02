"""
Modprobe configuration
======================

The modprobe configuration files are normally available to rules as a list of
ModProbe objects.  This combiner turns those into one set of data, preserving
the original file name that defined modprobe configuration line using a tuple.

"""

from insights.core.plugins import combiner
from insights.parsers.modprobe import ModProbe
from .. import LegacyItemAccess

from collections import namedtuple


ModProbeValue = namedtuple("ModProbeValue", ['value', 'source'])
"""
A value from a ModProbe source
"""


@combiner(ModProbe)
class AllModProbe(LegacyItemAccess):
    """
    Combiner for accessing all the modprobe configuration files in one
    structure.

    It's important for our reporting and information purposes to know not
    only what the configuration was but where it was defined.  Therefore, the
    format of the data in this combiner is slightly different compared to the
    ModProbe parser.  Here, each 'value' is actually a 2-tuple, with the
    actual data first and the file name from whence the value came second.
    This does mean that you need to pull the value out of each item - e.g.
    using a list comprehension - but it means that every item is associated
    with the file it was defined in.

    In line with the ModProbe configuration parser, the actual value is
    usually a list of the space-separated parts on the line, and the
    definitions for each module are similarly kept in a list, which makes

    Thanks to the LegacyItemAccess class, this can also be treated as a
    dictionary for look-ups of data in the `data` attribute.

    Attributes:
        data (dict): The combined data structures, with each item as a
            2-tuple, as described above.
        bad_lines(list): The list of unparseable lines from all files, with
            each line as a 2-tuple as described above.

    Sample data files::

        /etc/modprobe.conf:
            # watchdog drivers
            blacklist i8xx_tco

            # Don't install the Firewire ethernet driver
            install eth1394 /bin/true

        /etc/modprobe.conf.d/no_ipv6.conf:
            options ipv6 disable=1
            install ipv6 /bin/true

    Examples:
        >>> all_modprobe = shared[AllModProbe]
        >>> all_modprobe['alias']
        []
        >>> all_modprobe['blacklist']
        {'i8xx_tco': ModProbeValue(True, '/etc/modprobe.conf')}
        >>> all_modprobe['install']
        {'eth1394': ModProbeValue(['/bin/true'], '/etc/modprobe.conf'),
         'ipv6': ModProbeValue(['/bin/true'], '/etc/modprobe.conf.d/no_ipv6.conf')}
    """
    def __init__(self, modprobe):
        self.data = {}
        self.bad_lines = []
        for mod in modprobe:
            filename = mod.file_path  # relative path inside archive
            # Copy data section
            for section, sectdict in mod.data.items():
                if section not in self.data:
                    self.data[section] = {}
                for name, value in sectdict.items():
                    if name in self.data[section]:
                        # append to this module's value - should only
                        # happen for aliases.
                        self.data[section][name][0].append(value)
                    else:
                        # create new tuple
                        self.data[section][name] = ModProbeValue(value=value, source=filename)
            # Copy bad lines, if any
            if mod.bad_lines:
                self.bad_lines.extend(
                    [ModProbeValue(value=line, source=filename) for line in mod.bad_lines]
                )
        super(AllModProbe, self).__init__()
