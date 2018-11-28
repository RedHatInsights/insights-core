"""
configtree models configurations that are similar to dictionaries except that
each option may have a list of un-named attributes, and duplicate options are
allowed. Compound options containing children in addition to attributes also
are supported.

This model fits many systems that have a main configuration file with
supplementary files included in it by reference. Examples are httpd and nginx,
although simple .ini files are also supported. Base classes for Insights
parsers and combiners handle incorporating master and child documents into a
single tree. They make integration with Insights concise.

Individual document parsers are responsible for transforming raw content into
the configtree model. Some base classes and primitive parsing functions are
provided, but most systems' files (except maybe .ini) need specific handling.

configtree provides a small DSL for querying its trees, so navigating them for
specific information is less tedious and error prone.

Generating documents of various formats from a master tree is straightforward.
"""
import operator
import re
import six
from functools import partial
from itertools import chain


# classes modeling configuration trees
class Node(object):
    def __init__(self, name=None, attrs=None, children=None, ctx=None):
        """
        Base object of the document model. The documents are similar to
        dictionaries except that each level may have a list of un-named
        attributes, and duplicate keys at each level may be allowed.

        Attributes:
            name (str): something like "Directory" or "ServerRoot" from
                httpd.conf, "http" from nginx, or the name of an option in an
                ini file.
            attrs (list): the list of attributes associated with the name.
            children (list): child Nodes of this Node.
            ctx (ConfigParser):  provides lineat function for accessing the raw
                text from which the node was parsed.
        """
        self.name = name
        self.attrs = attrs or []
        self.children = children or []
        self.ctx = ctx
        self.pos = None
        self.parent = None

    def select(self, *queries, **kwargs):
        """
        Given a list of queries, executes those queries against the set of
        Nodes. A Node has three primary attributes: name (str), attrs
        ([str|int]), and children ([Node]).

        Nodes also have a value attribute that is either the first attribute
        (in the case of simple directives that only have one), or the string
        representation of all attributes joined by a single space.

        Each positional argument to select represents a query against the name
        and/or attributes of the corresponding level of the configuration tree.
        The first argument queries root nodes, the second argument queries
        children of the root nodes, etc.

        An individual query is either a single value or a tuple. A single value
        queries the name of a Node. A tuple queries the name and the attrs.

        So: `select(name_predicate)` or `select((name_predicate,
        attrs_predicate))`

        In general, `select(pred1, pred2, pred3, ...)`

        If a predicate is a simple value (string or int), an exact match is
        required for names, and an exact match of any attribute is required for
        attributes.

        Examples:
        `select("Directory")` queries for all root nodes named Directory.

        `select("Directory", "Options")` queries for all root nodes named
        Directory that contain at least one child node named Options. Notice
        the argument positions: Directory is in position 1, and Options is in
        position 2.

        `select(("Directory", "/"))` queries for all root nodes named Directory
        that contain an attribute exactly matching "/". Notice this is one
        argument to select: a 2-tuple with predicates for name and attrs.

        If you are only interested in attributes, just pass `None` for the name
        predicate in the tuple: `select((None, "/"))` will return all root
        nodes with at least one attribute of "/"

        In addition to exact matches, the elements of a query can be functions
        that accept the value corresponding to their position in the query. A
        handful of useful functions and boolean operators between them are
        provided.

        `select(startswith("Dir"))` queries for all root nodes with names
        starting with "Dir".

        `select(~startswith("Dir"))` queries for all root nodes with names not
        starting with "Dir".

        `select(startswith("Dir") | startswith("Ali"))` queries for all root
        nodes with names starting with "Dir" or "Ali". The return of `|` is a
        single callable passed in the first argument position of select.

        `select(~startswith("Dir") & ~startswith("Ali"))` queries for all root
        nodes with names not starting with "Dir" or "Ali".

        If a function is in an attribute position, it is considered True if it
        returns True for any attribute.

        For example, `select((None, 80))` often will return the list of one
        Node [Listen 80]

        `select(("Directory", startswith("/var")))` will return all root nodes
        named Directory that also have an attribute starting with "/var"

        If you know that your selection will only return one element, or you
        only want the first or last result of the query , pass `one=first` or
        `one=last`.

        `select(("Directory", startswith("/")), one=last)` will return the
        single root node for the last Directory entry starting with "/"

        If instead of the root nodes that match you want the child nodes that
        caused the match, pass `roots=False`.

        `node = select(("Directory", "/var/www/html"), "Options", one=last,
        roots=False)` might return the Options node if the Directory for
        "/var/www/html" was defined and contained an Options Directive. You
        could then access the attributes with `node.attrs`. If the query didn't
        match anything, it would have returned None.

        If you want to slide the query down the branches of the config, pass
        deep=True to select.  That allows you to do `conf.select("Directory",
        deep=True, roots=False)` and get back all Directory nodes regardless of
        nesting depth.

        conf.select() returns everything.

        Available predicates are:
        & (infix boolean and)
        | (infix boolean or)
        ~ (prefix boolean not)

        For ints or strings:
        eq (==)  e.g. conf.select("Directory, ("StartServers", eq(4)))
        ge (>=)  e.g. conf.select("Directory, ("StartServers", ge(4)))
        gt (>)
        le (<=)
        lt (<)

        For strings:
        contains
        endswith
        startswith
        """
        return select(*queries, **kwargs)(self.children)

    def find(self, *queries, **kwargs):
        """
        Finds the first result found anywhere in the configuration. Pass
        `one=last` for the last result. Returns `None` if no results are found.
        """
        kwargs["deep"] = True
        kwargs["roots"] = False
        if "one" not in kwargs:
            kwargs["one"] = first
        return self.select(*queries, **kwargs)

    def find_all(self, *queries):
        """
        Find all results matching the query anywhere in the configuration.
        Returns an empty `SearchResult` if no results are found.
        """
        return self.select(*queries, deep=True, roots=False)

    def _children_of_type(self, t):
        return [c for c in self.children if isinstance(c, t)]

    @property
    def sections(self):
        return SearchResult(children=self._children_of_type(Section))

    @property
    def directives(self):
        return SearchResult(children=self._children_of_type(Directive))

    def __getitem__(self, query):
        """
        Similar to select, except tuples are constructed without parentheses:
        `conf["Directory", "/"]` is the same as `conf.select(("Directory", "/"))`

        Notice that queries return `SearchResult` instances, which also have
        `__getitem__` delegating to `select` except the select is against
        grandchild nodes in the tree. This allows more complicated queries,
        like this one that gets all Options entries beneath the Directory
        entries starting with "/var":

        `conf["Directory", startswith("/var")]["Options"]`

        or equivalently

        `conf.select(("Directory", startswith("/var")), "Options, roots=False)

        Note you can recover the enclosing section with `node.parent` or a
        node's ultimate root with `node.root`. If a `Node` is a root,
        `node.root` is just the node itself.

        To get all root level Directory and Alias directives, you could do
        something like `conf[eq("Directory") | eq("Alias")]`

        To get loaded auth modules:
        `conf["LoadModule", contains("auth")]`
        """
        if isinstance(query, (int, slice)):
            return self.children[query]
        return select(query, roots=False)(self.children)

    @property
    def root(self):
        p = self
        while p and p.parent:
            p = p.parent
        return p

    @property
    def grandchildren(self):
        return list(chain.from_iterable(c.children for c in self.children))

    @property
    def section(self):
        return None

    @property
    def section_name(self):
        return None

    @property
    def line(self):
        if self.ctx and self.pos is not None:
            return self.ctx.lineat(self.pos)

    @property
    def lineno(self):
        if self.pos is not None:
            return self.pos + 1

    @property
    def file_path(self):
        if self.ctx:
            return self.ctx.file_path

    @property
    def file_name(self):
        if self.ctx:
            return self.ctx.file_name

    @property
    def value(self):
        if len(self.attrs) == 1:
            return self.attrs[0]
        return self.svalue()

    def svalue(self, conv=str):
        return " ".join([conv(a) for a in self.attrs])

    def __bool__(self):
        return bool(self.name or self.attrs or self.children)

    def __contains__(self, item):
        return any(c.name == item for c in self.children)

    def __len__(self):
        return len(self.children)

    def __iter__(self):
        return iter(self.children)

    def __repr__(self):
        return "\n".join(pretty_format(self))

    def __str__(self):
        return self.__repr__()

    __nonzero__ = __bool__


