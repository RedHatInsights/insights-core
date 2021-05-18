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
import re
import six
import sys
from collections import defaultdict
from itertools import chain, count
from insights.parsr.query.boolean import All, Any, Boolean, Not, pred, pred2  # noqa

# intern was a builtin until it moved to sys in python3
try:
    intern = sys.intern
except:
    pass


def _make_str(s):
    """
    Inspired by six.ensure_str in six version 1.15. See the six module for
    copyright notice.
    """
    if six.PY2 and isinstance(s, six.text_type):
        return s.encode("utf-8", "strict")
    if six.PY3 and isinstance(s, six.binary_type):
        return s.decode("utf-8", "strict")
    return s


# we need this when generating crumbs
try:
    isidentifier = str.isidentifier
except:
    isidentifier = re.compile(r"^[^\d\W]\w*\Z").match


try:
    from collections import Counter
except ImportError:
    from operator import itemgetter

    class Counter(object):
        def __init__(self, data):
            self.data = defaultdict(int)
            self.update(data)

        def update(self, data):
            for d in data:
                self.data[d] += 1

        def most_common(self, top=None):
            res = sorted(self.data.items(), key=itemgetter(1), reverse=True)
            return res[:top] if top is not None else res

ANY = None


class Entry(object):
    """
    Entry is the base class for the data model, which is a tree of Entry
    instances. Each instance has a name, attributes, a parent, and children.
    """
    __slots__ = ("_name", "attrs", "children", "parent", "lineno", "src")

    def __init__(self, name=None, attrs=None, children=None, lineno=None, src=None, set_parents=True):
        if type(name) is str:
            self._name = intern(name)
        elif isinstance(name, (six.text_type, six.binary_type)):
            self._name = intern(_make_str(name))
        else:
            self._name = name

        self.attrs = attrs if isinstance(attrs, (list, tuple)) else tuple()
        self.children = children if isinstance(children, (list, tuple)) else []
        self.parent = None
        self.lineno = lineno
        self.src = src  # insights.core.Parser instance
        if set_parents:
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
        return sorted(set(c._name for c in self.children if c._name))

    keys = get_keys

    def __dir__(self):
        """
        Exists for ipython autocompletion.
        """
        return self.get_keys() + object.__dir__(self)

    @property
    def source(self):
        p = self
        while p is not None and p.src is None:
            p = p.parent

        if p is not None and p.src is not None:
            return getattr(p.src, "file_path", p.src)

    def _crumbs_up(self):
        res = []
        segments = []
        cur = self
        while cur is not None:
            name = cur._name
            if name is not None:
                segments.append(name)
            cur = cur.parent

        if len(segments) == 0:
            res.append("")
        elif len(segments) == 1:
            res.append(segments[0])
        else:
            segments = list(reversed(segments))
            path = [segments[0]]
            for r in segments[1:]:
                r = "." + r if isidentifier(r) else '["{n}"]'.format(n=r)
                path.append(r)
            res.append("".join(path))
        return res

    def _crumbs_down(self):
        res = set()

        def inner(node, base):
            if node.children:
                for c in node.children:
                    name = str(c._name) or ""
                    if base:
                        if not isidentifier(name):
                            name = '"{n}"'.format(n=name)
                            path = base + "[" + name + "]"
                        else:
                            path = base + "." + name
                    else:
                        if not isidentifier(name):
                            name = '"{n}"'.format(n=name)
                            path = "[" + name + "]"
                        else:
                            path = name
                    inner(c, path)
            else:
                res.add(base)

        inner(self, "")
        return sorted(res)

    def get_crumbs(self, down=False):
        """
        Get the unique paths from the current entry up to the root or down
        to all of the leaves.
        """
        return self._crumbs_up() if not down else self._crumbs_down()

    crumbs = get_crumbs

    @property
    def line(self):
        """
        Returns the original first line of text that generated the ``Entry``.
        ``None`` if the model wasn't generated by an insights parser.
        """
        if self.src is not None and self.lineno is not None:
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
        Returns the furthest ancestor ``Entry``. If the node is already the
        furthest ancestor, ``None`` is returned.
        """
        p = self.parent
        while p is not None and p.parent is not None:
            p = p.parent
        return p

    @property
    def grandchildren(self):
        """
        Returns a flattened list of all grandchildren.
        """
        return list(chain.from_iterable(c.children for c in self.children))

    def upto(self, query):
        """
        Go up from the current node to the first node that matches query.
        """
        predicate = _desugar(query)
        parent = self.parent
        while parent is not None:
            if predicate(parent):
                return parent
            parent = parent.parent

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
        if isinstance(name, _EntryQuery):
            query = name.to_pyfunc()
        elif isinstance(name, Boolean):
            query = child_query(name, value).to_pyfunc()
        elif callable(name):
            def predicate(e):
                try:
                    return name(e)
                except:
                    return False
            query = predicate
        else:
            query = child_query(name, value).to_pyfunc()
        return Result(children=self.children if query(self) else [])

    def choose(self, chooser):
        """
        Run a selector function on each node. It should return a tuple, each
        element of which is some query using the node. This lets you select
        parts of each tree in a result.

        If you want to rename a field, make the element a dictionary whose
        key is the name you want and whose value is the query.

        If you want to get all the children of a particular node instead of
        specifying them individually, use the * operator in python 3.5+ or
        return the query with ".grandchildren" appended otherwise.

        Example:
        >>> from insights.parsr.query import make_child_query as q
        >>> from insights.parsr.query import from_dict

        >>> conf = from_dict(load_config())
        >>> p = (q("restartCount", gt(2)) & q("ready", False))

        >>> # get the name, the restartCount renamed to restart, the podIP
        >>> # from the node's parent, and all of the children from
        >>> # n.lastState.terminated.

        >>> # for python 3.5+
        >>> sel = lambda n: (n["name"], {"restart": n.restartCount}, n.parent.podIP, *n.lastState.terminated)

        >>> # for python 2
        >>> sel = lambda n: (n["name"], {"restart": n.restartCount}, n.parent.podIP, n.lastState.terminated.grandchildren)

        >>> conf.find(ANY).where(p).choose(sel)
        """
        results = []
        for c in self.children:
            res = chooser(c)
            res = res if isinstance(res, (list, tuple)) else (res,)
            tmp = []
            for r in res:
                if isinstance(r, dict):
                    for k, v in r.items():
                        if isinstance(v, list):
                            tmp.append(Entry(k, children=v, set_parents=False))
                        elif isinstance(v, Entry):
                            for i in v.children:
                                tmp.append(Entry(k, i.attrs, i.children, set_parents=False))
                        else:
                            tmp.append(Entry(k, attrs=(v,), set_parents=False))
                else:
                    if isinstance(r, list):
                        tmp.extend(r)
                    else:
                        if isinstance(r, _Choose):
                            tmp.extend(r.grandchildren)
                        else:
                            tmp.extend(r.children)
            if tmp:
                results.append(Entry(children=tmp, set_parents=False))
        return _Choose(results)

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
        return Result(children=[c for c in self.children if query(c)])

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

    keys = get_keys

    def get_crumbs(self, down=False):
        """
        Get the unique names from the current locations to the roots.
        """
        res = chain.from_iterable(c.get_crumbs(down=down) for c in self.children)
        return sorted(set(res))

    crumbs = get_crumbs

    @property
    def sources(self):
        res = []
        for c in self.children:
            src = c.source
            if src is not None:
                res.append(src)
        return sorted(set(res))

    @property
    def line(self):
        """
        Returns the line of the child if only one child exists. This helps
        queries behave more like dictionaries when you know only one result
        should exist.
        """
        if len(self.children) == 0:
            return None

        if len(self.children) == 1:
            return self.children[0].line

        raise Exception("More than one value to return.")

    @property
    def string_value(self):
        """
        Returns the string value of the child if only one child exists. This
        helps queries behave more like dictionaries when you know only one
        result should exist.
        """
        if len(self.children) == 0:
            return None

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
        Returns all of the deduplicated parents as a list. If a child has no
        parent, the child itself is treated as the parent.
        """
        parents = []
        seen = set()
        for c in self.children:
            p = c.parent
            if p is not None:
                if p not in seen:
                    parents.append(p)
                    seen.add(p)
            elif c not in seen:
                parents.append(c)
                seen.add(c)
        return Result(children=parents)

    @property
    def roots(self):
        """
        Returns the furthest ancestor ``Entry`` instances of all children. If a
        child has no furthest ancestor, the child itself is treated as a root.
        """
        roots = []
        seen = set()
        for c in self.children:
            r = c.root
            if r is not None:
                if r not in seen:
                    roots.append(r)
                    seen.add(r)
            elif c not in seen:
                roots.append(c)
                seen.add(c)
        return Result(children=roots)

    @property
    def values(self):
        """
        Returns the values of all the children as a list.
        """
        return [c.value for c in self.children if c.value is not None]

    @property
    def unique_values(self):
        """
        Returns the unique values of all the children as a list.
        """
        return sorted(set(c.value for c in self.children if c.value is not None))

    def upto(self, query):
        """
        Go up from the current results to the first nodes that match query.
        """
        roots = []
        seen = set()
        for c in self.children:
            root = c.upto(query)
            if root is not None and root not in seen:
                roots.append(root)
                seen.add(root)
        return Result(children=roots)

    def nth(self, n):
        """
        If the results are from a list beneath a node, get the nth element of
        the results for each unique parent.

        Example:
        ``conf.status.conditions.nth(0)`` will get the 0th condition of each
        status.
        """
        tmp = defaultdict(list)
        for c in self.children:
            tmp[c.parent].append(c)

        results = []
        for _, v in tmp.items():
            try:
                r = v[n]
                if isinstance(r, list):
                    results.extend(r)
                else:
                    results.append(v[n])
            except:
                pass
        return Result(children=results)

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
        if isinstance(name, _EntryQuery):
            query = name.to_pyfunc()
        elif isinstance(name, Boolean):
            query = child_query(name, value).to_pyfunc()
        elif callable(name):
            def predicate(e):
                try:
                    return name(e)
                except:
                    return False
            query = predicate
        else:
            query = child_query(name, value).to_pyfunc()
        results = []
        seen = set()
        for c in self.children:
            if c not in seen and query(c):
                results.append(c)
        return Result(children=results)

    def to_df(self):
        import pandas as pd

        res = []
        for p in self.children:
            try:
                d = dict((c._name, c.attrs[0]) for c in p.children if len(c.attrs) == 1)
                res.append(d)
            except:
                pass
        return pd.DataFrame(res)

    def most_common(self, top=None):
        """
        Returns the distribution of values returned by queries that return a
        single value for each node.
        """
        res = [c.attrs[0] for c in self.children if len(c.attrs) == 1]
        return Counter(res).most_common(top)

    def __getitem__(self, query):
        if isinstance(query, (int, slice)):
            return self.children[query]
        query = _desugar(query)
        return Result(children=[c for c in self.grandchildren if query(c)])


