"""
IpNetnsExecNamespaceLsofI - command ``/sbin/ip netns exec [network-namespace] lsof -i"``
========================================================================================

This module provides class ``IpNetnsExecNamespaceLsofI`` for parsing the output of command
``/sbin/ip netns exec [network-namespace] lsof -i``.
Filters have been added so that sensitive information can be filtered out.
This results in the modification of the original structure of data.
"""

from collections import namedtuple
from insights import CommandParser, parser
from insights.core.filters import add_filter
from insights.parsers import SkipException, keyword_search, parse_fixed_table
from insights.specs import Specs

add_filter(Specs.ip_netns_exec_namespace_lsof, "COMMAND")


@parser(Specs.ip_netns_exec_namespace_lsof)
class IpNetnsExecNamespaceLsofI(CommandParser):
    """
       This class provides processing for the output of command
       ``/sbin/ip netns exec [network-namespace] lsof -i``.

       Sample command output::

           COMMAND   PID   USER    FD  TYPE  DEVICE     SIZE/OFF  NODE NAME
           neutron-n 975   root    5u  IPv4  6482691    0t0        TCP *:http (LISTEN)

       Examples:
           >>> len(ns_lsof.search(command="neutron-n"))
           1
           >>> ns_lsof.data[0]["command"] == "neutron-n"
           True

       Attributes:
           fields (list): List of ``KeyValue`` namedtupules for each line
                          in the command.

           data (list): List of key value pair derived from the command.

       Raises:
           SkipException: When the file is empty or data is useless.
    """
    keyvalue = namedtuple("KeyValue",
                          ["command", "pid", "user", "fd", "type", "device", "size_off", "node", "name"])

    def parse_content(self, content):
        self.fields = []
        self.data = []
        if not content:
            raise SkipException("Empty file")

        self.data = parse_fixed_table(content,
                                      heading_ignore=["COMMAND", "PID", "USER", "FD", "TYPE", "DEVICE", "SIZE/OFF", "NODE", "NAME"],
                                      header_substitute=[("COMMAND", "command"), ("PID", "pid"), ("USER", "user"), ("FD", "fd"),
                                                         ("TYPE", "type"), ("DEVICE", "device"), ("SIZE/OFF", "size_off"),
                                                         ("NODE", "node"), ("NAME", "name")])
        if not self.data:
            raise SkipException("Useless data")

        for item in self.data:
            self.fields.append(self.keyvalue(item["command"], item["pid"], item["user"], item["fd"], item["type"], item["device"],
                               item["size_off"], item["node"], item["name"]))

    def __iter__(self):
        return iter(self.fields)

    def search(self, **kw):
        """Search item based on key value pair.

        Example:

            >>> len(ns_lsof.search(command="neutron-n")) == 1
            True
            >>> len(ns_lsof.search(user="nobody")) == 0
            True
        """
        return keyword_search(self.data, **kw)
