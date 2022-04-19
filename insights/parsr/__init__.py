"""
parsr is a library for building parsers based on `parsing expression grammars or
PEGs <http://bford.info/pub/lang/peg.pdf>`_.

You build a parser by making subparsers to match simple building blocks like
numbers, strings, symbols, etc. and then composing them to reflect the higher
level structure of your language.

Some means of combination are like those of regular expressions: sequences,
alternatives, repetition, optional matching, etc. However, matching is always
greedy. parsr also allows recursive definitions and the ability to transform
the match of any subparser with a function. The parser can recognize and
interpret its input at the same time.

Here's an example that evaluates arithmetic expressions.

    .. code-block:: python

        from insights.parsr import EOF, Forward, InSet, Many, Number, WS

        def op(args):
            ans, rest = args
            for op, arg in rest:
                if op == "+":
                    ans += arg
                elif op == "-":
                    ans -= arg
                elif op == "*":
                    ans *= arg
                else:
                    ans /= arg
            return ans


        LP = Char("(")
        RP = Char(")")

        expr = Forward()  # Forward declarations allow recursive structure
        factor = WS >> (Number | (LP >> expr << RP)) << WS
        term = (factor + Many(InSet("*/") + factor)).map(op)

        # Notice the funny assignment of Forward definitions.
        expr <= (term + Many(InSet("+-") + term)).map(op)

        evaluate = expr << EOF
"""
from __future__ import print_function
import functools
import logging
import os
import string
import traceback
from bisect import bisect_left
from six import StringIO, with_metaclass

log = logging.getLogger(__name__)


class Node(object):
    """
    Node is the base class of all parsers. It's a generic tree structure with
    each instance containing a list of its children. Its main purpose is to
    simplify pretty printing.
    """
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
    """
    Converts a PEG into a pretty printed string.
    """
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
    """
    Pretty prints a PEG.
    """
    print(text_format(tree))


def _debug_hook(func):
    """
    _debug_hook wraps the process function of every parser. It maintains a
    stack of active parsers during evaluation to help with error reporting and
    prints diagnostic messages for parsers with debug enabled.
    """
    @functools.wraps(func)
    def inner(self, pos, data, ctx):
        if ctx.function_error is not None:
            # no point in continuing...
            raise Exception()
        ctx.parser_stack.append(self)
        if self._debug:
            line = ctx.line(pos) + 1
            col = ctx.col(pos) + 1
            log.debug("Trying {0} at line {1} col {2}".format(self, line, col))
        try:
            res = func(self, pos, data, ctx)
            if self._debug:
                log.debug("Result: {0}".format(res[1]))
            return res
        except:
            if self._debug:
                ps = "-> ".join([str(p) for p in ctx.parser_stack])
                log.debug("Failed: {0}".format(ps))
            raise
        finally:
            ctx.parser_stack.pop()
    return inner


class Backtrack(Exception):
    """
    Mapped or Lifted functions should Backtrack if they want to fail without
    causing parsing to fail.
    """
    def __init__(self, msg):
        super(Backtrack, self).__init__(msg)


class Context(object):
    """
    An instance of Context is threaded through the process call to every
    parser. It stores an indention stack to track hanging indents, a tag stack
    for grammars like xml or apache configuration, the active parser stack for
    error reporting, and accumulated errors for the farthest position reached.
    """
    def __init__(self, lines, src=None):
        self.pos = -1
        self.indents = []
        self.tags = []
        self.src = src
        self.lines = [i for i, x in enumerate(lines) if x == "\n"]
        self.parser_stack = []
        self.errors = []
        self.function_error = None

    def set(self, pos, msg):
        """
        Every parser that encounters an error calls set with the current
        position and a message. If the error is at the farthest position
        reached by any other parser, the active parser stack and message are
        accumulated onto a list of errors for that position. If the position is
        beyond any previous errors, the error list is cleared before the active
        stack and new error are recorded. This is the "farthest failure
        heurstic."
        """
        if pos > self.pos:
            self.errors = []

        if pos >= self.pos:
            self.pos = pos
            self.errors.append((list(self.parser_stack), msg))

    def line(self, pos):
        return bisect_left(self.lines, pos)

    def col(self, pos):
        p = self.line(pos)
        if p == 0:
            return pos
        return (pos - self.lines[p - 1] - 1)