class SearchResult(Node):
    """
    Root node of select results. It has no name or attrs.

    Dictionary operators target grandchildren instead of children
    so that searches can be chained to reach into the tree.
    """
    def __contains__(self, item):
        return any(c.name == item for c in self.grandchildren)

    def __getitem__(self, query):
        if isinstance(query, (int, slice)):
            return self.children[query]
        return select(query, roots=False)(self.grandchildren)


class Root(Node):
    """
    Placeholder Node for top level documents. It has no name or attrs.
    """
    pass


class Section(Node):
    """
    Node for sections such as the XML-like stanzas in httpd configurations.
    """
    def __init__(self, **kwargs):
        super(Section, self).__init__(**kwargs)
        for c in self.children:
            c.parent = self

    @property
    def section(self):
        return self.name

    @property
    def section_name(self):
        return self.value


class Directive(Node):
    """ One liners. A name followed by one or more values. """
    @property
    def section(self):
        if self.parent:
            return self.parent.section

    @property
    def section_name(self):
        if self.parent:
            return self.parent.value


def from_dict(dct):
    """ Convert a dictionary into a configtree.  """
    def inner(d):
        results = []
        for name, v in d.items():
            if isinstance(v, dict):
                results.append(Section(name=name, children=from_dict(v)))
            elif isinstance(v, list):
                if not any(isinstance(i, dict) for i in v):
                    results.append(Directive(name=name, attrs=v))
                else:
                    for i in v:
                        if isinstance(i, dict):
                            results.append(Section(name=name, children=from_dict(i)))
                        elif isinstance(i, list):
                            results.append(Directive(name=name, attrs=i))
                        else:
                            results.append(Directive(name=name, attrs=[i]))
            else:
                results.append(Directive(name, attrs=[v]))
        return results
    return Root(children=inner(dct))


