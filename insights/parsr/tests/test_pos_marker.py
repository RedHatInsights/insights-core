import operator
import string
from functools import reduce
from insights.parsr import (
    EOF,
    EOL,
    InSet,
    LineEnd,
    Many,
    Number,
    OneLineComment,
    Opt,
    PosMarker,
    skip_none,
    String,
    WS,
    WSChar,
)
from insights.parsr.query import Entry

DATA = """
# this is a config file
a = 15
b = a string
valueless
d = 1.14

# another section
+valueless  # no value
e = hello   # a value
#
"""


def to_entry(ms):
    children = []
    for mark, value in ms:
        children.append(Entry(name=mark.value, attrs=[value], lineno=mark.lineno))
    return Entry(children=children)


class KVPairs:
    def __init__(self, sep_chars="=:", comment_chars="#;"):
        eol_chars = set("\n\r")
        sep_chars = set(sep_chars)
        comment_chars = set(comment_chars)
        key_chars = set(string.printable) - (sep_chars | eol_chars | comment_chars)
        value_chars = set(string.printable) - (eol_chars | comment_chars)

        OLC = reduce(operator.__or__, [OneLineComment(c) for c in comment_chars])
        Comment = (WS >> OLC).map(lambda x: None)
        Num = Number & (WSChar | LineEnd)
        Key = WS >> PosMarker(String(key_chars).map(str.strip)) << WS
        Sep = InSet(sep_chars)
        Value = WS >> (Num | String(value_chars).map(str.strip))
        KVPair = (Key + Opt(Sep + Value, default=[None, None])).map(
            lambda a: (a[0], a[1][1])
        )
        Line = Comment | KVPair | EOL.map(lambda x: None)
        Doc = Many(Line).map(skip_none).map(to_entry)
        self.Top = Doc + EOF

    def loads(self, s):
        return self.Top(s)[0]

    def load(self, f):
        return self.loads(f.read())


def test_marker():
    kvp = KVPairs()
    res = kvp.loads(DATA)
    assert res
    assert res["+valueless"][0].lineno == 9