class _Choose(Result):
    """
    Marker class that allows us to detected nested calls to choose
    """
    pass


class _EntryQuery(object):
    """
    _EntryQuery is the base class of all other query classes.
    """
    def __and__(self, other):
        return _AllEntryQuery(self, other)

    def __or__(self, other):
        return _AnyEntryQuery(self, other)

    def __invert__(self):
        return _NotEntryQuery(self)

    def to_pyfunc(self):
        ver = sys.version_info
        if ver[0] == 2 and ver[1] == 6:
            return self.test

        env = {}
        ids = count()

        def expr(b):
            if isinstance(b, _AllEntryQuery):
                return "(" + " and ".join(expr(p) for p in b.exprs) + ")"
            elif isinstance(b, _AnyEntryQuery):
                return "(" + " or ".join(expr(p) for p in b.exprs) + ")"
            elif isinstance(b, _NotEntryQuery):
                return "(" + "not " + expr(b.query) + ")"
            else:
                num = next(ids)
                func = "func_{num}".format(num=num)
                env[func] = b.test
                return func + "(value)"

        func = """
def predicate(value):
    try:
        return {body}
    except Exception as ex:
        return False
        """.format(body=expr(self))

        six.exec_(func, env, env)
        return env["predicate"]


class _AllEntryQuery(_EntryQuery, All):
    pass