class _ParserMeta(type):
    """
    ParserMeta wraps every parser subclass's process function with the
    ``_debug_hook`` decorator.
    """
    def __init__(cls, name, bases, clsdict):
        orig = getattr(cls, "process")
        setattr(cls, "process", _debug_hook(orig))


class Parser(with_metaclass(_ParserMeta, Node)):
    """
    Parser is the common base class of all Parsers.
    """
    def __init__(self):
        super(Parser, self).__init__()
        self.name = None
        self._debug = False

    def debug(self, d=True):
        """
        Set to ``True`` to enable diagnostic messages before and after the
        parser is invoked.
        """
        self._debug = d
        return self

    @staticmethod
    def _accumulate(first, rest):
        results = [first] if first else []
        if rest:
            results.extend(rest)
        return results

    def sep_by(self, sep):
        """
        Return a parser that matches zero or more instances of the current
        parser separated by instances of the parser sep.
        """
        return Lift(self._accumulate) * Opt(self) * Many(sep >> self)

    def until(self, pred):
        """
        Return an :py:class:`Until` parser that matches zero or more instances
        of the current parser until the pred parser succeeds.
        """
        return Until(self, pred)

    def map(self, func):
        """
        Return a :py:class:`Map` parser that transforms the results of the
        current parser with the function func.
        """
        return Map(self, func)

    def __add__(self, other):
        """
        Return a :py:class:`Sequence` that requires the current parser to be
        followed by the other parser. Additional calls to ``+`` on the returned
        parser will cause it to accumulate "other" onto itself instead of
        creating new Sequences. This has the desirable effect of causing
        sequence matches to be represented as flat lists instead of trees, but
        it can also have unintended consequences if a sequence is used in
        multiple parts of a grammar as the initial element of another sequence.

        :py:class:`Choice`s also accumulate and can lead to similar surprises.
        """
        return Sequence([self, other])

    def __or__(self, other):
        """
        Return a :py:class:`Choice` that requires the current parser or the
        other parser to match. Additional calls to ``|`` on the returned parser
        will cause it to accumulate "other" onto itself instead of creating new
        Choices. This has the desirable effect of making choices more
        efficient, but it can also have unintended consequences if a choice is
        used in multiple parts of a grammar as the initial element of another
        :py:class:`Choice`.
        """
        return Choice([self, other])

    def __lshift__(self, other):
        """
        Return a parser that requires the current parser and the other parser
        but ignores the other parser's result. Both parsers consume input.
        """
        return KeepLeft(self, other)

    def __rshift__(self, other):
        """
        Return a parser that requires the current parser and the other parser
        but ignores the current parser's result. Both parsers consume input.
        """
        return KeepRight(self, other)

    def __and__(self, other):
        """
        Return a parser that requires the current parser and the other parser
        but ignores the current parser's result. Only the current parser
        consumes input.
        """
        return FollowedBy(self, other)

    def __truediv__(self, other):
        """
        Return a parser that requires the current parser but requires the other
        parser to fail. Only the current parser consumes input.
        """
        return NotFollowedBy(self, other)

    def __mod__(self, name):
        """
        Gives the current parser a human friendly name for display in error
        messages and PEG rendering.
        """
        self.name = name
        return self

    def process(self, pos, data, ctx):
        raise NotImplementedError()

    def __call__(self, data, src=None, Ctx=Context):
        """
        Invoke the parser like a function on a regular string of characters.

        Optinally provide an arbitrary external object that will be made available to
        the Context instance. You also can provide a Context subclass if your
        parsers have particular needs not covered by the default
        implementation that provides significant indent and tag stacks.
        """
        data = list(data)
        data.append(None)  # add a terminal so we don't overrun
        ctx = Ctx(data, src=src)

        try:
            _, ret = self.process(0, data, ctx)
            return ret
        except Exception:
            pass

        if ctx.function_error is not None:
            pos, msg = ctx.function_error
            lineno = ctx.line(pos) + 1
            colno = ctx.col(pos) + 1
            msg = "At line {0} column {1}: {2}".format(lineno, colno, msg)
            raise Exception(msg)

        err = StringIO()

        lineno = ctx.line(ctx.pos) + 1
        colno = ctx.col(ctx.pos) + 1
        msg = "At line {0} column {1}:"
        print(msg.format(lineno, colno, ctx.lines), file=err)
        for parsers, msg in ctx.errors:
            names = " -> ".join([p.name for p in parsers if p.name])
            v = data[ctx.pos] or "EOF"
            print(names, file=err)
            print("    {0} Got {1!r}.".format(msg, v), file=err)
        err.seek(0)
        raise Exception(err.read())

    def __repr__(self):
        return self.name or self.__class__.__name__