def to_str(x):
    x = str(x)
    if " " in x or "'" in x or '"' in x:
        if "\\'" in x:
            return '"%s"' % x
        if '\\"' in x:
            return "'%s'" % x
        if " " in x:
            return '"%s"' % x
    return x


# pretty formatter for the model
def pretty_format(doc, indent=4):
    results = []

    def inner(d, prepend):
        if isinstance(d, (Root, SearchResult)):
            for c in d.children:
                inner(c, prepend)
        elif isinstance(d, Section):
            results.append("")
            header = d.name if not d.attrs else " ".join([d.name, d.svalue(conv=to_str)])
            results.append(prepend + "[" + header + "]")
            prep = prepend + (" " * indent)
            for c in d.children:
                inner(c, prep)
            results.append("")
        else:
            results.append(prepend + d.name + ": " + d.svalue(conv=to_str))
    inner(doc, "")
    return results


class PushBack(object):
    """
    Wraps an iterable with push back capability. Tracks position in the stream.
    """
    def __init__(self, stream):
        self.stream = iter(stream)
        self.buffer = []
        self.pos = 0

    def push_back(self, item):
        self.pos -= 1
        self.buffer.append(item)

    def peek(self):
        if not self.buffer:
            self.buffer.append(self._next())
        return self.buffer[-1]

    def __iter__(self):
        return self

    def _next(self):
        return next(self.stream)

    def next(self):
        self.pos += 1
        if self.buffer:
            return self.buffer.pop()
        return self._next()

    __next__ = next


