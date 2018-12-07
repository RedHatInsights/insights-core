"""
NetworkNamespace = ``/bin/ls /var/run/netns``
=============================================

This specs provides list of network namespace created on the host machine.

Typical output of this command is as below::

    temp_netns  temp_netns_2  temp_netns_3


The ``/bin/ls /var/run/netns`` is prefered over ``/bin/ip netns list`` because it works on
all RHEL versions, no matter ip package is installed or not.

Examples:
    >>> type(netns_obj)
    <class 'insights.parsers.net_namespace.NetworkNamespace'>
    >>> netns_obj.netns_list
    ['temp_netns', 'temp_netns_2', 'temp_netns_3']
    >>> len(netns_obj.netns_list)
    3
"""

from insights import Parser, parser, get_active_lines
from insights.parsers import SkipException
from insights.specs import Specs


@parser(Specs.namespace)
class NetworkNamespace(Parser):
    def parse_content(self, content):
        if not content:
            raise SkipException('Nothing to parse.')

        self._netns_list = []
        for line in get_active_lines(content):
            self._netns_list.extend(line.split())

    @property
    def netns_list(self):
        """
        This method returns list of network namespace created
        in process memory.

        Returns:

            `list` of network namepaces if exists.
        """
        return self._netns_list