class AnyChar(Parser):
    def process(self, pos, data, ctx):
        c = data[pos]
        if c is not None:
            return (pos + 1, c)
        msg = "Expected any character."
        ctx.set(pos, msg)
        raise Exception(msg)


class Char(Parser):
    """
    Char matches a single character.

        .. code-block:: python

            a = Char("a")     # parses a single "a"
            val = a("a")      # produces an "a" from the data.
            val = a("b")      # raises an exception

    """
    def __init__(self, char):
        super(Char, self).__init__()
        self.char = char

    def process(self, pos, data, ctx):
        if data[pos] == self.char:
            return (pos + 1, self.char)
        msg = "Expected {0}.".format(self.char)
        ctx.set(pos, msg)
        raise Exception(msg)

    def __repr__(self):
        if self.name is None:
            return "Char({0})".format(self.char)
        return self.name


class InSet(Parser):
    """
    InSet matches any single character from a set.

        .. code-block:: python

            vowel = InSet("aeiou")  # or InSet(set("aeiou"))
            val = vowel("a")  # okay
            val = vowel("e")  # okay
            val = vowel("i")  # okay
            val = vowel("o")  # okay
            val = vowel("u")  # okay
            val = vowel("y")  # raises an exception

    """
    def __init__(self, s, name=None):
        super(InSet, self).__init__()
        self.values = set(s)
        self.name = name

    def process(self, pos, data, ctx):
        c = data[pos]
        if c in self.values:
            return (pos + 1, c)
        msg = "Expected {0}.".format(self)
        ctx.set(pos, msg)
        raise Exception(msg)

    def __repr__(self):
        if self.name is None:
            return "InSet({0!r})".format(sorted(self.values))
        return super(InSet, self).__repr__()


class String(Parser):
    """
    Match one or more characters in a set. Matching is greedy.

        .. code-block:: python

            vowels = String("aeiou")
            val = vowels("a")            # returns "a"
            val = vowels("u")            # returns "u"
            val = vowels("aaeiouuoui")   # returns "aaeiouuoui"
            val = vowels("uoiea")        # returns "uoiea"
            val = vowels("oouieaaea")    # returns "oouieaaea"
            val = vowels("ga")           # raises an exception

    """
    def __init__(self, chars, echars=None, min_length=1):
        super(String, self).__init__()
        self.chars = set(chars)
        self.echars = set(echars) if echars else set()
        self.min_length = min_length

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
            msg = "Expected {0} of {1}.".format(self.min_length, sorted(self.chars))
            ctx.set(old, msg)
            raise Exception(msg)
        return pos, "".join(results)


class Literal(Parser):
    """
    Match a literal string. The ``value`` keyword lets you return a python
    value instead of the matched input. The ``ignore_case`` keyword makes the
    match case insensitive.

        .. code-block:: python

            lit = Literal("true")
            val = lit("true")  # returns "true"
            val = lit("True")  # raises an exception
            val = lit("one")   # raises an exception

            lit = Literal("true", ignore_case=True)
            val = lit("true")  # returns "true"
            val = lit("TRUE")  # returns "TRUE"
            val = lit("one")   # raises an exception

            t = Literal("true", value=True)
            f = Literal("false", value=False)
            val = t("true")  # returns the boolean True
            val = t("True")  # raises an exception

            val = f("false") # returns the boolean False
            val = f("False") # raises and exception

            t = Literal("true", value=True, ignore_case=True)
            f = Literal("false", value=False, ignore_case=True)
            val = t("true")  # returns the boolean True
            val = t("True")  # returns the boolean True

            val = f("false") # returns the boolean False
            val = f("False") # returns the boolean False
    """
    _NULL = object()

    def __init__(self, chars, value=_NULL, ignore_case=False):
        super(Literal, self).__init__()
        self.chars = chars if not ignore_case else chars.lower()
        self.value = value
        self.ignore_case = ignore_case
        self.name = "Literal{0!r}".format(self.chars)

    def process(self, pos, data, ctx):
        old = pos
        if not self.ignore_case:
            for c in self.chars:
                if data[pos] == c:
                    pos += 1
                else:
                    msg = "Expected {0!r}.".format(self.chars)
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
                    msg = "Expected case insensitive {0!r}.".format(self.chars)
                    ctx.set(old, msg)
                    raise Exception(msg)
            return pos, ("".join(result) if self.value is self._NULL else self.value)


