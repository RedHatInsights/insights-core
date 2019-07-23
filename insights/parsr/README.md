# parsr
parsr is a library for parsing and interpreting [parsing expression grammars or
PEGS](http://bford.info/pub/lang/peg.pdf) with extensions for grammars that
require knowledge of indentation or matching tags.

It contains a small set of combinators that perform recursive decent with
backtracking. Fancy tricks like rewriting left recursions and optimizations like
[packrat](https://pdos.csail.mit.edu/~baford/packrat/thesis/thesis.pdf) are not
implemented since the goal is a library that's small yet sufficient for parsing
non-standard configuration files. It also includes a generic data model that
parsers can target to take advantage of an [embedded query system](https://github.com/RedHatInsights/insights-core/blob/master/insights/parsr/query).

## Install
1. Ensure python3.6 or python3.7 is installed.
2. `python3.7 -m venv myproject && cd myproject`
3. `source bin/activate`
4. `pip install parsr`

## Examples
* [Arithmetic](https://github.com/RedHatInsights/insights-core/blob/master/insights/parsr/examples/arith.py)
* [Generic Key/Value Pair configuration](https://github.com/RedHatInsights/insights-core/blob/master/insights/parsr/examples/kvpairs.py)
* [INI configuration](https://github.com/RedHatInsights/insights-core/blob/master/insights/parsr/iniparser.py) is an example of significant indentation.
* [json](https://github.com/RedHatInsights/insights-core/blob/master/insights/parsr/examples/json_parser.py)
* [httpd configuration](https://github.com/RedHatInsights/insights-core/blob/master/insights/parsr/examples/httpd_conf.py) is an example of matching starting and ending tags.
* [nginx configuration](https://github.com/RedHatInsights/insights-core/blob/master/insights/parsr/examples/nginx_conf.py)
* [corosync configuration](https://github.com/RedHatInsights/insights-core/blob/master/insights/parsr/examples/corosync_conf.py)
* [multipath configuration](https://github.com/RedHatInsights/insights-core/blob/master/insights/parsr/examples/multipath_conf.py)
* [logrotate configuration](https://github.com/RedHatInsights/insights-core/blob/master/insights/parsr/examples/logrotate_conf.py)

## Primitives
These are the building blocks for matching individual characters, sets of
characters, and a few convenient objects like numbers. All matching is case
sensitive except for the `ignore_case` option with `Literal`.

### Char
Match a single character.
```python
a = Char("a")     # parses a single "a"
val = a("a")      # produces an "a" from the data.
val = a("b")      # raises an exception
```

### InSet
Match any single character in a set.
```python
vowel = InSet("aeiou")  # or InSet(set("aeiou"))
val = vowel("a")  # okay
val = vowel("e")  # okay
val = vowel("i")  # okay
val = vowel("o")  # okay
val = vowel("u")  # okay
val = vowel("y")  # raises an exception
```

### String
Match one or more characters in a set. Matching is greedy.
```python
vowels = String("aeiou")
val = vowels("a")            # returns "a"
val = vowels("u")            # returns "u"
val = vowels("aaeiouuoui")   # returns "aaeiouuoui"
val = vowels("uoiea")        # returns "uoiea"
val = vowels("oouieaaea")    # returns "oouieaaea"
val = vowels("ga")           # raises an exception
```

### Literal
Match a literal string. The `value` keyword lets you return a python value
instead of the matched input. The `ignore_case` keyword makes the match case
insensitive.
```python
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
```

### Number
Match a possibly negative integer or simple floating point number and return
the python `int` or `float` for it.
```python
val = Number("123")  # returns 123
val = Number("-12")  # returns -12
val = Number("12.4")  # returns 12.4
val = Number("-12.4")  # returns -12.4
```

parsr also provides SingleQuotedString, DoubleQuotedString, QuotedString, EOL,
EOF, WS, AnyChar, and several other primitives. See the bottom of
[parsr/\_\_init\_\_.py](https://github.com/RedHatInsights/insights-core/blob/master/insights/parsr/__init__.py)

## Combinators
There are several ways of combining primitives and their combinations.

### Sequence
Require expressions to be in order.

Sequences are optimized so only the first object maintains a list of itself and
following objects. Be aware that using a sequence in other sequences will cause
it to accumulate the elements of the new sequence onto it, which could affect it
if it's used in multiple definitions. To ensure a sequence isn't "sticky" after
its definition, wrap it in a `Wrapper` object.
```python
a = Char("a")     # parses a single "a"
b = Char("b")     # parses a single "b"
c = Char("c")     # parses a single "c"

ab = a + b        # parses a single "a" followed by a single "b"
                  # (a + b) creates a "Sequence" object. Using `ab` as an
                  # element in a later sequence would modify its original
                  # definition.

abc = a + b + c   # parses "abc"
                  # (a + b) creates a "Sequence" object to which c is appended

val = ab("ab")    # produces a list ["a", "b"]
val = ab("a")     # raises an exception
val = ab("b")     # raises an exception
val = ab("ac")    # raises an exception
val = ab("cb")    # raises an exception

val = abc("abc")  # produces ["a", "b", "c"]
```

### Choice
Accept one of several alternatives. Alternatives are checked from left to right,
and checking stops with the first one to succeed.

Choices are optimized so only the first object maintains a list of alternatives.
Be aware that using a choice object as an element in other choices will
cause it to accumulate the elemtents of the new choice onto it, which could
affect it if it's used in multiple definitions. To ensure a Choice isn't
"sticky" after its definition, wrap it in a `Wrapper` object.
```python
abc = a | b | c   # alternation or choice.
val = abc("a")    # parses a single "a"
val = abc("b")    # parses a single "b"
val = abc("c")    # parses a single "c"
val = abc("d")    # raises an exception
```

### Many
Match zero or more occurences of an expression. Matching is greedy.

Since `Many` can match zero occurences, it always succeeds. Keep this in mind
when using it in a list of alternatives or with `FollowedBy` or `NotFollowedBy`.
```python
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

ab = Many(a | b)  # parses any combination of "a" and "b" like "aababbaba..."
val = ab("aababb")# produces ["a", "a", "b", "a", "b", "b"]

bs = Many(Char("b"), lower=1) # requires at least one "b"
val = bs("b")     # produces ["b"]
val = bs("a")     # raises an Exception
```

### Until
Match zero or more occurences of an expression until a predicate matches.
Matching is greedy.

Since `Until` can match zero occurences, it always succeeds. Keep this in mind
when using it in a list of alternatives or with `FollowedBy` or `NotFollowedBy`.
```python
cs = AnyChar.until(Char("y")) # parses many (or no) characters until a "y" is
                              # encountered.

val = cs("")                  # returns []
val = cs("a")                 # returns ["a"]
val = cs("x")                 # returns ["x"]
val = cs("ccccc")             # returns ["c", "c", "c", "c", "c"]
val = cs("abcdycc")           # returns ["a", "b", "c", "d"]
```

### Followed by
Require an expression to be followed by another, but don't consume the input
that matches the latter expression.
```python
ab = Char("a") & Char("b") # matches an "a" followed by a "b", but the "b"
                           # isn't consumed from the input.
val = ab("ab")             # returns "a" and leaves "b" to be consumed.
val = ab("ac")             # raises an exception and doesn't consume "a".
```

### Not followed by
Require an expression to *not* be followed by another.
```python
anb = Char("a") / Char("b") # matches an "a" not followed by a "b".
val = anb("ac")             # returns "a" and leaves "c" to be consumed
val = anb("ab")             # raises an exception and doesn't consume "a".
```

### Keep Left / Keep Right
`KeepLeft` (`<<`) and `KeepRight` (`>>`) match adjacent expressions but ignore
one of their results.
```python
a = Char("a")
q = Char('"')

qa = a << q      # like a + q except only the result of a is returned
val = qa('a"')   # returns "a". Keeps the thing on the left of the << 

qa = q >> a      # like q + a except only the result of a is returned
val = qa('"a')   # returns "a". Keeps the thing on the right of the >> 

qa = q >> a << q # like q + a + q except only the result of the a is returned
val = qa('"a"')  # returns "a".
```

### Opt
`Opt` wraps a parser and returns a default value of `None` if it fails. That
value can be changed with the `default` keyword. Input is consumed if the
wrapped parser succeeds but not otherwise.
```python
a = Char("a")
o = Opt(a)      # matches an "a" if its available. Still succeeds otherwise but
                # doesn't advance the read pointer.
val = o("a")    # returns "a"
val = o("b")    # returns None. Read pointer is not advanced.

o = Opt(a, default="x") # matches an "a" if its available. Returns "x" otherwise.
val = o("a")    # returns "a"
val = o("b")    # returns "x". Read pointer is not advanced.
```

### map
All parsers have a `.map` function that allows you to pass a function to
evaluate the input they've matched.
```python
def to_number(val):
    # val is like [non_zero_digit, [other_digits]]
    first, rest = val
    s = first + "".join(rest)
    return int(s)

m = NonZeroDigit + Many(Digit)  # returns [nzd, [other digits]]
n = m.map(to_number)  # converts the match to an actual integer
val = n("15")  # returns the int 15
```

### Lift
Allows a multiple parameter function to work on parsers.
```python
def comb(a, b, c):
    return "".join([a, b, c])

# You'd normally invoke comb like comb("x", "y", "z"), but you can "lift" it for
# use with parsers like this:

x = Char("x")
y = Char("y")
z = Char("z")
p = Lift(comb) * x * y * z

# The * operator separates parsers whose results will go into the arguments of
# the lifted function. I've used Char above, but x, y, and z can be arbitrarily
# complex.

val = p("xyz")  # would return "xyz"
val = p("xyx")  # raises an exception. nothing would be consumed
```

### Forward
`Forward` allows recursive grammars where a nonterminal's definition includes
itself directly or indirectly. You initially create a `Forward` nonterminal
with regular assignment.
```python
expr = Forward()
```

You later give it its real definition with the `<=` operator.
```python
expr <= (term + Many(LowOps + term)).map(op)
```

### Arithmetic
Here's an arithmetic parser that ties several concepts together. A progression
of this parser from a simple imperative style to what you see below is in the
[original project repo](https://github.com/csams/parsr/blob/master/parsr/lesson).

```python
from parsr import EOF, Forward, InSet, LeftParen, Many, Number, RightParen, WS


def op(args):
    ans, rest = args
    for op, arg in rest:
        if op == "+":
            ans += arg
        elif op == "-":
            ans -= arg
        elif op == "*":
            ans *= arg
        elif op == "/":
            ans /= arg
    return ans


# high precedence operations
HighOps = InSet("*/")

# low precedence operations
LowOps = InSet("+-")

# Operator precedence is handled by having different declarations for each
# prededence level. expr handles low level operations, term handles high level
# operations, and factor handles simple numbers or subexpressions between
# parentheses. Since the first element in expr is term and the first element in
# term is factor, factors are evaluated first, then terms, and then exprs.

# We have to declare expr before its definition since it's used recursively
# through the definition of factor.
expr = Forward()

# A factor is a simple number or a subexpression between parentheses.
factor = WS >> (Number | (LeftParen >> expr << RightParen)) << WS

# A term handles strings of multiplication and division. As written, it would
# convert "1 + 2 - 3 + 4" into [1, [['+', 2], ['-', 3], ['+', 4]]]. The first
# element in the outer list is the initial factor. The second element of the
# outer list is another list, which is the result of the Many. The Many's list
# contains several two-element lists generated from each match of
# (HighOps + factor). We pass the entire structure into the op function with
# map.
term = (factor + Many(HighOps + factor)).map(op)

# expr has the same form and behavior as term.
# Notice that we assign to expr with "<=" instead of "=". This is how you assign
# to nonterminals that have been declared previously as Forward.
expr <= (term + Many(LowOps + term)).map(op)

val = expr("2*(3+4)/3+4")  # returns 8.666666666666668
```