class LineGetter(PushBack):
    """
    A push back wrapper for lines. Automatically skips comments and spaces.
    """
    def __init__(self, it, comment_marker="#", strip=True):
        super(LineGetter, self).__init__(it)
        self.comment_marker = comment_marker
        self.strip = strip

    def _next(self):
        l = next(self.stream)
        while l.strip() == "" or l.lstrip().startswith(self.comment_marker):
            self.pos += 1
            l = next(self.stream)
        while l.endswith("\\"):
            self.pos += 1
            l = l.rstrip("\\")
            l += next(self.stream).lstrip()

        return l.strip() if self.strip else l.rstrip()


def eat_whitespace(pb, to=None):
    try:
        while pb.peek().isspace() or pb.peek() == "#":
            if pb.peek().isspace():
                if pb.peek() == to:
                    break
                next(pb)
            if pb.peek() == "#":
                while pb.peek() != "\n":
                    next(pb)
    except StopIteration:
        pass


def parse_string(pb):
    buf = []
    start = next(pb)  # eat quote
    while pb.peek() != start:
        c = next(pb)
        if c == "\\":
            c = next(pb)
        buf.append(c)
    next(pb)  # eat quote
    return "".join(buf)


def parse_bare(pb):
    buf = []
    try:
        while not pb.peek().isspace():
            buf.append(next(pb))
    except StopIteration:
        pass
    return "".join(buf)


BOOLS = {
    "yes": True,
    "on": True,
    "true": True,
    "no": False,
    "off": False,
    "false": False
}


def typed(x):
    v = BOOLS.get(x.lower())
    if v is not None:
        return v
    for t in [int, float]:
        try:
            return t(x)
        except:
            pass
    return x


def parse_attrs(attr_string):
    pb = PushBack(attr_string)
    attrs = []
    while True:
        try:
            while(pb.peek().isspace()):
                next(pb)

            if pb.peek() in ('"', "'"):
                attrs.append(parse_string(pb))
            else:
                attrs.append(parse_bare(pb))
        except StopIteration:
            break
    if len(attrs) == 1:
        return [typed(attrs[0])]
    return attrs


def parse_name_attrs(line, sep=None):
    attrs = []
    parts = re.split(sep, line, 1) if sep else line.split(None, 1)
    name = parts[0].strip()
    if name[0] in ('"', "'"):
        name = parse_string(PushBack(name))
    else:
        name = parse_bare(PushBack(name))
    if len(parts) > 1:
        attrs = parse_attrs(parts[1])
    return (name, attrs)


class DocParser(object):
    """
    Wrapper class so parser functions don't have to thread ctx.

    Other line oriented configuration parsers may subclass this class to
    remove a bit of boilerplate.
    """
    def __init__(self, ctx):
        self.ctx = ctx

    def parse_doc(self, lg):
        children = []
        while True:
            try:
                children.append(self.parse_statement(lg))
            except StopIteration:
                break
        return Root(children=children, ctx=self.ctx)


if six.PY3:
    import unicodedata

    def caseless(text):
        return unicodedata.normalize("NFKD", text.casefold())
else:
    def caseless(text):
        return text.lower()


# DSL for querying trees of Nodes. Start with `select`.
def __or(funcs, args):
    """ Support list sugar for "or" of two predicates. Used inside `select`. """
    results = []
    for f in funcs:
        result = f(args)
        if result:
            results.extend(result)
    return results


# helper functions for Predicates
def _or(f, g):
    def inner(data):
        return f(data) or g(data)
    return inner


def _and(f, g):
    def inner(data):
        return f(data) and g(data)
    return inner


def _not(f):
    def inner(data):
        return not f(data)
    return inner


class Bool(object):
    """ Allows boolean logic between predicates. """
    def __and__(self, other):
        return CompositeBool(_and(self, other))

    def __or__(self, other):
        return CompositeBool(_or(self, other))

    def __invert__(self):
        return CompositeBool(_not(self))


class CompositeBool(Bool):
    """ Combines two DSL predicates. """
    def __init__(self, pred):
        self.pred = pred

    def __call__(self, data):
        try:
            return self.pred(data)
        except:
            return False