class Wrapper(Parser):
    """
    Parser that wraps another parser. This can be used to prevent sequences and
    choices from accidentally accumulating other parsers when used in multiple
    parts of a grammar.
    """
    def __init__(self, parser):
        super(Wrapper, self).__init__()
        self.add_child(parser)

    def process(self, pos, data, ctx):
        return self.children[0].process(pos, data, ctx)


class Mark(object):
    """
    An object created by :py:class:`PosMarker` to capture a value at a position
    in the input. Marks can give more context to a value transformed by mapped
    functions.
    """
    def __init__(self, lineno, col, value):
        self.lineno = lineno
        self.col = col
        self.value = value


class PosMarker(Wrapper):
    """
    Save the line number and column of a subparser by wrapping it in a
    PosMarker. The value of the parser that handled the input as well as the
    initial input position will be returned as a :py:class:`Mark`.
    """
    def process(self, pos, data, ctx):
        lineno = ctx.line(pos) + 1
        col = ctx.col(pos) + 1
        pos, result = super(PosMarker, self).process(pos, data, ctx)
        return pos, Mark(lineno, col, result)


class Sequence(Parser):
    """
    A Sequence requires all of its children to succeed. It returns a list of
    the values they matched.

    Additional uses of ``+`` on the parser will cause it to accumulate parsers
    onto itself instead of creating new Sequences. This has the desirable
    effect of causing sequence results to be represented as flat lists instead
    of trees, but it can also have unintended consequences if a sequence is
    used in multiple parts of a grammar as the initial element of another
    sequence. Use a :py:class:`Wrapper` to prevent that from happening.

        .. code-block :: python

            a = Char("a")     # parses a single "a"
            b = Char("b")     # parses a single "b"
            c = Char("c")     # parses a single "c"

            ab = a + b        # parses a single "a" followed by a single "b"
                              # (a + b) creates a "Sequence" object. Using `ab`
                              # as an element in a later sequence would modify
                              # its original definition.

            abc = a + b + c   # parses "abc"
                              # (a + b) creates a "Sequence" object to which c
                              # is appended

            val = ab("ab")    # produces a list ["a", "b"]
            val = ab("a")     # raises an exception
            val = ab("b")     # raises an exception
            val = ab("ac")    # raises an exception
            val = ab("cb")    # raises an exception

            val = abc("abc")  # produces ["a", "b", "c"]
    """
    def __init__(self, children):
        super(Sequence, self).__init__()
        self.set_children(children)

    def __add__(self, other):
        return self.add_child(other)

    def process(self, pos, data, ctx):
        results = []
        for p in self.children:
            pos, res = p.process(pos, data, ctx)
            results.append(res)
        return pos, results


class Choice(Parser):
    """
    A Choice requires at least one of its children to succeed, and it returns
    the value of the one that matched. Alternatives in a choice are tried left
    to right, so they have a definite priority. This a feature of PEGs over
    context free grammars.

    Additional uses of ``|`` on the parser will cause it to accumulate parsers
    onto itself instead of creating new Choices. This has the desirable effect
    of increasing efficiency, but it can also have unintended consequences if a
    choice is used in multiple parts of a grammar as the initial element of
    another choice. Use a :py:class:`Wrapper` to prevent that from happening.

        .. code-block:: python

            abc = a | b | c   # alternation or choice.
            val = abc("a")    # parses a single "a"
            val = abc("b")    # parses a single "b"
            val = abc("c")    # parses a single "c"
            val = abc("d")    # raises an exception
    """
    def __init__(self, children):
        super(Choice, self).__init__()
        self.set_children(children)

    def __or__(self, other):
        return self.add_child(other)

    def process(self, pos, data, ctx):
        for c in self.children:
            try:
                return c.process(pos, data, ctx)
            except:
                pass
        raise Exception()


