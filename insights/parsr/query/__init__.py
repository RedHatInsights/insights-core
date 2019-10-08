"""
insights.parsr.query defines a common data model and query language for parsers
created with ``insights.parsr`` to target.

The model allows duplicate keys, and it allows values with *unnamed* attributes
and recursive substructure. This is a common model for many kinds of
configuration.

Simple key/value pairs can be represented as a key with a value that has a
single attribute. Most dictionary shapes used to represent configuration are
made of keys with simple values (key/single attr), lists of simple values
(key/multiple attrs), or nested dictionaries (key/substructure).

Something like XML allows duplicate keys, and it allows values to have named
attributes and substructure. This module doesn't cover that case.

:py:class:`Entry`, :py:class:`Directive`, :py:class:`Section`, and
:py:class:`Result` have overloaded ``__getitem__`` functions that respond to
queries. This allows their instances to be accessed like simple dictionaries,
but the key passed to ``[]`` is converted to a query of immediate child
instances instead of a simple lookup.
"""
import operator
from functools import partial
from itertools import chain
from insights.parsr.query.boolean import All, Any, Boolean, lift, lift2, TRUE


def pretty_format(root, indent=4):
    """
    pretty_format generates a text representation of a model as a list of
    lines.
    """
    results = []

    def sep():
        if results and results[-1] != "":
            results.append("")

    def inner(d, prefix=""):
        if isinstance(d, Result):
            for c in d.children:
                inner(c, prefix)
            return
        if d.children:
            sep()
            name = d.name or ""
            header = name if not d.attrs else " ".join([name, d.string_value])
            if header:
                results.append(prefix + "[" + header + "]")
            prep = prefix + (" " * indent)
            for c in d.children:
                inner(c, prep)
            sep()
        else:
            results.append(prefix + (d.name or "") + ": " + d.string_value)

    inner(root)
    return results


class Entry(object):
    """
    Entry is the base class for the data model, which is a tree of Entry
    instances. Each instance has a name, attributes, a parent, and children.
    """

    __slots__ = ("_name", "attrs", "children", "parent", "lineno", "src")

    def __init__(self, name=None, attrs=None, children=None, lineno=None, src=None):
        self._name = name
        self.attrs = attrs or []
        self.children = children or []
        self.parent = None
        self.lineno = lineno
        self.src = src
        for c in self.children:
            c.parent = self
        super(Entry, self).__init__()

    def __getattr__(self, name):
        """
        Allows queries based on attribute access so long as they don't conflict
        with members of the Entry class itself.
        """
        if name == "name" and self._name is not None:
            return self._name

        res = self[name]
        if res:
            return res

        # fall through for stuff like file_path, etc.
        if hasattr(self.src, name):
            return getattr(self.src, name)

        return res

    def get_keys(self):
        """
        Returns the unique names of all the children as a list.
        """
        return sorted(set(c.name for c in self.children))

    def __dir__(self):
        return self.get_keys() + object.__dir__(self)

    @property
    def line(self):
        """
        Returns the original first line of text that generated the ``Entry``.
        """
        if self.src is not None:
            return self.src.content[self.lineno - 1]

    @property
    def string_value(self):
        """
        Returns the string representation of all attributes separated by a
        single whilespace.
        """
        t = " ".join(["%s"] * len(self.attrs))
        return t % tuple(self.attrs)

    @property
    def value(self):
        """
        Returns ``None`` if no attributes exist, the first attribute if only
        one exists, or the ``string_value`` if more than one exists.
        """
        if len(self.attrs) == 1:
            return self.attrs[0]
        return self.string_value if len(self.attrs) > 1 else None

    @property
    def root(self):
        """
        Returns the furthest ancestor ``Entry``.
        """
        p = self
        while p.parent is not None:
            p = p.parent
        return p

    @property
    def roots(self):
        """
        Returns the furthest ancestor ``Entry``.
        """
        return Result(children=list(set(c.root for c in self.children)))

    @property
    def grandchildren(self):
        """
        Returns a flattened list of all grandchildren.
        """
        return list(chain.from_iterable(c.children for c in self.children))

    def select(self, *queries, **kwargs):
        """
        select uses :py:func:`compile_queries` to compile ``queries`` into a
        query function and then passes the function, the current ``Entry``
        instances children, and ``kwargs`` on to :py:func:`select`.
        """
        query = compile_queries(*queries)
        return select(query, self.children, **kwargs)

    def find(self, *queries, **kwargs):
        """
        Finds matching results anywhere in the configuration. The arguments are
        the same as those accepted by :py:func:`compile_queries`, and it
        accepts a keyword called ``roots`` that will return the ultimate root
        nodes of any results.
        """
        roots = kwargs.get("roots", False)
        return self.select(*queries, deep=True, roots=roots)

    def where(self, name, value=None):
        """
        Selects current nodes based on name and value queries of child nodes.
        If any immediate children match the queries, the parent is included in
        the results. The :py:func:``make_child_query`` function can be used to
        construct queries that act on the children as a whole instead of one
        at a time.

        Example:
        >>> from insights.parsr.query import make_child_query as q
        >>> from insights.parsr.query import from_dict
        >>> r = from_dict(load_config())
        >>> r = conf.status.conditions.where(q("status", "False") | q("type", "Progressing"))
        >>> r.message
        >>> r = conf.status.conditions.where(q("status", "False") | q("type", "Progressing"))
        >>> r.message
        >>> r.lastTransitionTime.values
        ['2019-08-04T23:17:08Z', '2019-08-04T23:32:14Z']
        """
        query = make_child_query(name, value) if not isinstance(name, DictQueryBase) else name
        return Result(children=self.children if query.test(self) else [])

    @property
    def section(self):
        return None

    @property
    def section_name(self):
        return None

    @property
    def sections(self):
        """
        Returns all immediate children that are instances of
        :py:class:`Section`.
        """
        return Result(children=[c for c in self.children if isinstance(c, Section)])

    @property
    def directives(self):
        """
        Returns all immediate children that are instances of
        :py:class:`Directive`.
        """
        return Result(children=[c for c in self.children if isinstance(c, Directive)])

    def __contains__(self, key):
        return len(self[key]) > 0

    def __len__(self):
        return len(self.children)

    def __getitem__(self, query):
        if isinstance(query, (int, slice)):
            return self.children[query]
        query = _desugar(query)
        return Result(children=[c for c in self.children if query.test(c)])

    def __bool__(self):
        return bool(self._name or self.attrs or self.children)

    def __repr__(self):
        return "\n".join(pretty_format(self))

    __nonzero__ = __bool__


