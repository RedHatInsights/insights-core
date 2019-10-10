"""
Hostname - command ``hostname``
===============================

Parsers contained in this module are:

Hostname - command ``hostname -f``
----------------------------------

HostnameDefault - command ``hostname``
--------------------------------------

HostnameShort - command ``hostname -s``
---------------------------------------
"""

from insights.parsers import ParseException
from insights import parser, CommandParser
from insights.specs import Specs


class HostnameBase(CommandParser):
    """
    The base parser class for command ``hostname``.

    Raises:
        ParseException: When the output contains multiple non-empty lines.
    """
    def parse_content(self, content):
        content = list(filter(None, content))
        if len(content) != 1:
            msg = "hostname data contains multiple non-empty lines"
            raise ParseException(msg)
        self.raw = content[0].strip()
        self.hostname = self.raw.split(".")[0] if self.raw else None


@parser(Specs.hostname)
class Hostname(HostnameBase):
    """
    This parser simply reads the output of ``hostname -f``, which is the
    configured fully qualified domain name of the client system.  It then
    splits it into ``hostname`` and ``domain`` and stores these as attributes,
    along with the unmodified name in the ``fqdn`` attribute.

    Examples:
        >>> hostname.raw
        'rhel7.example.com'
        >>> hostname.fqdn
        'rhel7.example.com'
        >>> hostname.hostname
        'rhel7'
        >>> hostname.domain
        'example.com'

    Attributes:
        raw: The raw output of the ``hostname -f`` command.
        fqdn: The fully qualified domain name of the host. The same to
            ``hostname`` when domain part is not set.
        hostname: The hostname.
        domain: The domain get from the ``fqdn``.
    """
    def parse_content(self, content):
        super(Hostname, self).parse_content(content)
        self.fqdn = self.raw
        self.domain = ".".join(self.raw.split(".")[1:]) if self.raw else None

    def __repr__(self):
        return "<raw: {r}, hostname: {h}, domain: {d}>".format(r=self.raw, h=self.hostname, d=self.domain)


@parser(Specs.hostname_default)
class HostnameDefault(HostnameBase):
    """
    This parser simply reads the output of ``hostname``.

    Examples:
        >>> hostname_def.raw
        'rhel7'
        >>> hostname_def.hostname
        'rhel7'

    Attributes:
        raw: The raw output of the ``hostname`` command.
        hostname: The hostname.
    """
    def __repr__(self):
        return "<raw: {r}, hostname: {h}>".format(r=self.raw, h=self.hostname)


@parser(Specs.hostname_short)
class HostnameShort(HostnameBase):
    """
    This parser simply reads the output of ``hostname -s``, which is the
    configured short hostname of the client system.

    Examples:
        >>> hostname_s.raw
        'rhel7'
        >>> hostname_s.hostname
        'rhel7'

    Attributes:
        raw: The raw output of the ``hostname -s`` command.
        hostname: The hostname.
    """
    def __repr__(self):
        return "<raw: {r}, hostname: {h}>".format(r=self.raw, h=self.hostname)