class Many(Parser):
    """
    Many wraps another parser and requires it to match a certain number of
    times.

    When Many matches zero occurences (``lower=0``), it always succeeds. Keep
    this in mind when using it in a list of alternatives or with
    :py:class:`FollowedBy` or :py:class:`NotFollowedBy`.

    The results are returned as a list.

        .. code-block:: python

            x = Char("x")
            xs = Many(x)      # parses many (or no) x's in a row
            val = xs("")      # returns []
            val = xs("a")     # returns []
            val = xs("x")     # returns ["x"]
            val = xs("xxxxx") # returns ["x", "x", "x", "x", "x"]
            val = xs("xxxxb") # returns ["x", "x", "x", "x"]

            ab = Many(a + b)  # parses "abab..."
            val = ab("")      # produces []
            val = ab("ab")    # produces [["a", b"]]
            val = ab("ba")    # produces []
            val = ab("ababab")# produces [["a", b"], ["a", "b"], ["a", "b"]]

            ab = Many(a | b)  # parses any combination of "a" and "b" like
                              # "aababbaba..."
            val = ab("aababb")# produces ["a", "a", "b", "a", "b", "b"]
            bs = Many(Char("b"), lower=1) # requires at least one "b"

    """
    def __init__(self, parser, lower=0):
        super(Many, self).__init__()
        self.add_child(parser)
        self.lower = lower

    def process(self, pos, data, ctx):
        orig = pos
        results = []
        p = self.children[0]
        while True:
            try:
                pos, res = p.process(pos, data, ctx)
                results.append(res)
            except Exception:
                break
        if len(results) < self.lower:
            child = self.children[0]
            msg = "Expected at least {0} of {1}.".format(self.lower, child)
            ctx.set(orig, msg)
            raise Exception()

        return pos, results

    def __repr__(self):
        if not self.name:
            return "Many({0}, lower={1})".format(self.children[0], self.lower)
        return super(Many, self).__repr__()


class Until(Parser):
    """
    Until wraps a parser and a terminal parser. It accumulates matches of the
    first parser until the terminal parser succeeds. Input for the terminal
    parser is left unread, and the results of the first parser are returned as
    a list.

    Since Until can match zero occurences, it always succeeds. Keep this in
    mind when using it in a list of alternatives or with :py:class:`FollowedBy`
    or :py:class:`NotFollowedBy`.

        .. code-block:: python

            cs = AnyChar.until(Char("y")) # parses many (or no) characters
                                          # until a "y" is encountered.

            val = cs("")                  # returns []
            val = cs("a")                 # returns ["a"]
            val = cs("x")                 # returns ["x"]
            val = cs("ccccc")             # returns ["c", "c", "c", "c", "c"]
            val = cs("abcdycc")           # returns ["a", "b", "c", "d"]

    """
    def __init__(self, parser, predicate):
        super(Until, self).__init__()
        self.set_children([parser, predicate])

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
    """
    FollowedBy takes a parser and a predicate parser. The initial parser
    matches only if the predicate matches the input after it. On success, input
    for the predicate is left unread, and the result of the first parser is
    returned.

        .. code-block:: python

            ab = Char("a") & Char("b") # matches an "a" followed by a "b", but
                                       # the "b" isn't consumed from the input.
            val = ab("ab")             # returns "a" and leaves "b" to be
                                       # consumed.
            val = ab("ac")             # raises an exception and doesn't
                                       # consume "a".

    """
    def __init__(self, child, follow):
        super(FollowedBy, self).__init__()
        self.set_children([child, follow])

    def process(self, pos, data, ctx):
        left, right = self.children
        new, res = left.process(pos, data, ctx)
        right.process(new, data, ctx)
        return new, res


