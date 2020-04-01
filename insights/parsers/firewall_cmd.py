"""
FirewallD commands
==================

This module contains the following parsers:

FirewallCmdListALLZones - command ``/usr/bin/firewall-cmd --list-all-zones``
----------------------------------------------------------------------------
"""

from insights import parser, CommandParser
from insights.parsers import ParseException
from insights.specs import Specs


@parser(Specs.firewall_cmd_list_all_zones)
class FirewallCmdListALLZones(CommandParser):
    """
    Class for parsing the `/usr/bin/firewall-cmd --list-all-zones` command.

    Typical content of the command is::

        public (active)
            target: default
            icmp-block-inversion: no
            interfaces: eno1
            sources:
            services: dhcpv6-client ssh
            ports:
            protocols:
            masquerade: no
            forward-ports: port=80:proto=tcp:toport=12345:toaddr=
                port=81:proto=tcp:toport=1234:toaddr=
                port=83:proto=tcp:toport=456:toaddr=10.72.47.45
            source-ports:
            icmp-blocks:
            rich rules:
                rule family="ipv4" source address="10.0.0.0/24" destination address="192.168.0.10/32" port port="8080-8090" protocol="tcp" accept
                rule family="ipv4" source address="10.0.0.0/24" destination address="192.168.0.10/32" port port="443" protocol="tcp" reject
                rule family="ipv4" source address="192.168.0.10/24" reject
                rule family="ipv6" source address="1:2:3:4:6::" forward-port port="4011" protocol="tcp" to-port="4012" to-addr="1::2:3:4:7"


        trusted
            target: ACCEPT
            icmp-block-inversion: no
            interfaces:
            sources:
            services:
            ports:
            protocols:
            masquerade: no
            forward-ports:
            source-ports:
            icmp-blocks:
            rich rules:

    Examples:
        >>> type(zones)
        <class 'insights.parsers.firewall_cmd.FirewallCmdListALLZones'>
        >>> 'public' in zones.active_zones
        True
        >>> 'ACCEPT' in zones.zones['trusted']['target']
        True
        >>> zones.zones['public']['services']
        ['dhcpv6-client ssh']
        >>> 'port=83:proto=tcp:toport=456:toaddr=10.72.47.45' in zones.zones['public']['forward-ports']
        True


    Attributes:
        zones (dict): A dict of zone info

    Raises:
        ParseException: Raised when the output is in invalid format
    """

    def __init__(self, context):
        super(FirewallCmdListALLZones, self).__init__(context, ["firewalld is not running"])

    @property
    def active_zones(self):
        """Return a list of active zone name"""
        return [zone for zone, d in self.zones.items() if 'active' in d.get('_attributes', [])]

    def parse_content(self, content):
        self.zones = dict()
        zone_line = True
        zone_name = ''
        zone_attr_index = -1
        zone_attr_name = ''
        for line in content:
            line_strip = line.strip()
            if not line_strip:
                zone_line = True
                continue
            if zone_line:
                name_info = line_strip.split(None, 1)
                zone_name = name_info[0]
                self.zones[zone_name] = {}
                if len(name_info) > 1:
                    self.zones[zone_name]['_attributes'] = [i.strip() for i in name_info[1].strip('()').split(',')]
                zone_line = False
                zone_attr_index = -1
            else:
                current_index = len(line.rstrip()) - len(line_strip)
                zone_attr_index = current_index if zone_attr_index == -1 else zone_attr_index
                if current_index == zone_attr_index:
                    attrs = [i.strip() for i in line.split(':', 1)]
                    if len(attrs) != 2:
                        raise ParseException('Invalid format')
                    zone_attr_name, attr_value = attrs
                    attr_value = [attr_value] if attr_value else []
                    self.zones[zone_name][zone_attr_name] = attr_value
                else:
                    self.zones[zone_name][zone_attr_name].append(line_strip)
