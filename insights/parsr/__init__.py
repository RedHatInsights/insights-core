from __future__ import print_function
import functools
import string
from bisect import bisect_left
from io import StringIO


class Node(object):
    def __init__(self):
        self.children = []

    def add_child(self, child):
        self.children.append(child)
        return self

    def set_children(self, children):
        self.children = []
        for c in children:
            self.add_child(c)
        return self

    def __repr__(self):
        return self.__class__.__name__


def text_format(tree):
    out = StringIO()
    tab = " " * 2
    seen = set()

    def inner(cur, prefix):
        print(prefix + str(cur), file=out)
        if cur in seen:
            return

        seen.add(cur)

        next_prefix = prefix + tab
        for c in cur.children:
            inner(c, next_prefix)

    inner(tree, "")
    out.seek(0)
    return out.read()


def render(tree):
    print(text_format(tree))


def debug_hook(func):
    @functools.wraps(func)
    def inner(self, pos, data, ctx):
        if self._debug:
            line = ctx.line(pos) + 1
            col = ctx.col(pos) + 1
            print("Trying {} at line {} col {}".format(self, line, col))
            try:
                res = func(self, pos, data, ctx)
                print("Result: {}".format(res[1]))
                return res
            except:
                print("Failed")
                raise
        return func(self, pos, data, ctx)
    return inner


class Ctx(object):
    def __init__(self, lines, src=None):
        self.error_pos = -1
        self.error_msg = None
        self.indents = []
        self.tags = []
        self.src = src
        self.lines = [i for i, x in enumerate(lines) if x == "\n"]

    def set(self, pos, msg):
        if pos >= self.error_pos:
            self.error_pos = pos
            self.error_msg = msg

    def line(self, pos):
        return bisect_left(self.lines, pos)

    def col(self, pos):
        p = self.line(pos)
        if p == 0:
            return pos
        return (pos - self.lines[p - 1] - 1)


class Parser(Node):
    def __init__(self):
        super(Parser, self).__init__()
        self.name = None
        self._debug = False

    def debug(self, d=True):
        self._debug = d
        return self

    def map(self, func):
        return Map(self, func)

    @staticmethod
    def accumulate(first, rest):
        results = [first] if first else []
        if rest:
            results.extend(rest)
        return results

    def sep_by(self, sep):
        return Lift(self.accumulate) * Opt(self) * Many(sep >> self)

    def until(self, pred):
        return Until(self, pred)

    def __or__(self, other):
        return Choice([self, other])

    def __and__(self, other):
        return FollowedBy(self, other)

    def __truediv__(self, other):
        return NotFollowedBy(self, other)

    def __add__(self, other):
        return Seq([self, other])

    def __lshift__(self, other):
        return KeepLeft(self, other)

    def __rshift__(self, other):
        return KeepRight(self, other)

    def __mod__(self, name):
        self.name = name
        return self

    def process(self, pos, data, ctx):
        raise NotImplementedError()

    def __call__(self, data, src=None):
        data = list(data)
        data.append(None)  # add a terminal so we don't overrun
        ctx = Ctx(data, src=src)
        ex = None
        try:
            _, ret = self.process(0, data, ctx)
            return ret
        except Exception:
            lineno = ctx.line(ctx.error_pos) + 1
            colno = ctx.col(ctx.error_pos) + 1
            msg = "At line {} column {}: {}"
            ex = Exception(msg.format(lineno, colno, ctx.error_msg))
        if ex:
            raise ex

    def __repr__(self):
        return self.name or self.__class__.__name__


class Wrapper(Parser):
    def __init__(self, parser):
        super(Wrapper, self).__init__()
        self.add_child(parser)

    @debug_hook
    def process(self, pos, data, ctx):
        return self.children[0].process(pos, data, ctx)


class Mark(object):
    def __init__(self, lineno, col, value):
        self.lineno = lineno
        self.col = col
        self.value = value