class _AnyEntryQuery(_EntryQuery, Any):
    pass


class _NotEntryQuery(_EntryQuery, Not):
    pass


class _AllAttrQuery(_EntryQuery):
    def __init__(self, expr):
        self.expr = expr

    def test(self, e):
        return all(self.expr(a) for a in e.attrs)


class _AnyAttrQuery(_EntryQuery):
    def __init__(self, expr):
        self.expr = expr

    def test(self, e):
        return any(self.expr(a) for a in e.attrs)


def all_(expr):
    """
    Use to express that ``expr`` must succeed on all attributes for the query
    to be successful. Only works against :py:class:`Entry` attributes.
    """
    return _AllAttrQuery(_desugar_attr(expr))


def any_(expr):
    """
    Use to express that ``expr`` can succeed on any attribute for the query to be
    successful. Only works against :py:class:`Entry` attributes.
    """
    return _AnyAttrQuery(_desugar_attr(expr))


class ChildQuery(_EntryQuery):
    """
    Returns True if any child entry passes the query.
    """
    def __init__(self, expr):
        self.expr = expr

    def test(self, e):
        return any(self.expr(n) for n in e.children)


def child_query(name, value=None):
    """
    Converts a query into a ChildQuery that works on all child entries at once
    to determine if the current entry is accepted.
    """
    q = _desugar((name, value) if value is not None else name)
    return ChildQuery(q)


