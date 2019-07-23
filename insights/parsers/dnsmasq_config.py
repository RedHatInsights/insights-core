"""
DnsmasqConf - files ``/etc/dnsmasq.conf`` and ``/etc/dnsmasq.d/*.conf``
=======================================================================
"""

import string

from insights.core.plugins import parser
from insights.core import ConfigParser
from insights.specs import Specs

from insights.parsr import (Char, EOF, Forward, Lift, LineEnd, Many, Number,
        OneLineComment, Opt, PosMarker, skip_none, String, WS, WSChar)
from insights.parsr.query import Directive, Entry


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
        return parse_doc("\n".join(content), ctx=self)


def parse_doc(f, ctx=None, line_end="\n"):
    def to_entry(name, rest):
        rest = [] if not rest else [rest]
        return Directive(name=name.value, attrs=rest, lineno=name.lineno, src=ctx)

    Sep = Char("=")
    Stmt = Forward()
    Num = Number & (WSChar | LineEnd)
    Comment = (WS >> OneLineComment("#").map(lambda x: None))
    Bare = String(set(string.printable) - (set("#\n\r")))
    Name = WS >> PosMarker(String(string.ascii_letters + "_-" + string.digits)) << WS
    Value = WS >> (Num | Bare) << WS
    Stanza = (Lift(to_entry) * Name * (Opt(Sep >> Value))) | Comment
    Stmt <= WS >> Stanza << WS
    Doc = Many(Stmt).map(skip_none)
    Top = Doc + EOF

    return Entry(children=Top(f)[0], src=ctx)
