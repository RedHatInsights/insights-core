"""
This module allows parsers to construct data with a common representation that
is compatible with insights.parsr.query.

The model allows duplicate keys, and it allows values with *unnamed* attributes
and recursive substructure. This is a common model for many kinds of
configuration.

Simple key/value pairs can be represented as a key with a value that has a
single attribute. Most dictionary shapes used to represent configuration are
made of keys with simple values (key/single attr), lists of simple values
(key/multiple attrs), or nested dictionaries (key/substructure).

Something like XML allows duplicate keys, and it allows values to have named
attributes and substructure. This module doesn't cover that case.

`Entry` and `Result` have overloaded __getitem__ functions that respond to
queries from the insights.parsr.query module. This allows their instances to be
accessed like simple dictionaries, but the key passed to `[]` is converted to a
query of immediate child instances instead of a simple lookup.
"""
import operator
from functools import partial
from itertools import chain
from insights.parsr.query.boolean import All, Any, Boolean, lift, lift2, TRUE


def pretty_format(root, indent=4):
    results = []

    def sep():
        if results and results[-1] != "":
            results.append("")

    def inner(d, prefix=""):
        if isinstance(d, Directive):
            results.append(prefix + d.name + ": " + d.string_value)
        elif isinstance(d, Section):
            sep()
            header = d.name if not d.attrs else " ".join([d.name, d.string_value])
            results.append(prefix + "[" + header + "]")
            prep = prefix + (" " * indent)
            for c in d.children:
                inner(c, prep)
            sep()
        else:
            for c in d.children:
                inner(c, prefix)

    inner(root)
    return results


class Entry(object):
    def __init__(self, name=None, attrs=None, children=None, lineno=None, src=None):
        self.name = name
        self.attrs = attrs or []
        self.children = children or []
        self.parent = None
        self.lineno = lineno
        self.src = src
        for c in self.children:
            c.parent = self

    def __getattr__(self, name):
        return getattr(self.src, name)

    @property
    def line(self):
        if self.src is not None:
            return self.src.content[self.lineno - 1]

    @property
    def string_value(self):
        t = " ".join(["%s"] * len(self.attrs))
        return t % tuple(self.attrs)

    @property
    def value(self):
        if len(self.attrs) == 1:
            return self.attrs[0]
        return self.string_value if len(self.attrs) > 1 else None

    @property
    def root(self):
        p = self
        while p.parent is not None and p.parent.parent is not None:
            p = p.parent
        return p

    @property
    def grandchildren(self):
        return list(chain.from_iterable(c.children for c in self.children))

    def select(self, *queries, **kwargs):
        query = compile_queries(*queries)
        return select(query, self.children, **kwargs)

    def find(self, *queries, **kwargs):
        """
        Finds matching results anywhere in the configuration
        """
        roots = kwargs.get("roots", False)
        return self.select(*queries, deep=True, roots=roots)

    @property
    def section(self):
        return None

    @property
    def section_name(self):
        return None

    @property
    def sections(self):
        return Result(children=[c for c in self.doc.children if isinstance(c, Section)])

    @property
    def directives(self):
        return Result(children=[c for c in self.doc.children if isinstance(c, Directive)])

    def __contains__(self, key):
        return len(self[key]) > 0

    def __len__(self):
        return len(self.children)

    def __getitem__(self, query):
        if isinstance(query, (int, slice)):
            return self.children[query]
        query = desugar(query)
        return Result(children=[c for c in self.children if query.test(c)])

    def __bool__(self):
        return bool(self.name or self.attrs or self.children)

    def __repr__(self):
        return "\n".join(pretty_format(self))

    __nonzero__ = __bool__


class Section(Entry):
    @property
    def section(self):
        return self.name

    @property
    def section_name(self):
        return self.value


class Directive(Entry):
    @property
    def section(self):
        if self.parent:
            return self.parent.section

    @property
    def section_name(self):
        if self.parent:
            return self.parent.section_name


