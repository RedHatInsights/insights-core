"""
OVSappctlFdbShowBridgeCount - command ``/usr/bin/ovs-appctl fdb/show [bridge-name]``
====================================================================================

This module provides class ``OVSappctlFdbShowBridgeCount`` for parsing the
output of command ``/usr/bin/ovs-appctl fdb/show [bridge-name]`` and return
the MAC entry count.

Sample command output::

    port VLAN  MAC Age
    6       1 MAC1 118
    3       0 MAC2 24

The content collected by insights-client::

    ['br-int:6', 'br-int1:21', 'br-tun:1', 'br0:0']

Examples:
    >>> data["br-int"]
    '6'
    >>> data.get("br0")
    '0'
    >>> "br-int1" in data
    True
"""

from insights import CommandParser, LegacyItemAccess, parser
from insights.parsers import ParseException, SkipException, optlist_to_dict
from insights.specs import Specs


@parser(Specs.ovs_bridge_mac_table_entry_count)
class OVSappctlFdbShowBridgeCount(CommandParser, LegacyItemAccess):
    """
       This class provides processing for the output of the command
       ``/usr/bin/ovs-appctl fdb/show [bridge-name]``.

       The content collected by insights-client::

           ['br-int:6', 'br-int1:21', 'br-tun:1', 'br0:0']

       Attributes:
           data (dict): A dictionary where each element contains
                        the bridge-name as key and MAC count as value.

       Raises:
           SkipException: When the file is empty.
           ParseException: When the input data format is incorrect.
    """

    def parse_content(self, content):
        """
           Input content is split on the basis of ':' and then the data for
           each bridge is stored as a key:value pair where key is the
           bridge name and value is the MAC count.
        """
        # No content found or file is empty
        if len(content) == 0:
            raise SkipException("Empty file")

        self.data = {}
        # Split the content on the basis of ':' and extract bridge details
        content = "".join(content).strip()
        if content.startswith("["):
            content = content.strip("[]").replace("'", "")
            self.data = optlist_to_dict(content, opt_sep=", ", kv_sep=":", strip_quotes=True)
        else:
            raise ParseException("Incorrect input data format")
