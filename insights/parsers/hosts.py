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

from insights import Parser, parser
from insights.parsers import SkipException
from insights.specs import Specs


@parser(Specs.hosts)
class Hosts(Parser, dict):
    """
    Read the ``/etc/hosts`` file and parse it into a dictionary of host name
    lists, keyed on IP address.

    Raises:
        SkipException: When no useful data.
    """

    def parse_content(self, content):
        self._names = set()
        host_data = dict()
        for line in content:
            if "#" in line:
                line = line.split("#")[0]
            line = line.strip()
            words = line.split(None)
            if len(words) > 1:
                if words[0] not in host_data:
                    host_data[words[0]] = []
                host_data[words[0]].extend(words[1:])
                self._names.update(words[1:])

        if not host_data:
            raise SkipException("No useful data")

        self.update(host_data)
        for host_set in host_data.values():
            self._names.update(host_set)

    @property
    def data(self):
        """
        (dict): The parsed result as a dict with IP address as the key.
        """
        return self

    @property
    def all_names(self):
        """
        (set): The set of host names known, regardless of their IP address.
        """
        return self._names

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
