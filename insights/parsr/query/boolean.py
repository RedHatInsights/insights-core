"""
The boolean module allows delayed evaluation of boolean expressions. You wrap
predicates in objects that have overloaded operators so they can be connected
symbolically to express ``and``, ``or``, and ``not``. This is useful if you
want to build up a complicated predicate and pass it to something else for
evaluation, in particular :py:class:`insights.parsr.query.Entry` instances.

    .. code-block:: python

        def is_even(n):
            return (n % 2) == 0

        def is_positive(n):
            return n > 0

        even_and_positive = pred(is_even) & pred(is_positive)

        even_and_positive(6) == True
        even_and_positive(-2) == False
        even_and_positive(3) == False

You can also convert two parameter functions to which you want to partially
apply an argument. The arguments partially applied will be those *after* the
first argument. The first argument is the value the function should evaluate
when it's fully applied.

    .. code-block:: python

        import operator
        lt = pred2(operator.lt)  # operator.lt is lt(a, b) == (a < b)
        gt = pred2(operator.gt)  # operator.gt is gt(a, b) == (a > b)

        gt_five = gt(5)  # creates a function of one argument that when called
                         # returns operator.gt(x, 5)

        lt_ten = lt(10)  # creates a function of one argument that when called
                         # returns operator.lt(x, 5)

        gt_five_and_lt_10 = gt(5) & lt(10)

"""


class Boolean(object):
    def __and__(self, other):
        return All(self, other)

    def __or__(self, other):
        return Any(self, other)

    def __invert__(self):
        return Not(self)

    def test(self, value):
        return True

    def __call__(self, value):
        return self.test(value)


class TRUE(Boolean):
    pass


class FALSE(Boolean):
    def test(self, value):
        return False


class Any(Boolean):
    def __init__(self, *exprs):
        self.exprs = list(exprs)

    def test(self, value):
        return any(q.test(value) for q in self.exprs)


class All(Boolean):
    def __init__(self, *exprs):
        self.exprs = list(exprs)

    def test(self, value):
        return all(q.test(value) for q in self.exprs)


class Not(Boolean):
    def __init__(self, query):
        self.query = query

    def test(self, value):
        return not self.query.test(value)


class Predicate(Boolean):
    def __init__(self, func, *args):
        self.func = func
        self.args = args

    def test(self, value):
        try:
            return self.func(value, *self.args)
        except Exception:
            return False


class CaselessPredicate(Predicate):
    def test(self, lhs):
        if isinstance(lhs, str):
            return super(CaselessPredicate, self).test(lhs.lower())
        return super(CaselessPredicate, self).test(lhs)


def pred(func, ignore_case=False):
    if ignore_case:
        return CaselessPredicate(func)
    return Predicate(func)


def pred2(func, ignore_case=False):
    def inner(val):
        if ignore_case:
            return CaselessPredicate(func, val.lower())
        return Predicate(func, val)
    return inner


Or = Any
And = All
TRUE = TRUE()
FALSE = FALSE()
