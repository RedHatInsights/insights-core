"""
OVSappctlFdbShowBridgeCount - command ``/usr/bin/ovs-appctl fdb/show [bridge-name]``
====================================================================================

This module provides class ``OVSappctlFdbShowBridgeCount`` to parse the
output of command ``/usr/bin/ovs-appctl fdb/show [bridge-name]`` and returns
the MAC entry count.

Sample command output::

    port VLAN  MAC Age
    6       1 MAC1 118
    3       0 MAC2 24

The content collected by insights-client::

    {"br-int": 6, "br-int1": 21, "br-tun": 1, "br0": 0}

Examples:
    >>> data["br-int"]
    6
    >>> data.get("br0")
    0
    >>> "br-int1" in data
    True
"""

import json
from insights import CommandParser, LegacyItemAccess, parser
from insights.parsers import ParseException, SkipException
from insights.specs import Specs


@parser(Specs.ovs_bridge_mac_table_entry_count)
class OVSappctlFdbShowBridgeCount(CommandParser, LegacyItemAccess):
    """
       This class provides processing for the output of the command
       ``/usr/bin/ovs-appctl fdb/show [bridge-name]``.

       The content collected by insights-client::

           {"br-int": 6, "br-int1": 21, "br-tun": 1, "br0": 0}

       Attributes:
           data (dict): A dictionary where each element contains
                        the bridge-name as key and mac-count as value.

       Raises:
           SkipException: When the file is empty.
           ParseException: When the input data format or content is incorrect.
    """

    def parse_content(self, content):
        """
           Input content is stored as a dictionary where bridge-name is
           the key and mac-count is the value.
        """
        # No content found or file is empty
        if len(content) == 0:
            raise SkipException("Empty file")

        self.data = {}
        content = "".join(content).strip()
        try:
            self.data = json.loads(content)
        except Exception:
            raise ParseException("Incorrect content: '{0}'".format(content))
