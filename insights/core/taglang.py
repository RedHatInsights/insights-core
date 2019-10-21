"""
Simple language for defining predicates against a list or set of strings.

Operator Precedence:
    - ``!`` high - opposite truth value of its predicate
    - ``/`` high - starts a regex that continues until whitespace unless quoted
    - ``&`` medium - "and" of two predicates
    - ``|`` low - "or" of two predicates
    - ``,`` low - "or" of two predicates. Synonym for ``|``.

It supports grouping with parentheses and quoted strings/regexes surrounded
with either single or double quotes.

Examples:
    >>> pred = parse("a | b & !c")  # means (a or (b and (not c)))
    >>> pred(["a"])
    True
    >>> pred(["b"])
    True
    >>> pred(["b", "c"])
    False
    >>> pred = parse("/net | apache")
    >>> pred(["networking"])
    True
    >>> pred(["mynetwork"])
    True
    >>> pred(["apache"])
    True
    >>> pred(["security"])
    False
    >>> pred = parse("(a | b) & c")
    >>> pred(["a", "c"])
    True
    >>> pred(["b", "c"])
    True
    >>> pred(["a"])
    False
    >>> pred(["b"])
    False
    >>> pred(["c"])
    False

Regular expressions start with a forward slash ``/`` and continue until
whitespace unless they are quoted with either single or double quotes. This
means that they can consume what would normally be considered an operator or a
closing parenthesis if you aren't careful.

For example, this is a parse error because the regex consumes the comma:
    >>> pred = parse("/net, apache")
    Exception

Instead, do this:
    >>> pred = parse("/net , apache")

or this:
    >>> pred = parse("/net | apache")

or this:
    >>> pred = parse("'/net', apache")
"""
import re
import string
from insights.parsr import (Char, EOF, Forward, InSet, Many, Opt, String,
                            QuotedString, WS)


class Predicate(object):
    """
    Provides __call__ for invoking the Predicate like a function without having
    to explictly call its test method.
    """

    def __call__(self, value):
        return self.test(value)


class Eq(Predicate):
    """ The value must be in the set of values. """

    def __init__(self, value):
        self.value = value

    def test(self, values):
        return self.value in values


class Regex(Predicate):
    """ The regex must match at least one of the values. """

    def __init__(self, value):
        self.regex = re.compile(value)

    def test(self, values):
        return any(self.regex.search(v) for v in values)


class Not(Predicate):
    """ The values must not satisfy the wrapped condition. """

    def __init__(self, pred):
        self.pred = pred

    def test(self, value):
        return not self.pred.test(value)


class And(Predicate):
    """ The values must satisfy both the left and the right condition. """

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def test(self, value):
        return self.left.test(value) and self.right.test(value)


class Or(Predicate):
    """ The values must satisfy either the left or the right condition. """

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def test(self, value):
        return self.left.test(value) or self.right.test(value)


def negate(args):
    op, p = args
    return Not(p) if op else p


def oper(args):
    left, rest = args
    for op, right in rest:
        if op == "&":
            left = And(left, right)
        if op in ",|":
            left = Or(left, right)
    return left


expr = Forward()

bare = String(set(string.printable) - (set(string.whitespace) | set(")&,|")))

tag = (QuotedString | bare).map(Eq)

regex_body = QuotedString | String(set(string.printable) - set(string.whitespace))
regex = Char("/") >> regex_body.map(Regex)

factor_body = ((Char("(") >> expr << Char(")")) | regex | tag)
factor = (WS >> Opt(Char("!")) + factor_body << WS).map(negate)

term = (factor + Many(Char("&") + factor)).map(oper)
expr <= (term + Many(InSet(",|") + term)).map(oper)

parse = expr << EOF