class Result(Entry):
    def __init__(self, children=None):
        super(Result, self).__init__()
        self.children = children or []

    @property
    def string_value(self):
        if len(self.children) == 1:
            return self.children[0].string_value
        raise Exception("More than one value to return.")

    @property
    def value(self):
        if len(self.children) == 1:
            return self.children[0].value
        raise Exception("More than one value to return.")

    def select(self, *queries, **kwargs):
        query = compile_queries(*queries)
        return select(query, self.grandchildren, **kwargs)

    def __getitem__(self, query):
        if isinstance(query, (int, slice)):
            return self.children[query]
        query = desugar(query)
        return Result(children=[c for c in self.grandchildren if query.test(c)])


def from_dict(orig):
    def inner(d):
        result = []
        for k, v in d.items():
            if isinstance(v, dict):
                result.append(Entry(name=k, children=inner(v)))
            elif isinstance(v, list):
                res = [from_dict(i) if isinstance(i, dict) else i for i in v]
                if res:
                    if isinstance(res[0], Entry):
                        result.append(Entry(name=k, children=res))
                    else:
                        result.append(Entry(name=k, attrs=res))
                else:
                    result.append(Entry(name=k))
            else:
                result.append(Entry(name=k, attrs=[v]))
        return result
    return Entry(children=inner(orig))


class EntryQuery(object):
    def __init__(self, expr):
        self.expr = expr

    def test(self, node):
        return self.expr.test(node)


class NameQuery(EntryQuery):
    def test(self, node):
        return self.expr.test(node.name)


class AttrQuery(EntryQuery):
    pass


class AllAttrQuery(AttrQuery):
    def test(self, n):
        return all(self.expr.test(a) for a in n.attrs)


class AnyAttrQuery(AttrQuery):
    def test(self, n):
        return any(self.expr.test(a) for a in n.attrs)


def any_(*exprs):
    return AnyAttrQuery(Any(*[desugar_attr(e) for e in exprs]))


def all_(*exprs):
    return AllAttrQuery(All(*[desugar_attr(e) for e in exprs]))


def desugar_name(q):
    if q is None:
        return NameQuery(TRUE)
    if isinstance(q, NameQuery):
        return q
    if isinstance(q, Boolean):
        return NameQuery(q)
    if callable(q):
        return NameQuery(lift(q))
    return NameQuery(lift(partial(operator.eq, q)))


def desugar_attr(q):
    if isinstance(q, Boolean):
        return q
    if callable(q):
        return lift(q)
    return lift(partial(operator.eq, q))


def desugar_attrs(q):
    if not q:
        return
    if len(q) == 1:
        q = q[0]
        return q if isinstance(q, AttrQuery) else AnyAttrQuery(desugar_attr(q))
    else:
        attr_queries = [desugar_attr(a) for a in q[1:]]
        return AnyAttrQuery(Any(*attr_queries))


def desugar(q):
    if isinstance(q, tuple):
        q = list(q)
        name_query = desugar_name(q[0])
        attrs_query = desugar_attrs(q[1:])
        if attrs_query:
            return All(name_query, attrs_query)
        return name_query
    return desugar_name(q)


def flatten(nodes):
    def inner(n):
        res = [n]
        res.extend(chain.from_iterable(inner(c) for c in n.children))
        return res
    return list(chain.from_iterable(inner(n) for n in nodes))


def compile_queries(*queries):
    def match(qs, nodes):
        q = desugar(qs[0])
        res = [n for n in nodes if q.test(n)]
        qs = qs[1:]
        if qs:
            gc = list(chain.from_iterable(n.children for n in res))
            return match(qs, gc)
        return res

    def inner(nodes):
        return Result(children=match(queries, nodes))
    return inner


def select(query, nodes, deep=False, roots=False):
    results = query(flatten(nodes)) if deep else query(nodes)

    if not roots:
        return Result(children=results)

    seen = set()
    top = []
    for r in results:
        root = r.root
        if root not in seen:
            seen.add(root)
            top.append(root)
    return Result(children=top)


lt = lift2(operator.lt)
le = lift2(operator.le)
eq = lift2(operator.eq)
gt = lift2(operator.gt)
ge = lift2(operator.ge)

contains = lift2(operator.contains)
startswith = lift2(str.startswith)
endswith = lift2(str.endswith)

ieq = lift2(operator.eq, ignore_case=True)
icontains = lift2(operator.contains, ignore_case=True)
istartswith = lift2(str.startswith, ignore_case=True)
iendswith = lift2(str.endswith, ignore_case=True)

first = 0
last = -1