class PosMarker(Wrapper):
    """
    Save the line number and column of a non-terminal or terminal by
    wrapping it in a PosMarker. The value of the parser that handled the input
    as well as the initial input position will be returned as a Mark instance.
    """
    @debug_hook
    def process(self, pos, data, ctx):
        lineno = ctx.line(pos) + 1
        col = ctx.col(pos) + 1
        pos, result = super(PosMarker, self).process(pos, data, ctx)
        return pos, Mark(lineno, col, result)


class Seq(Parser):
    def __init__(self, children):
        super(Seq, self).__init__()
        self.set_children(children)

    def __add__(self, other):
        return self.add_child(other)

    @debug_hook
    def process(self, pos, data, ctx):
        results = []
        for p in self.children:
            pos, res = p.process(pos, data, ctx)
            results.append(res)
        return pos, results


class Choice(Parser):
    def __init__(self, children):
        super(Choice, self).__init__()
        self.set_children(children)

    def __or__(self, other):
        return self.add_child(other)

    @debug_hook
    def process(self, pos, data, ctx):
        ex = None
        for c in self.children:
            try:
                return c.process(pos, data, ctx)
            except Exception as e:
                ex = e
        raise ex


class Many(Wrapper):
    @debug_hook
    def process(self, pos, data, ctx):
        results = []
        p = self.children[0]
        while True:
            try:
                pos, res = p.process(pos, data, ctx)
                results.append(res)
            except Exception:
                break
        return pos, results


class Many1(Many):
    @debug_hook
    def process(self, pos, data, ctx):
        pos, results = super(Many1, self).process(pos, data, ctx)
        if len(results) == 0:
            child = self.children[0]
            raise Exception("Expected at least one {}.".format(child))
        return pos, results


class Until(Parser):
    def __init__(self, parser, predicate):
        super(Until, self).__init__()
        self.set_children([parser, predicate])

    @debug_hook
    def process(self, pos, data, ctx):
        parser, pred = self.children
        results = []
        while True:
            try:
                pred.process(pos, data, ctx)
            except Exception:
                try:
                    pos, res = parser.process(pos, data, ctx)
                    results.append(res)
                except Exception:
                    break
            else:
                break
        return pos, results


class FollowedBy(Parser):
    def __init__(self, p, f):
        super(FollowedBy, self).__init__()
        self.set_children([p, f])

    @debug_hook
    def process(self, pos, data, ctx):
        left, right = self.children
        new, res = left.process(pos, data, ctx)
        try:
            right.process(new, data, ctx)
        except Exception:
            raise
        else:
            return new, res


class NotFollowedBy(Parser):
    def __init__(self, p, f):
        super(NotFollowedBy, self).__init__()
        self.set_children([p, f])

    @debug_hook
    def process(self, pos, data, ctx):
        left, right = self.children
        new, res = left.process(pos, data, ctx)
        try:
            right.process(new, data, ctx)
        except Exception:
            return new, res
        else:
            raise Exception("{} can't follow {}".format(right, left))


class KeepLeft(Parser):
    def __init__(self, left, right):
        super(KeepLeft, self).__init__()
        self.set_children([left, right])

    @debug_hook
    def process(self, pos, data, ctx):
        left, right = self.children
        pos, res = left.process(pos, data, ctx)
        pos, _ = right.process(pos, data, ctx)
        return pos, res


class KeepRight(Parser):
    def __init__(self, left, right):
        super(KeepRight, self).__init__()
        self.set_children([left, right])

    @debug_hook
    def process(self, pos, data, ctx):
        left, right = self.children
        pos, _ = left.process(pos, data, ctx)
        pos, res = right.process(pos, data, ctx)
        return pos, res


class Opt(Parser):
    def __init__(self, p, default=None):
        super(Opt, self).__init__()
        self.add_child(p)
        self.default = default

    @debug_hook
    def process(self, pos, data, ctx):
        try:
            return self.children[0].process(pos, data, ctx)
        except Exception:
            return pos, self.default


