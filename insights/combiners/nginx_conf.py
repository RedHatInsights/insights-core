#!/usr/bin/env python
"""
NginxConfTree - Combiner for nginx configuration
=======================================================
This module models nginx configuration as a tree. It correctly handles include
directives by splicing individual document trees into their parents until one
document tree is left.

A DSL is provided to query the tree through a select function or brackets [].
The brackets allow a more conventional lookup feel but aren't quite as powerful
as using select directly.
"""
import os
import string
from insights import combiner, parser, run
from insights.core import ConfigCombiner, ConfigParser
from insights.parsr.query import eq
from insights.parsr import (Char, EOF, Forward, LeftCurly, Lift, LineEnd,
        RightCurly, Many, Number, OneLineComment, Parser, PosMarker, SemiColon,
        QuotedString, skip_none, String, WS, WSChar)
from insights.parsr.query import Directive, Entry, Section
from insights.specs import Specs


class EmptyQuotedString(Parser):
    def __init__(self, chars):
        super(EmptyQuotedString, self).__init__()
        single = Char("'") >> String(set(chars) - set("'"), "'", 0) << Char("'")
        double = Char('"') >> String(set(chars) - set('"'), '"', 0) << Char('"')
        self.add_child(single | double)

    def process(self, pos, data, ctx):
        return self.children[0].process(pos, data, ctx)


@parser(Specs.nginx_conf, continue_on_error=False)
class _NginxConf(ConfigParser):
    def __init__(self, *args, **kwargs):
        def to_entry(name, attrs, body):
            if body == ";":
                return Directive(name=name.value, attrs=attrs, lineno=name.lineno, src=self)
            return Section(name=name.value, attrs=attrs, children=body, lineno=name.lineno, src=self)

        name_chars = string.ascii_letters + "_/"
        Stmt = Forward()
        Num = Number & (WSChar | LineEnd | SemiColon)
        Comment = OneLineComment("#").map(lambda x: None)
        BeginBlock = WS >> LeftCurly << WS
        EndBlock = WS >> RightCurly << WS
        Bare = String(set(string.printable) - (set(string.whitespace) | set("#;{}'\"")))
        Name = WS >> PosMarker(String(name_chars) | EmptyQuotedString(name_chars)) << WS
        Attr = WS >> (Num | Bare | QuotedString) << WS
        Attrs = Many(Attr)
        Block = BeginBlock >> Many(Stmt).map(skip_none) << EndBlock
        Stanza = (Lift(to_entry) * Name * Attrs * (Block | SemiColon)) | Comment
        Stmt <= WS >> Stanza << WS
        Doc = Many(Stmt).map(skip_none)
        self.Top = Doc + EOF
        super(_NginxConf, self).__init__(*args, **kwargs)

    def parse_doc(self, content):
        return Entry(children=self.Top("\n".join(content))[0], src=self)


@combiner(_NginxConf)
class NginxConfTree(ConfigCombiner):
    """
    Exposes nginx configuration through the parsr query interface.

    See the :py:class:`insights.core.ConfigComponent` class for example usage.
    """
    def __init__(self, confs):
        super(NginxConfTree, self).__init__(confs, "nginx.conf", eq("include"))

    @property
    def conf_path(self):
        return os.path.dirname(self.main.file_path)


def get_tree(root=None):
    """
    This is a helper function to get an nginx configuration component for your
    local machine or an archive. It's for use in interactive sessions.
    """
    return run(NginxConfTree, root=root).get(NginxConfTree)


if __name__ == "__main__":
    run(NginxConfTree, print_summary=True)
