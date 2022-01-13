import string

from insights.parsr import (EOF, HangingString, InSet, LeftBracket, Lift,
        LineEnd, Literal, Many, OneLineComment, Opt, PosMarker, RightBracket,
        skip_none, String, WithIndent, WS, WSChar)
from insights.parsr.query import Directive, Entry, eq, Section


class Error(Exception):
    """Base class for iniparser exceptions."""
    def __init__(self, msg=''):
        self.message = msg
        Exception.__init__(self, msg)

    def __repr__(self):
        return self.message

    __str__ = __repr__


class NoOptionError(Error):
    """A requested option was not found."""
    def __init__(self, section, option):
        Error.__init__(self, "No option {0!r} in section: {1!r}".format(option, section))
        self.option = option
        self.section = section
        self.args = (option, section)


class NoSectionError(Error):
    """Raised when no section matches a requested option."""
    def __init__(self, section):
        Error.__init__(self, 'No section: {0!r}'.format(section))
        self.section = section
        self.args = section


def parse_doc(content, ctx, return_defaults=False, return_booleans=True):
    def to_directive(x):
        name, rest = x
        rest = [rest] if rest is not None else []
        return Directive(name=name.value.strip(), attrs=rest, lineno=name.lineno, src=ctx)

    def to_section(name, rest):
        return Section(name=name.value.strip(), children=rest, lineno=name.lineno, src=ctx)

    def apply_defaults(cfg, include_defaults):
        if "DEFAULT" not in cfg:
            return cfg

        defaults = cfg["DEFAULT"]
        not_defaults = cfg[~eq("DEFAULT")]
        for c in not_defaults:
            for d in defaults.grandchildren:
                if d.name not in c:
                    c.children.append(d)

        if not include_defaults:
            cfg.children = list(not_defaults)
        return cfg

    header_chars = (set(string.printable) - set(string.whitespace) - set("[]")) | set(" ")
    sep_chars = set("=:")
    key_chars = header_chars - sep_chars
    value_chars = set(string.printable) - set("\n\r")

    Yes = Literal("yes", True, ignore_case=True)
    No = Literal("no", False, ignore_case=True)
    Tru = Literal("true", True, ignore_case=True)
    Fals = Literal("false", False, ignore_case=True)
    if return_booleans:
        Boolean = ((Yes | No | Tru | Fals) & (WSChar | LineEnd)) % "Boolean"

    LeftEnd = (WS + LeftBracket + WS)
    RightEnd = (WS + RightBracket + WS)
    Header = (LeftEnd >> PosMarker(String(header_chars)) << RightEnd) % "Header"
    Key = WS >> PosMarker(String(key_chars)) << WS
    Sep = InSet(sep_chars, "Sep")

    if return_booleans:
        Value = WS >> (Boolean | HangingString(value_chars))
    else:
        Value = WS >> (HangingString(value_chars))

    KVPair = WithIndent(Key + Opt(Sep >> Value)) % "KVPair"
    Comment = (WS >> (OneLineComment("#") | OneLineComment(";")).map(lambda x: None))

    Line = Comment | KVPair.map(to_directive)
    Sect = Lift(to_section) * Header * Many(Line).map(skip_none)
    Doc = Many(Comment | Sect).map(skip_none)
    Top = Doc << WS << EOF

    res = Entry(children=Top(content), src=ctx)
    return apply_defaults(res, return_defaults)
