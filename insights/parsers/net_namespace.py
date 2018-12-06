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
    >>> netns_obj.get_netns
    ['temp_netns', 'temp_netns_2', 'temp_netns_3']
    >>> len(netns_obj.get_netns)
    3
"""

from insights import Parser, parser, get_active_lines
from insights.specs import Specs


@parser(Specs.namespace)
class NetworkNamespace(Parser):
    def parse_content(self, content):
        self.netns_list = []
        for line in get_active_lines(content):
            netns = line.split(" ")
            if netns and '' in netns:
                self.netns_list = [x for x in netns if x]
            elif netns:
                self.netns_list.append(netns[0])

    @property
    def get_netns(self):
        """
        This method returns list of network namespace created
        in process memory.

        Returns:

            `list` of network namepaces if exists, else
            `empty list` if network namespaces if do not exists
        """
        return self.netns_list
