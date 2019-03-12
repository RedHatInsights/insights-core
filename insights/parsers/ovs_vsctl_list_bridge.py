"""
OVSvsctlListBridge - command ``/usr/bin/ovs-vsctl list bridge``
===============================================================

This module provides class ``OVSvsctlListBridge`` for parsing the
output of command ``ovs-vsctl list bridge``.
Filters have been added so that sensitive information can be filtered out.
This results in the modification of the original structure of data.
"""

import re
from insights import LegacyItemAccess, CommandParser, parser
from insights.core.filters import add_filter
from insights.parsers import SkipException, optlist_to_dict
from insights.specs import Specs

FILTERS = ["name", "other_config", "mac-table-size"]
add_filter(Specs.ovs_vsctl_list_bridge, FILTERS)


@parser(Specs.ovs_vsctl_list_bridge)
class OVSvsctlListBridge(LegacyItemAccess, CommandParser):
    """
    Class to parse output of command ``ovs-vsctl list bridge``.
    Generally, the data is in key:value format with values having
    data types as string, numbers, list or dictionary.
    The class provides attribute ``data`` as list with lines parsed
    line by line based on keys for each bridge.

    Sample command output::

        name                : br-int
        other_config        : {disable-in-band="true", mac-table-size="2048"}
        name                : br-tun
        other_config        : {}

    Examples:
        >>> bridge_lists[0]["name"]
        'br-int'
        >>> bridge_lists[0]["other_config"]["mac-table-size"]
        '2048'
        >>> bridge_lists[0]["other_config"]["disable-in-band"]
        'true'
        >>> bridge_lists[1]["name"]
        'br-tun'
        >>> len(bridge_lists[1]["other_config"]) == 0
        True

    Attributes:
        data (list): A list containing dictionary elements where each
                     element contains the details of a bridge.

    Raises:
        SkipException: When file is empty.
    """

    bridge_keys = ("_uuid", "auto_attach", "controller", "datapath_id",
            "datapath_type", "datapath_version", "external_ids", "fail_mode",
            "flood_vlans", "flow_tables", "ipfix", "mcast_snooping_enable:",
            "mirrors", "name", "netflow", "other_config", "ports", "protocols",
            "rstp_enable", "rstp_status", "sflow", "status", "stp_enable")

    def parse_content(self, content):
        """
           Input content is split on the basis of key 'name' as details for multiple
           bridges will be present and then the extracted data for each bridge
           is stored in a dictionary.
        """
        # No content found or file is empty
        if not content:
            raise SkipException("Empty file")

        self.data = []
        bridge_details = {}
        for line in content:
            key, value = [i.strip() for i in line.split(":", 1)]
            parsed_value = value
            if value.startswith("{") and value.endswith("}"):
                value = value.strip("{}")
                parsed_value = {}
                if value:
                    parsed_value = optlist_to_dict(value, opt_sep=", ", strip_quotes=True)
            elif value.startswith("[") and value.endswith("]"):
                value = value.strip("[]")
                parsed_value = []
                if value:
                    parsed_value = [i.strip(' \t\r\n\"\'') for i in value.split(",")]
            elif value.startswith("\"") and value.endswith("\""):
                parsed_value = value.strip('"')
            if key not in bridge_details:
                bridge_details[key] = parsed_value
            elif key in bridge_details:
                # A new bridge comes
                self.data.append(bridge_details)
                bridge_details= {key: parsed_value}
        # Add the last bridge
        self.data.append(bridge_details)
