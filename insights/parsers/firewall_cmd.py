"""
FirewallD commands
==================

This module contains the following parsers:

FirewallCmdListALLZones - command ``/usr/bin/firewall-cmd --list-all-zones``
----------------------------------------------------------------------------
"""
from collections import defaultdict

from insights import parser, CommandParser
from insights.parsers import SkipException, ParseException
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
            forward-ports:
            source-ports:
            icmp-blocks:
            rich rules:


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
        >>> zones.zones['trusted']['target']
        'ACCEPT'

    Attributes:
        active_zones (list): A list of active zones
        zones (dict): A dict of zone info

    Raises:
        SkipException: Raised when firewalld is not running
        ParseException: Raised when the output is in invalid format
    """

    def parse_content(self, content):
        error_line = "firewalld is not running"
        if any(error_line in line.lower() for line in content):
            raise SkipException("no content")
        self.zones = defaultdict(dict)
        self.active_zones = []
        zone_start = True
        zone_name = ''
        for line in content:
            if not line.strip():
                zone_start = True
                continue
            if zone_start:
                name_info = line.strip().split(None, 1)
                if len(name_info) > 1 and 'active' in name_info[1]:
                    self.active_zones.append(name_info[0])
                zone_name = name_info[0]
                zone_start = False
            else:
                attrs = line.split(':', 1)
                if len(attrs) == 2:
                    self.zones[zone_name][attrs[0].strip()] = attrs[1].strip()
                else:
                    raise ParseException('Invalid format')
