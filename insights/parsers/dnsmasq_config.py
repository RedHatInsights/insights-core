"""
DnsmasqConf - files ``/etc/dnsmasq.conf`` and ``/etc/dnsmasq.d/*.conf``
=======================================================================
"""

from insights.core.plugins import parser
from insights.core import ConfigParser
from insights.specs import Specs
from insights.configtree import (
    DocParser,
    LineGetter,
    parse_name_attrs,
    Node,
)


class DnsmasqConfDocParser(DocParser):
    def parse_statement(self, lg):
        line = lg.peek()
        pos = lg.pos
        if "=" in line:
            name, attrs = parse_name_attrs(line, sep="=")
        else:
            name, attrs = line, None

        ret = Node(name=name, attrs=attrs, ctx=self.ctx)
        next(lg)
        ret.pos = pos
        return ret


def parse_doc(f, ctx=None):
    return DnsmasqConfDocParser(ctx).parse_doc(LineGetter(f))


@parser(Specs.dnsmasq_config)
class DnsmasqConf(ConfigParser):
    """
    Class to parses the content of dnsmasq configuration files ``/etc/dnsmasq.conf`` and ``/etc/dnsmasq.d/*.conf``

    Sample configuration output::

        # Listen on this specific port instead of the standard DNS port
        # (53). Setting this to zero completely disables DNS function,
        # leaving only DHCP and/or TFTP.
        port=5353

        no-resolv
        domain-needed
        no-negcache
        max-cache-ttl=1
        enable-dbus
        dns-forward-max=5000
        cache-size=5000
        bind-dynamic
        except-interface=lo
        server=/in-addr.arpa/127.0.0.1
        server=/cluster.local/127.0.0.1
        # End of config

    Examples::
        >>> "no-resolv" in conf
        True
        >>> conf["server"]
        server=/in-addr.arpa/127.0.0.1
        server=/cluster.local/127.0.0.1
        >>> conf["dns-forward-max"][-1].value
        5000

    """

    def parse_doc(self, content):
        return parse_doc(content, ctx=self)
