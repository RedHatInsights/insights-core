"""
multipath_conf parses multipath.conf configuration files into nested
dictionaries.
"""
import string
from insights.parsr import (EOF, Forward, LeftCurly, Lift, Literal, LineEnd,
        RightCurly, Many, Number, OneLineComment, PosMarker, skip_none, String,
        QuotedString, WS, WSChar)
from insights.parsr.query import Entry


def loads(data):
    return Entry(children=Top(data)[0])


def load(f):
    return loads(f.read())


def to_entry(name, rest):
    if isinstance(rest, list):
        return Entry(name=name.value, children=rest, lineno=name.lineno)
    return Entry(name=name.value, attrs=[rest], lineno=name.lineno)


Stmt = Forward()
Num = Number & (WSChar | LineEnd)
NULL = Literal("none", value=None)
Comment = (WS >> OneLineComment("#").map(lambda x: None))
BeginBlock = (WS >> LeftCurly << WS)
EndBlock = (WS >> RightCurly << WS)
Bare = String(set(string.printable) - (set(string.whitespace) | set("#{}'\"")))
Name = WS >> PosMarker(String(string.ascii_letters + "_")) << WS
Value = WS >> (Num | NULL | QuotedString | Bare) << WS
Block = BeginBlock >> Many(Stmt).map(skip_none) << EndBlock
Stanza = (Lift(to_entry) * Name * (Block | Value)) | Comment
Stmt <= WS >> Stanza << WS
Doc = Many(Stmt).map(skip_none)
Top = Doc + EOF
