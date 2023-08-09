"""
Parsers for the Corosync Cluster Engine configurations
======================================================


Parsers included in this module are:

CorosyncConf - file ``/etc/corosync/corosync.conf``
---------------------------------------------------
"""
import string
from insights.core import ConfigParser
from insights.specs import Specs
from insights import parser

from insights.parsr import (EOF, Forward, InSet, LeftCurly, Lift, LineEnd,
        Literal, RightCurly, Many, Number, OneLineComment, PosMarker,
        skip_none, String, QuotedString, WS, WSChar)
from insights.parsr.query import Directive, Entry, Section


def parse_doc(f, ctx=None, line_end="\n"):
    def to_entry(name, rest):
        if isinstance(rest, list):
            return Section(name=name.value, children=rest, lineno=name.lineno, src=ctx)
        return Directive(name=name.value, attrs=[rest], lineno=name.lineno, src=ctx)

    Sep = InSet(":=")
    Stmt = Forward()
    Num = Number & (WSChar | LineEnd)
    NULL = Literal("none", value=None)
    Comment = (WS >> OneLineComment("#").map(lambda x: None))
    BeginBlock = (WS >> LeftCurly << WS)
    EndBlock = (WS >> RightCurly << WS)
    Bare = String(set(string.printable) - (set(string.whitespace) | set("#{}'\"")))
    Name = WS >> PosMarker(String(string.ascii_letters + "_" + string.digits)) << WS
    Value = WS >> (Num | NULL | QuotedString | Bare) << WS
    Block = BeginBlock >> Many(Stmt).map(skip_none) << EndBlock
    Stanza = (Lift(to_entry) * Name * (Block | (Sep >> Value))) | Comment
    Stmt <= WS >> Stanza << WS
    Doc = Many(Stmt).map(skip_none)
    Top = Doc + EOF

    return Entry(children=Top(f)[0], src=ctx)


@parser(Specs.corosync_conf)
class CorosyncConf(ConfigParser):
    """Parse the output of the file ``/etc/corosync/corosync.conf`` using
    the ``ConfigParser`` base class. It exposes the corosync
    configuration through the parsr query interface.

    The parameters in the directives are referred from the manpage of
    ``corosync.conf``. See ``man 8 corosync.conf`` for more info.

    Sample content of the file ``/etc/corosync/corosync.conf`` ::

        totem {
            version: 2
            secauth: off
            cluster_name: tripleo_cluster
            transport: udpu
            token: 10000
        }

        nodelist {
            node {
                ring0_addr: overcloud-controller-0
                nodeid: 1
            }

            node {
                ring0_addr: overcloud-controller-1
                nodeid: 2
            }

            node {
                ring0_addr: overcloud-controller-2
                nodeid: 3
            }
        }

        quorum {
            provider: corosync_votequorum
        }

        logging {
            to_logfile: yes
            logfile: /var/log/cluster/corosync.log
            to_syslog: yes
        }


    Example:

        >>> from insights.parsr.query import first, last
        >>> corosync_conf['quorum']['provider'][first].value
        'corosync_votequorum'
        >>> corosync_conf['totem']['token'][first].value
        10000
        >>> corosync_conf['nodelist']['node']['nodeid'][last].value
        3

    """
    def parse_doc(self, content):
        return parse_doc("\n".join(content), ctx=self)