class NotFollowedBy(Parser):
    """
    NotFollowedBy takes a parser and a predicate parser. The initial parser
    matches only if the predicate parser fails to match the input after it. On
    success, input for the predicate is left unread, and the result of the
    first parser is returned.

        .. code-block:: python

            anb = Char("a") / Char("b") # matches an "a" not followed by a "b".
            val = anb("ac")             # returns "a" and leaves "c" to be
                                        # consumed
            val = anb("ab")             # raises an exception and doesn't
                                        # consume "a".

    """
    def __init__(self, child, follow):
        super(NotFollowedBy, self).__init__()
        self.set_children([child, follow])

    def process(self, pos, data, ctx):
        left, right = self.children
        new, res = left.process(pos, data, ctx)
        try:
            right.process(new, data, ctx)
        except Exception:
            return new, res
        else:
            msg = "{0} can't follow {1}".format(right, left)
            ctx.set(new, msg)
            raise Exception()


class KeepLeft(Parser):
    """
    KeepLeft takes two parsers. It requires them both to succeed but only
    returns results for the first one. It consumes input for both.

        .. code-block:: python

            a = Char("a")
            q = Char('"')

            aq = a << q      # like a + q except only the result of a is
                             # returned
            val = aq('a"')   # returns "a". Keeps the thing on the left of the
                             # <<

    """
    def __init__(self, left, right):
        super(KeepLeft, self).__init__()
        self.set_children([left, right])

    def process(self, pos, data, ctx):
        left, right = self.children
        pos, res = left.process(pos, data, ctx)
        pos, _ = right.process(pos, data, ctx)
        return pos, res


class KeepRight(Parser):
    """
    KeepRight takes two parsers. It requires them both to succeed but only
    returns results for the second one. It consumes input for both.

        .. code-block:: python

            q = Char('"')
            a = Char("a")

            qa = q >> a      # like q + a except only the result of a is
                             # returned
            val = qa('"a')   # returns "a". Keeps the thing on the right of the
                             # >>

    """
    def __init__(self, left, right):
        super(KeepRight, self).__init__()
        self.set_children([left, right])

    def process(self, pos, data, ctx):
        left, right = self.children
        pos, _ = left.process(pos, data, ctx)
        return right.process(pos, data, ctx)


class Opt(Parser):
    """
    Opt wraps a single parser and returns its value if it succeeds. It returns
    a default value otherwise. The input pointer is advanced only if the
    wrapped parser succeeds.

        .. code-block:: python

            a = Char("a")
            o = Opt(a)      # matches an "a" if its available. Still succeeds
                            # otherwise but doesn't advance the read pointer.
            val = o("a")    # returns "a"
            val = o("b")    # returns None. Read pointer is not advanced.

            o = Opt(a, default="x") # matches an "a" if its available. Returns
                                    # "x" otherwise.
            val = o("a")    # returns "a"
            val = o("b")    # returns "x". Read pointer is not advanced.

    """
    def __init__(self, p, default=None):
        super(Opt, self).__init__()
        self.add_child(p)
        self.default = default

    def process(self, pos, data, ctx):
        try:
            return self.children[0].process(pos, data, ctx)
        except Exception:
            return pos, self.default


class Map(Parser):
    """
    Map wraps a parser and a function. It returns the result of using the
    function to transform the wrapped parser's result.

    Example::

        .. code-block:: python

            Digit = InSet("0123456789")
            Digits = Many(Digit, lower=1)
            Number = Digits.map(lambda x: int("".join(x)))

    """
    def __init__(self, child, func):
        super(Map, self).__init__()
        self.add_child(child)
        self.func = func

    def process(self, pos, data, ctx):
        pos, res = self.children[0].process(pos, data, ctx)
        try:
            return pos, self.func(res)
        except Backtrack as bt:
            ctx.set(pos, bt.msg)
            raise
        except:
            tb = traceback.format_exc()
            msg = (self.name or "Map") + " raised{l}{tb}".format(l=os.linesep, tb=tb)
            ctx.function_error = (pos, msg)
            raise

    def __repr__(self):
        if not self.name:
            return "Map({0}({1}))".format(self.func.__name__, self.children[0])
        return super(Map, self).__repr__()


