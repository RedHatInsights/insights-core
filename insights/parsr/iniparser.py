"""
iniparser parses ini files into a python dictionary of dictionaries. Duplicate
keys in a section convert the value to a list. Numbers are automatically
converted to python ints or floats. Line continuations based on hanging indents
are supported. Sections inherit keys from the `[DEFAULT]` section. All keys are
converted to lower case. Variable interpolation is not supported.
"""
import string
from insights.parsr import (EOF, HangingString, InSet, LeftBracket, LineEnd,
        Many, Number, OneLineComment, Opt, RightBracket, String, WithIndent,
        WS, WSChar)


def loads(s):
    res = Top(s)[0]
    default = res.get("default")
    if default:
        default_keys = set(default)
        for header, items in res.items():
            if header != "default":
                missing = default_keys - set(items)
                for m in missing:
                    items[m] = default[m]

    return res


def load(f):
    return loads(f.read())


def to_dict(x):
    x = [i for i in x if i is not None]
    d = {}
    for k, v in x:
        k = k.lower()
        if k in d:
            if not isinstance(d[k], list):
                d[k] = [d[k]]
            d[k].append(v)
        else:
            d[k] = v
    return d


header_chars = (set(string.printable) - set(string.whitespace) - set("[]"))
sep_chars = set("=:")
key_chars = header_chars - sep_chars
value_chars = set(string.printable) - set("\n\r")

Num = Number & (WSChar | LineEnd)
LeftEnd = (WS + LeftBracket + WS)
RightEnd = (WS + RightBracket + WS)
Header = LeftEnd >> String(header_chars) << RightEnd
Key = WS >> String(key_chars) << WS
Sep = InSet(sep_chars)
Value = WS >> (Num | HangingString(value_chars))
KVPair = WithIndent(Key + Opt(Sep + Value, default=[None, None])).map(lambda a: (a[0], a[1][1]))
Comment = (WS >> (OneLineComment("#") | OneLineComment(";")).map(lambda x: None))
Line = Comment | KVPair
Section = Header + (Many(Line).map(to_dict))
Doc = Many(Comment | Section).map(to_dict)
Top = Doc + EOF
