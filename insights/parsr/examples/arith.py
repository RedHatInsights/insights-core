"""
Simple arithmetic with usual operator precedence and associativity. It allows
addition, subtraction, multiplication, division, and grouping with parentheses.
"""
from insights.parsr import (EOF, Forward, InSet, LeftParen, Many, Number,
        RightParen, WS)


def evaluate(e):
    return Top(e)


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
#
# The Top declaration ensures that the entire input is valid with no extra data
# at the end.

# We have to declare expr before its definition since it's used recursively.
expr = Forward()


# A factor is a simple number or a subexpression between parentheses
factor = (WS >> (Number | (LeftParen >> expr << RightParen)) << WS) % "factor"

# A term handles strings of multiplication and division. As written, it would
# convert "1 + 2 - 3 + 4" into [1, [['+', 2], ['-', 3], ['+', 4]]]. The first
# element in the outer list is the initial factor. The second element of the
# outer list is another list, which is the result of the Many. The Many's list
# contains several two-element lists generated from each match of
# (HighOps + factor). We pass the entire structure into the op function with
# map.
term = (factor + Many(HighOps + factor)).map(op) % "term"

# expr has the same form as term.
expr <= (term + Many(LowOps + term)).map(op) % "expr"

# Top returns [result, None] on success and raises an Exception on failure.
Top = expr << EOF
