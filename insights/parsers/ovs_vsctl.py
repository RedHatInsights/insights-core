"""
Open vSwitch ``ovs-vsctl`` - utility for querying ovs-vswitchd
==============================================================

Classes in this module are:

OVSvsctlList - command ``/usr/bin/ovs-vsctl list TBL [REC]``
------------------------------------------------------------

Parsers in this module are:

OVSvsctlListBridge - command ``/usr/bin/ovs-vsctl list bridge``
---------------------------------------------------------------
"""
from insights.core import CommandParser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.parsers import get_active_lines, optlist_to_dict
from insights.specs import Specs


class OVSvsctlList(CommandParser, list):
    """
    Class to parse output of command ``ovs-vsctl list TBL [REC]``.
    Generally, the data is in ``key:value`` format with values having
    data types as string, numbers, list or dictionary.

    Raises:
        SkipComponent: When file is empty.
    """
    def parse_content(self, content):
        """
           Details of the subset of the Open vSwitch database, which holds the configuration
           for the Open vSwitch daemon, are extracted and stored in a list as a dictionary.
        """
        # No content found or file is empty
        if not content:
            raise SkipComponent("Empty file")

        record = {}
        for line in get_active_lines(content):
            key, value = [i.strip() for i in line.split(":", 1)]
            parsed_value = value.strip('"')
            if value.startswith("{") and value.endswith("}"):
                parsed_value = {}
                value = value.strip("{}")
                if value:
                    parsed_value = optlist_to_dict(value, opt_sep=", ", strip_quotes=True)
            elif value.startswith("[") and value.endswith("]"):
                parsed_value = []
                value = value.strip("[]")
                if value:
                    parsed_value = [i.strip(' \t\"\'') for i in value.split(",")]

            if key in record:
                # A new record comes
                self.append(record)
                record = {}

            record[key] = parsed_value

        # Add the last record
        self.append(record)

    @property
    def data(self):
        """
        Set data as property to keep compatibility
        """
        return self


@parser(Specs.ovs_vsctl_list_bridge)
class OVSvsctlListBridge(OVSvsctlList):
    """
    Class to parse output of command ``ovs-vsctl list bridge``.

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
        >>> bridge_lists[1].get("name")
        'br-tun'
        >>> len(bridge_lists[1]["other_config"]) == 0
        True
    """
    pass