class Section(Entry):
    """
    A Section is an ``Entry`` composed of other Sections and
    :py:class:`Directive` instances.
    """
    @property
    def section(self):
        """
        Returns the name of the section.
        """
        return self.name

    @property
    def section_name(self):
        """
        Returns the value of the section.
        """
        return self.value


class Directive(Entry):
    """
    A Directive is an ``Entry`` that represents a single option or named value.
    They are normally found in :py:class:`Section` instances.
    """
    @property
    def section(self):
        if self.parent:
            return self.parent.section

    @property
    def section_name(self):
        if self.parent:
            return self.parent.section_name


class Result(Entry):
    """
    Result is an Entry whose children are the results of a query.
    """
    def __init__(self, children=None):
        super(Result, self).__init__()
        self.children = children or []

    def get_keys(self):
        """
        Returns the unique names of all the grandchildren as a list.
        """
        return sorted(set(c.name for c in self.grandchildren))

    @property
    def string_value(self):
        """
        Returns the string value of the child if only one child exists. This
        helps queries behave more like dictionaries when you know only one
        result should exist.
        """
        if len(self.children) == 1:
            return self.children[0].string_value
        raise Exception("More than one value to return.")

    @property
    def value(self):
        """
        Returns the value of the child if only one child exists. This helps
        queries behave more like dictionaries when you know only one result
        should exist.
        """
        if len(self.children) == 0:
            return None

        if len(self.children) == 1:
            return self.children[0].value

        raise Exception("More than one value to return.")

    @property
    def parents(self):
        """
        Returns the values of all the children as a list.
        """
        return Result(children=[c.parent for c in self.children])

    @property
    def values(self):
        """
        Returns the values of all the children as a list.
        """
        return [c.value for c in self.children]

    @property
    def unique_values(self):
        """
        Returns the values of all the children as a list.
        """
        return sorted(set(c.value for c in self.children))

    def select(self, *queries, **kwargs):
        query = compile_queries(*queries)
        return select(query, self.grandchildren, **kwargs)

    def where(self, name, value=None):
        """
        Selects current nodes based on name and value queries of child nodes.
        If any immediate children match the queries, the parent is included in
        the results. The :py:func:``make_child_query`` function can be used to
        construct queries that act on the children as a whole instead of one
        at a time.

        Example:
        >>> from insights.parsr.query import make_child_query as q
        >>> from insights.parsr.query import from_dict
        >>> r = from_dict(load_config())
        >>> r = conf.status.conditions.where(q("status", "False") | q("type", "Progressing"))
        >>> r.message
        >>> r = conf.status.conditions.where(q("status", "False") | q("type", "Progressing"))
        >>> r.message
        >>> r.lastTransitionTime.values
        ['2019-08-04T23:17:08Z', '2019-08-04T23:32:14Z']
        """
        query = make_child_query(name, value) if not isinstance(name, DictQueryBase) else name
        return Result(children=list(set(c for c in self.children if query.test(c))))

    def __getitem__(self, query):
        if isinstance(query, (int, slice)):
            return self.children[query]
        query = _desugar(query)
        return Result(children=[c for c in self.grandchildren if query.test(c)])


