"""
Hosts - file ``/etc/hosts``
===========================

This parser parses the ``/etc/hosts`` file, strips the comments, ignores the
blank lines, and collects the host names by IP address.  IPv4 and IPv6
addresses are supported.

Sample hosts file::

    127.0.0.1 localhost localhost.localdomain localhost4 localhost4.localdomain4
    ::1 localhost localhost.localdomain localhost6 localhost6.localdomain6
    # The same IP address can appear more than once, with different names
    127.0.0.1 fte.example.com

    10.0.0.1 nonlocal.example.com nonlocal2.fte.example.com
    10.0.0.2 other.host.example.com # Comments at end of line are ignored

Examples:

    >>> hosts = shared[Hosts]
    >>> len(hosts.all_names)
    10
    >>> hosts.all_names[0] # uses a set, so may not be in same order
    'localhost6'
    >>> hosts.data['127.0.0.1']
    ['localhost', 'localhost.localdomain', 'localhost4', 'localhost4.localdomain4',
     'fte.example.com']
    >>> hosts.get_nonlocal()
    {'10.0.0.1': ['nonlocal.example.com', 'nonlocal2.fte.example.com'],
     '10.0.0.2': ['other.host.example.com']}

"""

from collections import defaultdict
from .. import Parser, parser
from insights.specs import Specs


@parser(Specs.hosts)
class Hosts(Parser):
    """
    Read the ``/etc/hosts`` file and parse it into a dictionary of host name
    lists, keyed on IP address.
    """

    def parse_content(self, content):
        host_data = defaultdict(list)
        for line in content:
            line = line.strip()
            if "#" in line:
                line = line.split("#")[0]
            words = line.split(None)
            if len(words) > 1:
                host_data[words[0]].extend(words[1:])
        self.data = dict(host_data)

    @property
    def all_names(self):
        """
        (set): The set of host names known, regardless of their IP address.
        """
        names = set()
        for host_set in self.data.values():
            names.update(host_set)
        return names

    def get_nonlocal(self):
        """
        A dictionary of host name lists, keyed on IP address, that are not
        the 'localhost' addresses '127.0.0.1' or '::1'.
        """
        return dict((ip, host_list)
                    for ip, host_list in self.data.items()
                    if ip not in ("127.0.0.1", "::1"))

    def ip_of(self, hostname):
        """
        Return the (first) IP address given for this host name.  None is
        returned if no IP address is found.
        """
        for ip, host_list in self.data.items():
            if hostname in host_list:
                return ip
        return None
