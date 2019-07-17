import string
from insights.parsr import (EOF, Forward, LeftCurly, Lift, LineEnd, RightCurly,
        Many, Number, OneLineComment, PosMarker, SemiColon, QuotedString,
        skip_none, String, WS, WSChar)
from insights.parsr.query import Entry


def loads(data):
    return Top(data)[0]


def load(f):
    return loads(f.read())


def to_entry(name, attrs, body):
    if body == ";":
        return Entry(name=name.value, attrs=attrs, lineno=name.lineno)
    return Entry(name=name.value, attrs=attrs, children=body, lineno=name.lineno)


Stmt = Forward()
Num = Number & (WSChar | LineEnd)
Comment = OneLineComment("#").map(lambda x: None)
BeginBlock = WS >> LeftCurly << WS
EndBlock = WS >> RightCurly << WS
Bare = String(set(string.printable) - (set(string.whitespace) | set("#;{}'\"")))
Name = WS >> PosMarker(String(string.ascii_letters + "_")) << WS
Attr = WS >> (Num | Bare | QuotedString) << WS
Attrs = Many(Attr)
Block = BeginBlock >> Many(Stmt).map(skip_none) << EndBlock
Stanza = (Lift(to_entry) * Name * Attrs * (Block | SemiColon)) | Comment
Stmt <= WS >> Stanza << WS
Doc = Many(Stmt).map(skip_none)
Top = Doc + EOF