class _EntryQuery(object):
    """
    _EntryQuery is the base class of all other query classes.
    """
    def __init__(self, expr):
        super(_EntryQuery, self).__init__()
        self.expr = expr

    def test(self, node):
        return self.expr.test(node)


class NameQuery(_EntryQuery):
    """
    A query against the name of an :py:class:`Entry`.
    """
    def test(self, node):
        return self.expr.test(node.name)


class AttrQuery(_EntryQuery):
    """
    A query against an attribute of an :py:class:`Entry`.
    """
    def __and__(self, other):
        return _AndAttrQuery(self, other)

    def __or__(self, other):
        return _OrAttrQuery(self, other)

    def __invert__(self):
        return _NotAttrQuery(self)


class _AndAttrQuery(AttrQuery):
    def __init__(self, *exprs):
        self.exprs = list(exprs)

    def test(self, n):
        return all(expr.test(n) for expr in self.exprs)

    def __and__(self, other):
        self.exprs.append(other)
        return self


class _OrAttrQuery(AttrQuery):
    def __init__(self, *exprs):
        self.exprs = list(exprs)

    def test(self, n):
        return any(expr.test(n) for expr in self.exprs)

    def __or__(self, other):
        self.exprs.append(other)
        return self


class _NotAttrQuery(AttrQuery):
    def __init__(self, query):
        self.query = query

    def test(self, n):
        return not self.query.test(n)


class _AllAttrQuery(AttrQuery):
    def test(self, n):
        return all(self.expr.test(a) for a in n.attrs)


class _AnyAttrQuery(AttrQuery):
    def test(self, n):
        return any(self.expr.test(a) for a in n.attrs)


def any_(expr):
    """
    Use to express that ``expr`` can succeed on any attribute for the query to be
    successful. Only works against :py:class:`Entry` attributes.
    """
    return _AnyAttrQuery(_desugar_attr(expr))


def all_(expr):
    """
    Use to express that ``expr`` must succeed on all attributes for the query
    to be successful. Only works against :py:class:`Entry` attributes.
    """
    return _AllAttrQuery(_desugar_attr(expr))


def _desugar_name(q):
    if q is None:
        return NameQuery(TRUE)
    if isinstance(q, NameQuery):
        return q
    if isinstance(q, Boolean):
        return NameQuery(q)
    if callable(q):
        return NameQuery(lift(q))
    return NameQuery(lift(partial(operator.eq, q)))


def _desugar_attr(q):
    if isinstance(q, Boolean):
        return q
    if callable(q):
        return lift(q)
    return lift(partial(operator.eq, q))


def _desugar_attrs(q):
    if not q:
        return
    if len(q) == 1:
        q = q[0]
        return q if isinstance(q, AttrQuery) else _AnyAttrQuery(_desugar_attr(q))
    else:
        attr_queries = [_desugar_attr(a) for a in q]
        return _AnyAttrQuery(Any(*attr_queries))