class Map(Parser):
    def __init__(self, p, func):
        super(Map, self).__init__()
        self.add_child(p)
        self.func = func

    @debug_hook
    def process(self, pos, data, ctx):
        pos, res = self.children[0].process(pos, data, ctx)
        return pos, self.func(res)

    def __repr__(self):
        return "Map({})".format(self.func)


class Lift(Parser):
    def __init__(self, func):
        super(Lift, self).__init__()
        self.func = func

    def __mul__(self, other):
        return self.add_child(other)

    @debug_hook
    def process(self, pos, data, ctx):
        results = []
        for c in self.children:
            pos, res = c.process(pos, data, ctx)
            results.append(res)
        try:
            return pos, self.func(*results)
        except Exception as e:
            ctx.set(pos, str(e))
            raise


class Forward(Parser):
    def __init__(self):
        super(Forward, self).__init__()
        self.delegate = None

    def __le__(self, delegate):
        self.set_children([delegate])

    @debug_hook
    def process(self, pos, data, ctx):
        return self.children[0].process(pos, data, ctx)


class EOF(Parser):
    @debug_hook
    def process(self, pos, data, ctx):
        if data[pos] is None:
            return pos, None
        msg = "Expected end of input."
        ctx.set(pos, msg)
        raise Exception(msg)


class Char(Parser):
    def __init__(self, char):
        super(Char, self).__init__()
        self.char = char

    @debug_hook
    def process(self, pos, data, ctx):
        if data[pos] == self.char:
            return (pos + 1, self.char)
        msg = "Expected {}.".format(self.char)
        ctx.set(pos, msg)
        raise Exception(msg)

    def __repr__(self):
        return "Char('{}')".format(self.char)


class InSet(Parser):
    def __init__(self, s, name=None):
        super(InSet, self).__init__()
        self.values = set(s)
        self.name = name

    @debug_hook
    def process(self, pos, data, ctx):
        c = data[pos]
        if c in self.values:
            return (pos + 1, c)
        msg = "Expected {}.".format(self)
        ctx.set(pos, msg)
        raise Exception(msg)


class Literal(Parser):
    _NULL = object()

    def __init__(self, chars, value=_NULL, ignore_case=False):
        super(Literal, self).__init__()
        self.chars = chars if not ignore_case else chars.lower()
        self.value = value
        self.ignore_case = ignore_case

    @debug_hook
    def process(self, pos, data, ctx):
        old = pos
        if not self.ignore_case:
            for c in self.chars:
                if data[pos] == c:
                    pos += 1
                else:
                    msg = "Expected {}.".format(self.chars)
                    ctx.set(old, msg)
                    raise Exception(msg)
            return pos, (self.chars if self.value is self._NULL else self.value)
        else:
            result = []
            for c in self.chars:
                if data[pos].lower() == c:
                    result.append(data[pos])
                    pos += 1
                else:
                    msg = "Expected case insensitive {}.".format(self.chars)
                    ctx.set(old, msg)
                    raise Exception(msg)
            return pos, ("".join(result) if self.value is self._NULL else self.value)


class String(Parser):
    def __init__(self, chars, echars=None, min_length=1):
        super(String, self).__init__()
        self.chars = set(chars)
        self.echars = set(echars) if echars else set()
        self.min_length = min_length

    @debug_hook
    def process(self, pos, data, ctx):
        results = []
        p = data[pos]
        old = pos
        while p in self.chars or p == "\\":
            if p == "\\" and data[pos + 1] in self.echars:
                results.append(data[pos + 1])
                pos += 2
            elif p in self.chars:
                results.append(p)
                pos += 1
            else:
                break
            p = data[pos]
        if len(results) < self.min_length:
            msg = "Expected {} of {}.".format(self.min_length, self.chars)
            ctx.set(old, msg)
            raise Exception(msg)
        return pos, "".join(results)