make_child_query = child_query


def _desugar_name(q):
    if q is None:
        return lambda _: True
    if isinstance(q, Boolean):
        f = q.to_pyfunc()
        return lambda e: f(e._name)
    if callable(q):
        def predicate(e):
            try:
                return q(e._name)
            except:
                return False
        return predicate
    return lambda e: e._name == q


def _desugar_attr(q):
    if isinstance(q, Boolean):
        return q.to_pyfunc()
    if callable(q):
        def predicate(v):
            try:
                return q(v)
            except:
                return False
        return predicate
    return lambda v: v == q


def _desugar_attrs(q):
    if not q:
        return
    if len(q) == 1:
        q = q[0]
        return q if isinstance(q, _EntryQuery) else _AnyAttrQuery(_desugar_attr(q))
    else:
        # conf[name, q0, q1] means "name and (q0 or q1 for any attribute)"
        attr_queries = [_desugar_attr(a) for a in q]
        return _AnyAttrQuery(lambda v: any(p(v) for p in attr_queries))


def _desugar(q):
    if isinstance(q, _EntryQuery):
        return q.to_pyfunc()
    if isinstance(q, tuple):
        name_query = _desugar_name(q[0])
        attrs_query = _desugar_attrs(q[1:])
        if attrs_query:
            aq = attrs_query.to_pyfunc()
            return lambda e: name_query(e) and aq(e)
        return name_query
    if q is None:
        return lambda _: True
    return _desugar_name(q)


def _flatten(nodes):
    """
    Flatten the config tree into a list of nodes.
    """
    def inner(n):
        yield n
        for i in chain.from_iterable(inner(c) for c in n.children):
            yield i
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
    queries = [_desugar(q) for q in queries]

    def match(qs, nodes):
        q = qs[0]
        qs = qs[1:]
        res = [n for n in nodes if q(n)]
        if qs and res:
            gc = list(chain.from_iterable(n.children for n in res))
            return match(qs, gc)
        return res

    def inner(nodes):
        return Result(children=match(queries, nodes))
    return inner


def select(query, nodes, deep=False, roots=False):
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


def from_dict(orig, src=None):
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
                        result.append(Entry(name=k, attrs=tuple(res)))
                else:
                    result.append(Entry(name=k))
            else:
                result.append(Entry(name=k, attrs=(v,)))
        return tuple(result)
    return Entry(children=inner(orig), src=src)


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
            name = d._name or ""
            header = name if not d.attrs else " ".join([name, d.string_value])
            if header:
                results.append(prefix + "[" + header + "]")
            prep = prefix + (" " * indent)
            for c in d.children:
                inner(c, prep)
            sep()
        else:
            results.append(prefix + (d._name or "") + ": " + d.string_value)

    inner(root)
    return results


# These predicates can be used in queries.
lt = pred2(operator.lt)
le = pred2(operator.le)
eq = pred2(operator.eq)
gt = pred2(operator.gt)
ge = pred2(operator.ge)

isin = pred2(lambda v, values: v in set(values))
matches = pred2(lambda v, pat: re.search(pat, v))

contains = pred2(operator.contains)
startswith = pred2(str.startswith)
endswith = pred2(str.endswith)

ieq = pred2(operator.eq, ignore_case=True)
icontains = pred2(operator.contains, ignore_case=True)
istartswith = pred2(str.startswith, ignore_case=True)
iendswith = pred2(str.endswith, ignore_case=True)

first = 0
last = -1