class Lift(Parser):
    """
    Lift wraps a function of multiple arguments. Use it with the multiplication
    operator on as many parsers as function arguments, and the results of those
    parsers will be passed to the function. The result of a Lift parser is the
    result of the wrapped function.

    Example::

        .. code-block:: python

            def comb(a, b, c):
                return "".join([a, b, c])

            # You'd normally invoke comb like comb("x", "y", "z"), but you can
            # "lift" it for use with parsers like this:

            x = Char("x")
            y = Char("y")
            z = Char("z")
            p = Lift(comb) * x * y * z

            # The * operator separates parsers whose results will go into the
            # arguments of the lifted function. I've used Char above, but x, y,
            # and z can be arbitrarily complex.

            val = p("xyz")  # would return "xyz"
            val = p("xyx")  # raises an exception. nothing would be consumed

    """
    def __init__(self, func):
        super(Lift, self).__init__()
        self.func = func

    def __mul__(self, other):
        return self.add_child(other)

    def process(self, pos, data, ctx):
        results = []
        for c in self.children:
            pos, res = c.process(pos, data, ctx)
            results.append(res)
        try:
            return pos, self.func(*results)
        except Backtrack as bt:
            ctx.set(pos, bt.msg)
            raise
        except:
            tb = traceback.format_exc()
            msg = (self.name or "Lift") + " raised{l}{tb}".format(l=os.linesep, tb=tb)
            ctx.set(pos, msg)
            ctx.function_error = (pos, msg)
            raise


class Forward(Parser):
    """
    Forward allows recursive grammars where a nonterminal's definition includes
    itself directly or indirectly. You initially create a Forward nonterminal
    with regular assignment.

        .. code-block:: python

            expr = Forward()

    You later give it its real definition with the ``<=`` operator.

        .. code-block:: python

            expr <= (term + Many(LowOps + term)).map(op)

    """
    def __init__(self):
        super(Forward, self).__init__()
        self.delegate = None

    def __le__(self, delegate):
        self.set_children([delegate])

    def process(self, pos, data, ctx):
        return self.children[0].process(pos, data, ctx)


class EOF(Parser):
    """
    EOF marks the end of input. This parser doesn't need to be created
    directly. An instance is provided in this module.

        .. code-block:: python

            # Top executes an Expr and ensures no input is left over.
            Top = Expr << EOF

    """
    def process(self, pos, data, ctx):
        if data[pos] is None:
            return pos, None
        msg = "Expected end of input."
        ctx.set(pos, msg)
        raise Exception(msg)


class EnclosedComment(Parser):
    """
    EnclosedComment matches a start literal, an end literal, and all characters
    between. It returns the content between the start and end.

        .. code-block:: python

            Comment = EnclosedComment("/*", "*/")

    """
    def __init__(self, s, e):
        super(EnclosedComment, self).__init__()
        Start = Literal(s)
        End = Literal(e)
        p = Start >> AnyChar.until(End).map(lambda x: "".join(x)) << End
        self.add_child(p)

    def process(self, pos, data, ctx):
        return self.children[0].process(pos, data, ctx)


class OneLineComment(Parser):
    """
    OneLineComment matches everything from a literal to the end of a line,
    excluding the end of line characters themselves. It returns the content
    between the start literal and the end of the line.

        .. code-block:: python

            Comment = OneLineComment("#") | OneLineComment("//")

    """
    def __init__(self, s):
        super(OneLineComment, self).__init__()
        p = Literal(s) >> Opt(AnyChar.until(InSet("\r\n")), "")
        self.add_child(p)

    def process(self, pos, data, ctx):
        return self.children[0].process(pos, data, ctx)


class WithIndent(Wrapper):
    """
    Consumes whitespace until a non-whitespace character is encountered, pushes
    the column position onto an indentation stack in the :py:class:`Context`,
    and then calls the parser it's wrapping. The wrapped parser and any
    of its children can make use of the saved indentation. Returns the value of
    the wrapped parser.

    WithIndent allows :py:class:`HangingString` to work by giving a way to mark
    how indented following lines must be to count as continuations.

        .. code-block:: python

            Key = WS >> PosMarker(String(key_chars)) << WS
            Sep = InSet(sep_chars, "Sep")
            Value = WS >> (Boolean | HangingString(value_chars))
            KVPair = WithIndent(Key + Opt(Sep >> Value))

    """
    def process(self, pos, data, ctx):
        new, _ = WS.process(pos, data, ctx)
        try:
            ctx.indents.append(ctx.col(new))
            return self.children[0].process(new, data, ctx)
        finally:
            ctx.indents.pop()


