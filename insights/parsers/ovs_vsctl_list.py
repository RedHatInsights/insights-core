"""
OVSvsctlList - command ``/usr/bin/ovs-vsctl list TBL [REC]``
============================================================

This module provides class ``OVSvsctlList`` for parsing the
output of command ``ovs-vsctl list TBL [REC]``.
"""

from insights import CommandParser, get_active_lines, parser
from insights.parsers import SkipException, optlist_to_dict
from insights.specs import Specs


@parser(Specs.ovs_vsctl_list_bridge)
class OVSvsctlList(CommandParser):
    """
    Class to parse output of command ``ovs-vsctl list TBL [REC]``.
    Generally, the data is in key:value format with values having
    data types as string, numbers, list or dictionary.
    The class provides attribute ``data`` as list with lines parsed
    line by line based on keys for each bridge.

    Sample command output::

        name                : br-int
        other_config        : {disable-in-band="true", mac-table-size="2048"}
        name                : br-tun

    Examples:
        >>> bridge_lists[0]["name"]
        'br-int'
        >>> bridge_lists[0]["other_config"]["mac-table-size"]
        '2048'
        >>> bridge_lists[0]["other_config"]["disable-in-band"]
        'true'
        >>> bridge_lists[1].get("name")
        'br-tun'

    Attributes:
        data (list): A list containing dictionary elements where each
                     element contains the details of a bridge.

    Raises:
        SkipException: When file is empty.
    """
    def parse_content(self, content):
        """
           Details of the subset of the Open vSwitch database, which holds the configuration
           for the Open vSwitch daemon, are extracted and stored in a list as a dictionary.
        """
        # No content found or file is empty
        if not content:
            raise SkipException("Empty file")

        self.data = []
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
                self.data.append(record)
                record = {}

            record[key] = parsed_value

        # Add the last record
        self.data.append(record)

    def __getitem__(self, line):
        return self.data[line]
