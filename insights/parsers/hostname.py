"""
hostname - command ``/bin/hostname``
====================================

"""

from insights.parsers import ParseException
from insights import parser, CommandParser
from insights.specs import Specs


class HostnameBase(CommandParser):
    """
    The base parser class for command ``hostname``.
    """
    def parse_content(self, content):
        content = list(filter(None, content))
        if len(content) != 1:
            msg = "hostname data contains multiple non-empty lines"
            raise ParseException(msg)


@parser(Specs.hostname)
class Hostname(HostnameBase):
    """
    This parser simply reads the output of ``/bin/hostname``, which is the
    configured fully qualified domain name of the client system.  It then
    splits it into ``hostname`` and ``domain`` and stores these as attributes,
    along with the unmodified name in the ``fqdn`` attribute.

    Examples:

    >>> hostname.fqdn
    'www.example.com'
    >>> hostname.hostname
    'www'
    >>> hostname.domain
    'example.com'

    Attributes:
        fqdn: The fully qualified domain name of the host. The same to
            ``hostname`` when domain part is not set.
        hostname: The hostname.
        domain: The domain get from the fqdn.
    """
    def parse_content(self, content):
        super(Hostname, self).parse_content(content)
        raw = content[0].strip()
        self.fqdn = raw
        self.hostname = raw.split(".")[0] if raw else None
        self.domain = ".".join(raw.split(".")[1:]) if raw else None

    def __str__(self):
        return "<hostname: {h}, domain: {d}>".format(h=self.hostname, d=self.domain)


@parser(Specs.hostname_default)
class HostnameDefault(HostnameBase):
    """
    This parser simply reads the output of ``/bin/hostname``, which is the
    configured fully qualified domain name of the client system.  It then
    splits it into ``hostname`` and ``domain`` and stores these as attributes,
    along with the unmodified name in the ``fqdn`` attribute.

    Examples:

    >>> hostname.fqdn
    'www.example.com'
    >>> hostname.hostname
    'www'
    >>> hostname.domain
    'example.com'

    Attributes:
        hostname: The hostname.
    """
    def parse_content(self, content):
        super(Hostname, self).parse_content(content)
        raw = content[0].strip()
        self.hostname = raw.split(".")[0] if raw else None

    def __str__(self):
        return "<hostname: {h}, domain: {d}>".format(h=self.hostname, d=self.domain)


@parser(Specs.hostname_short)
class HostnameShort(HostnameBase):
    """
    This parser simply reads the output of ``/bin/hostname``, which is the
    configured fully qualified domain name of the client system.  It then
    splits it into ``hostname`` and ``domain`` and stores these as attributes,
    along with the unmodified name in the ``fqdn`` attribute.

    Examples:

    >>> hostname.fqdn
    'www.example.com'
    >>> hostname.hostname
    'www'
    >>> hostname.domain
    'example.com'

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