class UnaryBool(Bool):
    """ Lifts predicates into the DSL. """
    def __init__(self, pred):
        self.pred = pred

    def __call__(self, data):
            if not isinstance(data, list):
                data = [data]
            for d in data:
                try:
                    if self.pred(d):
                        return True
                except:
                    pass
            return False


def BinaryBool(pred):
    """ Lifts predicates that take an argument into the DSL. """
    class Predicate(Bool):
        def __init__(self, value, ignore_case=False):
            self.value = caseless(value) if ignore_case else value
            self.ignore_case = ignore_case

        def __call__(self, data):
            if not isinstance(data, list):
                data = [data]
            for d in data:
                try:
                    if pred(caseless(d) if self.ignore_case else d, self.value):
                        return True
                except:
                    pass
            return False
    return Predicate


startswith = BinaryBool(str.startswith)
istartswith = partial(startswith, ignore_case=True)

endswith = BinaryBool(str.endswith)
iendswith = partial(endswith, ignore_case=True)

contains = BinaryBool(operator.contains)
icontains = partial(contains, ignore_case=True)

le = BinaryBool(operator.le)
ile = partial(le, ignore_case=True)

lt = BinaryBool(operator.lt)
ilt = partial(lt, ignore_case=True)

ge = BinaryBool(operator.ge)
ige = partial(ge, ignore_case=True)

gt = BinaryBool(operator.gt)
igt = partial(gt, ignore_case=True)

eq = BinaryBool(operator.eq)
ieq = partial(eq, ignore_case=True)


def __make_name_pred(name):
    return name if callable(name) else lambda x: (name is None or x == name)


def __make_attrs_pred(attrs):
    if len(attrs) == 1 and callable(attrs[0]):
        return attrs[0]
    return lambda x: (len(attrs) == 0 or any(a in x for a in attrs))


def __compose(g, f):
    def inner(nodes):
        results = []
        tmp = f(nodes)
        for t in tmp:
            results.extend(g(t.children))
        return results
    return inner


# selection strategy when multiple results are returned but only one is needed
first = 0
last = -1


def select(*queries, **kwargs):
    """
    Builds a function that will execute the specified queries against a list of
    Nodes.
    """
    def make_query(*args):
        def simple_query(nodes):
            if len(args) == 0:
                return nodes
            pred = args[0]
            results = []
            if isinstance(pred, list):
                funcs = [make_query(q) for q in pred]
                return __or(funcs, nodes)
            elif isinstance(pred, tuple):
                name, attrs = pred[0], pred[1:]
                name_pred = __make_name_pred(name)
                attrs_pred = __make_attrs_pred(attrs)
                for n in nodes:
                    if name_pred(n.name) and attrs_pred(n.attrs):
                        results.append(n)
            else:
                name_pred = __make_name_pred(pred)
                for n in nodes:
                    if name_pred(n.name):
                        results.append(n)
            return results
        if len(args) > 1:
            return __compose(make_query(*args[1:]), simple_query)
        return simple_query

    def deep_query(query, nodes):
        """ Slide the query down the branches. """
        def inner(children):
            results = []
            for c in children:
                if query([c]):
                    results.append(c)
                results.extend(inner(c.children))
            return results
        return inner(nodes)

    def unique(roots):
        seen = set()
        results = []
        for r in roots:
            if r not in seen:
                seen.add(r)
                results.append(r)
        return results

    def compiled_query(nodes):
        """
        This is the compiled query that can be run against a configuration.
        """
        query = make_query(*queries)

        roots = kwargs.get("roots", True)
        if kwargs.get("deep", False):
            results = deep_query(query, nodes)
            if roots:
                results = unique([r.root for r in results])
        elif roots:
            results = unique([n.root for n in query(nodes)])
        else:
            results = query(nodes)

        one = kwargs.get("one")
        if one is None:
            return SearchResult(children=results)
        return results[one] if results else None
    return compiled_query
