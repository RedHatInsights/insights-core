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
    >>> 'localhost6'in  hosts.all_names
    True
    >>> hosts.data['127.0.0.1']
    ['localhost', 'localhost.localdomain', 'localhost4', 'localhost4.localdomain4', 'fte.example.com']
    >>> sorted(hosts.get_nonlocal().keys())
    ['10.0.0.1', '10.0.0.2']
    >>> hosts.lines[-1]['ip']
    '10.0.0.2'
    >>> hosts.lines[2]['names']
    ['fte.example.com']

"""
from insights.core import Parser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.hosts)
class Hosts(Parser):
    """
    Read the ``/etc/hosts`` file and parse it into a dictionary of host name
    lists, keyed on IP address.
    """

    def parse_content(self, content):
        self._ips = set()
        self._names = set()
        self._lines = list()
        self._data = dict()
        for line in content:
            line = line.strip()
            if "#" in line:
                line = line.split("#")[0]
            words = line.split(None)
            if len(words) > 1:
                ip, names = words[0], words[1:]
                line_data = {'ip': ip, 'names': names, 'raw_line': line}
                self._ips.add(ip)
                self._names.update(names)
                self._lines.append(line_data)
                if ip not in self._data:
                    self._data[ip] = []
                self._data[ip].extend(names)

        if not self._data:
            raise SkipComponent("No useful data")

    @property
    def data(self):
        """
        (dict): The parsed result as a dict with IP address as the key.
        """
        return self._data

    @property
    def lines(self):
        """
        (list): List of the parsed lines in the original order, in the following
            format::

                {
                    'ip': '127.0.0.1',
                    'names': ['localhost', 'localhost.localdomain', 'localhost4', 'localhost4.localdomain4']
                    'raw_line:' '127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4'
                }
        """
        return self._lines

    @property
    def all_ips(self):
        """
        (set): The set of ip addresses known.
        """
        return self._ips

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
                    for ip, host_list in self._data.items()
                    if ip not in ("127.0.0.1", "::1"))

    def ip_of(self, hostname):
        """
        Return the (first) IP address given for this host name.  None is
        returned if no IP address is found.
        """
        for ip, host_list in self._data.items():
            if hostname in host_list:
                return ip
        return None