class EnclosedComment(Parser):
    def __init__(self, s, e):
        super(EnclosedComment, self).__init__()
        Start = Literal(s)
        End = Literal(e)
        p = Start >> AnyChar.until(End).map(lambda x: "".join(x)) << End
        self.add_child(p)

    @debug_hook
    def process(self, pos, data, ctx):
        return self.children[0].process(pos, data, ctx)


class OneLineComment(Parser):
    def __init__(self, s):
        super(OneLineComment, self).__init__()
        p = Literal(s) >> Opt(String(set(string.printable) - set("\r\n")), "")
        self.add_child(p)

    @debug_hook
    def process(self, pos, data, ctx):
        return self.children[0].process(pos, data, ctx)


class WithIndent(Wrapper):
    @debug_hook
    def process(self, pos, data, ctx):
        new, _ = WS.process(pos, data, ctx)
        try:
            ctx.indents.append(ctx.col(new))
            return self.children[0].process(new, data, ctx)
        finally:
            ctx.indents.pop()


class HangingString(Parser):
    def __init__(self, chars, echars=None, min_length=1):
        super(HangingString, self).__init__()
        p = String(chars, echars=echars, min_length=min_length)
        self.add_child(p << (EOL | EOF))

    @debug_hook
    def process(self, pos, data, ctx):
        old = pos
        results = []
        while True:
            try:
                if ctx.col(pos) > ctx.indents[-1]:
                    pos, res = self.children[0].process(pos, data, ctx)
                    results.append(res.rstrip(" \\"))
                else:
                    pos = old
                    break
                old = pos
                pos, _ = WS.process(pos, data, ctx)
            except Exception:
                break
        ret = " ".join(results)
        return pos, ret


class StartTagName(Wrapper):
    @debug_hook
    def process(self, pos, data, ctx):
        pos, res = self.children[0].process(pos, data, ctx)
        ctx.tags.append(res)
        return pos, res


class EndTagName(Wrapper):
    def __init__(self, parser, ignore_case=False):
        super(EndTagName, self).__init__(parser)
        self.ignore_case = ignore_case

    @debug_hook
    def process(self, pos, data, ctx):
        pos, res = self.children[0].process(pos, data, ctx)
        expect = ctx.tags.pop()

        r, e = res, expect

        if self.ignore_case:
            r = res.lower()
            e = expect.lower()

        if r != e:
            msg = "Expected {}. Got {}.".format(expect, res)
            ctx.set(pos, msg)
            raise Exception(msg)
        return pos, res


def make_number(sign, int_part, frac_part):
    tmp = sign + int_part + ("".join(frac_part) if frac_part else "")
    return float(tmp) if "." in tmp else int(tmp)


def skip_none(x):
    return [i for i in x if i is not None]


EOF = EOF()
EOL = InSet("\n\r") % "EOL"
LineEnd = Wrapper(EOL | EOF)
EQ = Char("=")
LT = Char("<")
GT = Char(">")
FS = Char("/")
LeftCurly = Char("{")
RightCurly = Char("}")
LeftBracket = Char("[")
RightBracket = Char("]")
LeftParen = Char("(")
RightParen = Char(")")
Colon = Char(":")
SemiColon = Char(";")
Comma = Char(",")
AnyChar = InSet(string.printable) % "Any Char"
NonZeroDigit = InSet(set(string.digits) - set("0"))
Digit = InSet(string.digits) % "Digit"
Digits = String(string.digits) % "Digits"
Letter = InSet(string.ascii_letters)
Letters = String(string.ascii_letters)
WSChar = InSet(set(string.whitespace) - set("\n\r")) % "Whitespace w/o EOL"
WS = Many(InSet(string.whitespace) % "WS") % "Whitespace"
Number = (Lift(make_number) * Opt(Char("-"), "") * Digits * Opt(Char(".") + Digits)) % "Number"
SingleQuotedString = Char("'") >> String(set(string.printable) - set("'"), "'") << Char("'")
DoubleQuotedString = Char('"') >> String(set(string.printable) - set('"'), '"') << Char('"')
QuotedString = Wrapper(DoubleQuotedString | SingleQuotedString) % "Quoted String"
