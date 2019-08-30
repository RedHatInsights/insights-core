"""
hostname - command ``/bin/hostname``
====================================

This parser simply reads the output of ``/bin/hostname``, which is the
configured fully qualified domain name of the client system.  It then
splits it into ``hostname`` and ``domain`` and stores these as attributes,
along with the unmodified name in the ``fqdn`` attribute.

Examples:

    >>> hostname = shared[Hostname]
    >>> hostname.fqdn
    'www.example.com'
    >>> hostname.hostname
    'www'
    >>> hostname.domain
    'example.com'

HostnameI - command ``hostname -I``
-----------------------------------

"""

from . import ParseException
from .. import parser, CommandParser
from insights.specs import Specs


@parser(Specs.hostname)
class Hostname(CommandParser):
    """Class for parsing ``hostname`` command output.

    Attributes:
        fqdn: The fully qualified domain name of the host. The same to
            ``hostname`` when domain part is not set.
        hostname: The hostname.
        domain: The domain get from the fqdn.
    """
    def parse_content(self, content):
        content = list(filter(None, content))
        if len(content) != 1:
            msg = "hostname data contains multiple non-empty lines"
            raise ParseException(msg)
        raw = content[0].strip()
        self.fqdn = raw
        self.hostname = raw.split(".")[0] if raw else None
        self.domain = ".".join(raw.split(".")[1:]) if raw else None

    def __str__(self):
        return "<hostname: {h}, domain: {d}>".format(h=self.hostname, d=self.domain)


@parser(Specs.ip_addresses)
class HostnameI(CommandParser):
    """
    Class for parsing ``hostname -I`` command output.

    Attributes:
        raw: The raw output the ``hostname -I`` command
        ipv4: The IPv4 address of the host
        ipv6: The IPv6 address of the host
    """
    def parse_content(self, content):
        content = list(filter(None, content))
        if len(content) != 1:
            msg = "hostname data contains multiple non-empty lines"
            raise ParseException(msg)
        self.ipv4 = self.ipv6 = None
        self.raw = content[0].strip()
        for v in self.raw.split(None, 1):
            if '.' in v:
                self.ipv4 = v.strip()
            elif ':' in v:
                self.ipv6 = v.strip()

        if not self.ipv4:
            raise ParseException('No IPv4 address is found')
