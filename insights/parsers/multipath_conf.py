"""
multipath.conf file content
===========================

MultipathConfTree - file ``/etc/multipath.conf``
------------------------------------------------

MultipathConfTreeInitramfs - command ``lsinitrd -f /etc/multipath.conf``
------------------------------------------------------------------------
"""
import string

from insights.core import ConfigParser, CommandParser
from insights.core.plugins import parser
from insights.parsr import (EOF, Forward, LeftCurly, Lift, LineEnd, Literal,
                            Many, Number, OneLineComment, PosMarker, QuotedString,
                            RightCurly, String, WS, WSChar, skip_none)
from insights.parsr.query import Entry
from insights.specs import Specs


def parse_doc(content, ctx):
    def to_entry(name, rest):
        if isinstance(rest, list):
            return Entry(name=name.value, children=rest, lineno=name.lineno, src=ctx)
        return Entry(name=name.value, attrs=[rest], lineno=name.lineno, src=ctx)

    Stmt = Forward()
    Num = Number & (WSChar | LineEnd)
    NULL = Literal("none", value=None)
    Comment = (WS >> OneLineComment("#").map(lambda x: None))
    BeginBlock = (WS >> LeftCurly << WS)
    EndBlock = (WS >> RightCurly << WS)
    Bare = String(set(string.printable) - (set(string.whitespace) | set("#{}'\"")))
    Name = WS >> PosMarker(String(string.ascii_letters + "_")) << WS
    Value = WS >> (Num | NULL | QuotedString | Bare) << WS
    EmptyString = String('"\'', min_length=2)
    Value = WS >> (Num | NULL | QuotedString | EmptyString | Bare) << WS
    Block = BeginBlock >> Many(Stmt).map(skip_none) << EndBlock
    Stanza = (Lift(to_entry) * Name * (Block | Value)) | Comment
    Stmt <= WS >> Stanza << WS
    Doc = Many(Stmt).map(skip_none)
    Top = Doc + EOF

    return Entry(children=Top(content)[0])


@parser(Specs.multipath_conf)
class MultipathConfTree(ConfigParser):
    """
    Exposes multipath configuration through the parsr query interface.

    See the :py:class:`insights.core.ConfigComponent` class for example usage.
    """
    def parse_doc(self, content):
        return parse_doc("\n".join(content), ctx=self)


def get_tree(root=None):
    """
    This is a helper function to get a multipath configuration component for
    your local machine or an archive. It's for use in interactive sessions.
    """
    from insights import run
    return run(MultipathConfTree, root=root).get(MultipathConfTree)


@parser(Specs.multipath_conf_initramfs)
class MultipathConfTreeInitramfs(ConfigParser, CommandParser):
    """
    Exposes the multipath configuration from initramfs image through the
    parsr query interface.

    See the :py:class:`insights.core.ConfigComponent` class for example usage.
    """

    bad_lines = [
        'no <initramfs file> specified and the default image'
    ]

    def __init__(self, context):
        super(MultipathConfTreeInitramfs, self).__init__(
                context, extra_bad_lines=self.bad_lines)

    def parse_doc(self, content):
        return parse_doc("\n".join(content), ctx=self)


def get_tree_from_initramfs(root=None):
    """
    This is a helper function to get a multipath configuration(from initramfs
    image) component for your local machine or an archive. It's for use in
    interactive sessions.
    """
    from insights import run
    return run(MultipathConfTreeInitramfs, root=root).get(MultipathConfTreeInitramfs)