def _desugar(q):
    if isinstance(q, DictQueryBase):
        return q
    if isinstance(q, tuple):
        q = list(q)
        name_query = _desugar_name(q[0])
        attrs_query = _desugar_attrs(q[1:])
        if attrs_query:
            return All(name_query, attrs_query)
        return name_query
    return _desugar_name(q)


class DictQueryBase(object):
    """
    Base class for queries that target all children of a node as once.
    """
    def __init__(self, expr):
        self.expr = expr

    def __or__(self, other):
        return DictOr(self, other)

    def __and__(self, other):
        return DictAnd(self, other)

    def __invert__(self):
        return DictNot(self)


class DictQuery(DictQueryBase):
    """
    Returns True if any child node passes the query.
    """
    def test(self, node):
        return any(self.expr.test(n) for n in node.children)


class DictNot(DictQueryBase):
    def test(self, node):
        return not self.expr.test(node)


class DictAnd(DictQueryBase):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def test(self, node):
        return self.left.test(node) and self.right.test(node)


class DictOr(DictQueryBase):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def test(self, node):
        return self.left.test(node) or self.right.test(node)


def make_child_query(name, value=None):
    """
    Converts a query into a DictQuery that works on all child nodes at once
    to determine if the current node is accepted.
    """
    q = _desugar((name, value) if value is not None else name)
    return DictQuery(q)


def _flatten(nodes):
    def inner(n):
        res = [n]
        res.extend(chain.from_iterable(inner(c) for c in n.children))
        return res
    return list(chain.from_iterable(inner(n) for n in nodes))


def compile_queries(*queries):
    """
    compile_queries returns a function that will execute a list of query
    expressions against an :py:class:`Entry`. The first query is run against
    the current entry's children, the second query is run against the children
    of the children remaining from the first query, and so on.

    If a query is a single object, it matches against the name of an Entry. If
    it's a tuple, the first element matches against the name, and subsequent
    elements are tried against each individual attribute. The attribute results
    are `or'd` together and that result is `anded` with the name query. Any
    query that raises an exception is treated as ``False``.
    """
    def match(qs, nodes):
        q = _desugar(qs[0])
        res = [n for n in nodes if q.test(n)]
        qs = qs[1:]
        if qs:
            gc = list(chain.from_iterable(n.children for n in res))
            return match(qs, gc)
        return res

    def inner(nodes):
        return Result(children=match(queries, nodes))
    return inner


def select(query, nodes, deep=False, roots=None):
    """
    select runs query, a function returned by :py:func:`compile_queries`,
    against a list of :py:class:`Entry` instances. If you pass ``deep=True``,
    select recursively walks each entry in the list and accumulates the
    results of running the query against it. If you pass ``roots=True``,
    select returns the deduplicated set of final ancestors of all successful
    queries. Otherwise, it returns the matching entries.
    """
    results = query(_flatten(nodes)) if deep else query(nodes)

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


def from_dict(orig):
    """
    from_dict is a helper function that does its best to convert a python dict
    into a tree of :py:class:`Entry` instances that can be queried.
    """

    def inner(d):
        result = []
        for k, v in d.items():
            if isinstance(v, dict):
                result.append(Entry(name=k, children=inner(v)))
            elif isinstance(v, list):
                res = [Entry(name=k, children=inner(i)) if isinstance(i, dict) else i for i in v]
                if res:
                    if isinstance(res[0], Entry):
                        result.extend(res)
                    else:
                        result.append(Entry(name=k, attrs=res))
                else:
                    result.append(Entry(name=k, attrs=[]))
            else:
                result.append(Entry(name=k, attrs=[v]))
        return result
    return Entry(children=inner(orig))


# These are operators that can be used inside of queries.
lt = lift2(operator.lt)
le = lift2(operator.le)
eq = lift2(operator.eq)
gt = lift2(operator.gt)
ge = lift2(operator.ge)


def isin(v, values):
    return v in set(values)


isin = lift2(isin)

contains = lift2(operator.contains)
startswith = lift2(str.startswith)
endswith = lift2(str.endswith)

ieq = lift2(operator.eq, ignore_case=True)
icontains = lift2(operator.contains, ignore_case=True)
istartswith = lift2(str.startswith, ignore_case=True)
iendswith = lift2(str.endswith, ignore_case=True)

first = 0
last = -1
