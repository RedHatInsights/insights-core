"""
OVSvsctlListBridge - command ``/usr/bin/ovs-vsctl list bridge``
===============================================================

This module provides class ``OVSvsctlListBridge`` for parsing the
output of command ``ovs-vsctl list bridge``.
Filters have been added so that sensitive information can be filtered out.
This results in the modification of the original structure of data.

Sample filtered command output::

    name                : br-int
    other_config        : {disable-in-band="true", mac-table-size="2048"}
    name                : br-tun
    other_config        : {}

Examples:
    >>> data[0]["name"]
    'br-int'
    >>> data[0]["other_config"]["mac-table-size"]
    '2048'
    >>> data[0]["other_config"]["disable-in-band"]
    'true'
    >>> data[1]["name"]
    'br-tun'
    >>> len(data[1]["other_config"]) == 0
    True
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

       Attributes:
           data (list): A list containing dictionary elements where each
                        element contains the details of a bridge.

       Raises:
        SkipException: When file is empty or value is not present for a key.
    """

    def parse_content(self, content):
        """
           Input content is split on the basis of key 'name' as details for multiple
           bridges will be present and then the extracted data for each bridge
           is stored in a dictionary.
        """
        # No content found or file is empty
        if len(content) == 0:
            raise SkipException("Empty file")

        self.data = []
        content = ",".join(content).strip()

        # Split the content on the basis of key 'name' and extract bridge details
        key_list = [key.start() for key in re.finditer("name", content)]
        bridge_details = []
        for start in range(len(key_list)):
            if start != len(key_list) - 1:
                info = content[key_list[start]:key_list[start + 1] - 1]
            else:
                info = content[key_list[start]:]
            bridge_details.append(info.split(",", 1))

        # Extract and store the data for each bridge
        for line in bridge_details:
            details = {}
            for parameters in line:
                try:
                    key, value = parameters.split(": ")
                except Exception:
                    key = parameters[:-1].strip()
                    raise SkipException("Value not present for the key {0}".format(key))

                if value[0].startswith("{"):
                    if not re.match(r"(\{\s*\})+", value):
                        value = optlist_to_dict(value.strip("{}"), opt_sep=", ", strip_quotes=True)
                    else:
                        value = {}
                details[key.strip()] = value
            self.data.append(details)
