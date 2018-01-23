"""
Modprobe configuration - files ``/etc/modprobe.conf`` and ``/etc/modprobe.d/*``
===============================================================================

This parser collects command information from the Modprobe configuration
files and stores information about each module mentioned. Lines such as
comments and those without the commands 'alias', 'blacklist', 'install',
'options', 'remove' and 'softdep' are ignored.

Blacklisted modules simply have True as their value in the dictionary.  Alias
lines list the module last, and these are recorded as a list of aliases.  For
all other commands the module name (after the command) is used as the key,
and the rest of the line is split up and stored as a list.  Any lines that
don't parse, either because they're not long enough or because they don't
start with a valid keyword, are stored in the ``bad_lines`` property list.

Sample file ``/etc/modprobe.conf``::

    alias scsi_hostadapter2 qla2xxx
    alias scsi_hostadapter3 usb-storage
    alias net-pf-10 off
    alias ipv6 off
    alias bond0 bonding
    alias bond1 bonding
    options bonding max_bonds=2
    options bnx2 disable_msi=1

Examples:

    >>> mconf_list = shared[ModProbe] # A list: multiple files may be found
    >>> for mconf in mconf_list:
    ...     print "File:", mconf.file_name
    ...     print "Modules with aliases:", sorted(mconf.data['alias'].keys())
    File: /etc/modprobe.conf
    Modules with aliases: ['bonding', 'off', 'qla2xxx', 'usb-storage']
"""

from collections import defaultdict
from .. import Parser, parser, get_active_lines, LegacyItemAccess
from insights.specs import Specs


@parser(Specs.modprobe)
class ModProbe(LegacyItemAccess, Parser):
    """
    Parse Modprobe configuration files - /etc/modprobe.conf and files in the
    /etc/modprobe.d/ directory.
    """

    COMMAND_LIST = ["alias", "blacklist", "install", "options", "remove", "softdep"]

    def parse_content(self, content):
        self.data = defaultdict(dict)
        self.bad_lines = []
        for line in get_active_lines(content):
            parts = line.split()
            if len(parts) > 1 and parts[0] in self.COMMAND_LIST:
                command = parts[0]
                # Blacklist just gives the module name - set its value to True
                if command == 'blacklist':
                    self.data[command][parts[1]] = True
                elif parts[0] == 'alias':
                    # module name comes second for aliases
                    if len(parts) != 3:
                        self.bad_lines.append(line)
                        continue
                    modname = parts[2]
                    # one module can have multiple aliases
                    if modname not in self.data[command]:
                        self.data[command][modname] = []
                    self.data[command][modname].append(parts[1])
                else:
                    self.data[command][parts[1]] = parts[2:]
            else:
                self.bad_lines.append(line)