class HangingString(Parser):
    """
    HangingString matches lines with indented continuations like in ini files.

        .. code-block:: python

            Key = WS >> PosMarker(String(key_chars)) << WS
            Sep = InSet(sep_chars, "Sep")
            Value = WS >> (Boolean | HangingString(value_chars))
            KVPair = WithIndent(Key + Opt(Sep >> Value))

    """
    def __init__(self, chars, echars=None, min_length=1):
        super(HangingString, self).__init__()
        p = String(chars, echars=echars, min_length=min_length)
        self.add_child(p << (EOL | EOF))

    def process(self, pos, data, ctx):
        old = pos
        results = []
        while True:
            try:
                if ctx.col(pos) > ctx.indents[-1]:
                    pos, res = self.children[0].process(pos, data, ctx)
                    # Remove any inline comments.
                    results.append(res.split("#", 1)[0].rstrip(" \\"))
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
    """
    Wraps a parser that represents a starting tag for grammars like xml, html,
    etc. The tag result is captured and put onto a tag stack in the
    :py:class:`Context` object.
    """
    def process(self, pos, data, ctx):
        pos, res = self.children[0].process(pos, data, ctx)
        ctx.tags.append(res)
        return pos, res


class EndTagName(Wrapper):
    """
    Wraps a parser that represents an end tag for grammars like xml, html, etc.
    The result is captured and compared to the last tag on the tag stack in the
    :py:class:`Context` object. The tags must match for the parse to be
    successful.
    """
    def __init__(self, parser, ignore_case=False):
        super(EndTagName, self).__init__(parser)
        self.ignore_case = ignore_case

    def process(self, pos, data, ctx):
        pos, res = self.children[0].process(pos, data, ctx)
        expect = ctx.tags.pop()

        r, e = res, expect

        if self.ignore_case:
            r = res.lower()
            e = expect.lower()

        if r != e:
            msg = "Expected {0!r}. Got {1!r}.".format(expect, res)
            ctx.set(pos, msg)
            raise Exception(msg)
        return pos, res


class EmptyQuotedString(Parser):
    def __init__(self, chars):
        super(EmptyQuotedString, self).__init__()
        single = Char("'") >> String(set(chars) - set("'"), "'", 0) << Char("'")
        double = Char('"') >> String(set(chars) - set('"'), '"', 0) << Char('"')
        self.add_child(single | double)

    def process(self, pos, data, ctx):
        return self.children[0].process(pos, data, ctx)


def _make_number(sign, int_part, frac_part):
    tmp = sign + int_part + ("".join(frac_part) if frac_part else "")
    return float(tmp) if "." in tmp else int(tmp)


def skip_none(x):
    return [i for i in x if i is not None]


EOF = EOF() % "EOF"
EOL = InSet("\n\r") % "EOL"
LineEnd = Wrapper(EOL | EOF) % "LineEnd"
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
AnyChar = AnyChar() % "any character"
NonZeroDigit = InSet(set(string.digits) - set("0")) % "non zero digit"
Digit = InSet(string.digits) % "digit"
Digits = String(string.digits) % "digits"
Letter = InSet(string.ascii_letters) % "ASCII letter"
Letters = String(string.ascii_letters) % "ASCII letters"
WSChar = InSet(set(string.whitespace) - set("\n\r")) % "whitespace w/o EOL"
WS = Many(InSet(string.whitespace) % "any whitespace")
Number = (Lift(_make_number) * Opt(Char("-"), "") * Digits * Opt(Char(".") + Digits)) % "number"
SingleQuotedString = Char("'") >> String(set(string.printable) - set("'"), "'") << Char("'")
DoubleQuotedString = Char('"') >> String(set(string.printable) - set('"'), '"') << Char('"')
QuotedString = Wrapper(DoubleQuotedString | SingleQuotedString) % "quoted string"
