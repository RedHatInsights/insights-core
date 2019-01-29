"""
IfCFG - files ``/etc/sysconfig/network-scripts/ifcfg-*``
========================================================

IfCFG is a parser for the network interface definition files in
``/etc/sysconfig/network-scripts``.  These are pulled into the network
scripts using ``source``, so they are mainly ``bash`` environment
declarations of the form **KEY=value**.  These are stored in the ``data``
property as a dictionary.  Quotes surrounding the value

Three options are handled differently:

* ``BONDING_OPTS`` is usually a quoted list of key=value arguments separated
  by spaces.
* ``TEAM_CONFIG`` and ``TEAM_PORT_CONFIG`` are treated as JSON stored as a
  single string.  Double quotes within the string are escaped using double
  back slashes, and these are removed so that the quoting is preserved.

Because this parser reads multiple files, the interfaces are stored as a
list within the parser and need to be iterated through in order to find
specific interfaces.

Sample configuration from a teamed interface in file ``/etc/sysconfig/network-scripts/ifcfg-team1``::

    DEVICE=team1
    DEVICETYPE=Team
    ONBOOT=yes
    NETMASK=255.255.252.0
    IPADDR=192.168.0.1
    TEAM_CONFIG='{"runner": {"name": "lacp", "active": "true", "tx_hash": ["eth", "ipv4"]}, "tx_balancer": {"name": "basic"}, "link_watch": {"name": "ethtool"}}'

Examples:

    >>> for nic in shared[IfCFG]: # Parser contains list of all interfaces
    ...     print 'NIC:', nic.iname
    ...     print 'IP address:', nic['IPADDR']
    ...     if 'TEAM_CONFIG' in nic:
    ...         print 'Team runner name:', nic['TEAM_CONFIG']['runner']['name']
    ...
    NIC: team1
    IP addresss: 192.168.0.1
    Team runner name: lacp

"""

import json
import re
from collections import OrderedDict
from .. import parser, get_active_lines, LegacyItemAccess, CommandParser
from insights.specs import Specs

JSON_FIELDS = ["TEAM_CONFIG", "TEAM_PORT_CONFIG"]

QUOTES = "\"'"

bond_mode_map = {
    'balance-rr': 0,
    'active-backup': 1,
    'balance-xor': 2,
    'broadcast': 3,
    '802.3ad': 4,
    'balance-tlb': 5,
    'balance-alb': 6
}


@parser(Specs.ifcfg)
class IfCFG(LegacyItemAccess, CommandParser):
    """
    Parse `ifcfg-` file,return a dict contain ifcfg config file info.
    "iface" key is interface name parse from file name
    `TEAM_CONFIG`, `TEAM_PORT_CONFIG` will return a dict with user config dict
    `BONDING_OPTS` also will return a dict

    Properties:
        ifname (str): The interface name as defined in the name of the file
            (i.e. the part after ``ifcfg-``).
    """

    def __init__(self, context):
        super(IfCFG, self).__init__(context)
        self.data["iface"] = context.path.rsplit("-", 1)[1]
        self.ifname = self.data['iface']
        self._has_empty_line = any(l.strip() == '' for l in context.content)

    def parse_content(self, content):
        self.data = {}
        for line in get_active_lines(content):
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            # Since keys are variable names in bash, stripping quotes and
            # spaces off them makes no sense.
            key = key.strip().strip(QUOTES).upper()

            # In some cases we want to know what the actual value-side
            # of the key is before dequoting and stripping.
            if key in ["DEVICE", "MASTER", "TEAM_MASTER", "BONDING_OPTS"]:
                self.data["raw_{0}_value".format(key.split('_')[0].lower())] = value
            if key != "DEVICE":
                value = value.strip().strip(QUOTES)
            if key in JSON_FIELDS:
                value = json.loads(value.replace("\\", ""))
            if key == "BONDING_OPTS":
                value_map = OrderedDict()
                value = re.sub(r'\s*=\s*', '=', value)
                for key_value_pair in value.split():
                    sub_key, sub_value = [
                        s.strip() for s in key_value_pair.split("=", 1)
                    ]
                    value_map[sub_key] = sub_value
                value = value_map
            self.data[key] = value

    @property
    def bonding_mode(self):
        """
        (int) the numeric value of bonding mode, or `None` if no bonding
        mode is found.
        """
        if "BONDING_OPTS" not in self or 'mode' not in self['BONDING_OPTS']:
            return None

        m = self["BONDING_OPTS"]["mode"]
        if m.isdigit():
            return int(m)
        if m in bond_mode_map:
            return bond_mode_map[m]
        return None

    @property
    def has_empty_line(self):
        """
        (bool) `True` if the file has empty line else `False`.
        """
        return self._has_empty_line
