import operator
import os
import re
from fnmatch import fnmatch
from itertools import chain

from insights.core import Parser


# classes modeling configuration trees
class Node(object):
    def __init__(self, name=None, attrs=None, children=None, ctx=None):
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

    def __getitem__(self, query):
        """
        Similar to select, except tuples are automatically constructed, and
        subselects of children are specified by chained brackets:
        `conf["Directory", "/"] is the same as conf.select(("Directory", "/"))

        Notice that queries return `SearchResult` instances, which also have
        __getitem__ delegating to select except the select is against
        grandchild nodes in the tree.  This allows more complicated queries,
        like this one that gets all Options entries beneath the Directory
        entries starting with "/var"

        `conf["Directory", startswith("/var")]["Options"]`

        or equivalently

        `conf.select(("Directory", startswith("/var")), "Options, roots=False)

        Note you can recover the enclosing section with node.parent or a node's
        ultimate root with node.root. If a Node is a root, node.root is just
        the node itself.

        To get all root level Directory and Alias directives, you could do
        something like `conf[eq("Directory") | eq("Alias")]`

        To get loaded auth modules
        `conf["LoadModule", contains("auth")]`
        """
        if isinstance(query, int):
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
        if isinstance(query, int):
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


# parser components that create trees of Nodes based on configuration files.
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
        return l.strip() if self.strip else l.rstrip()


def parse_string(pb):
    buf = []
    start = next(pb)  # eat quote
    while pb.peek() != start:
        c = next(pb)
        buf.append(c)
        if c == "\\":
            buf.append(next(pb))
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


class Op(object):
    def __and__(self, other):
        return Bool(_and(self, other))

    def __or__(self, other):
        return Bool(_or(self, other))

    def __invert__(self):
        return Bool(_not(self))


class Bool(Op):
    def __init__(self, pred):
        self.pred = pred

    def __call__(self, data):
        return self.pred(data)


def __udf(op, _type):
    """ Lifts operators into the DSL. """
    class Predicate(Op):
        def __init__(self, value):
            self.value = value

        def __call__(self, data):
            if isinstance(data, _type):
                return op(data, self.value)
            if isinstance(data, list):
                return any(op(d, self.value) for d in data if isinstance(d, _type))
            return False
    return Predicate


startswith = __udf(str.startswith, str)
endswith = __udf(str.endswith, str)
contains = __udf(operator.contains, str)

le = __udf(operator.le, (int, str))
lt = __udf(operator.lt, (int, str))
ge = __udf(operator.ge, (int, str))
gt = __udf(operator.gt, (int, str))
eq = __udf(operator.eq, (int, str))


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

    def compiled_query(nodes):
        """
        This is the compiled query that can be run against a configuration.
        """
        query = make_query(*queries)

        roots = kwargs.get("roots", True)
        if kwargs.get("deep", False):
            results = deep_query(query, nodes)
            if roots:
                results = [r.root for r in results]
        elif roots:
            results = [n.root for n in query(nodes)]
        else:
            results = query(nodes)

        one = kwargs.get("one")
        if one is None:
            return SearchResult(children=results)
        return results[one] if results else None
    return compiled_query


def find_matches(confs, pattern):
    results = [c for c in confs if fnmatch(c.file_path, pattern)]
    return sorted(results, key=operator.attrgetter("file_name"))


def find_main(confs, name):
    for c in confs:
        if c.file_name == name:
            return c


def flatten(docs, pred):
    def inner(children):
        results = []
        for c in children:
            if select(pred)([c]) and c.children:
                results.extend(inner(c.children))
            else:
                results.append(c)
        return results
    return inner(docs)


class ConfigComponent(object):
    def select(self, *queries, **kwargs):
        return self.doc.select(*queries, **kwargs)

    def __getitem__(self, query):
        return self.select(query)

    def __contains__(self, item):
        return item in self.doc

    def __iter__(self):
        return iter(self.doc)

    def __repr__(self):
        return str(self.doc)

    def __str__(self):
        return self.__repr__()


class ConfigParser(Parser, ConfigComponent):
    def parse_content(self, content):
        self.content = content
        self.doc = self.parse_doc(content)

    def lineat(self, pos):
        return self.content[pos] if pos is not None else None


class ConfigCombiner(ConfigComponent):
    def __init__(self, confs, main_file, include_finder):
        self.confs = confs
        self.main = find_main(confs, main_file)
        server_root = self.conf_path

        # Set the children of all include directives to the contents of the
        # included configs
        for conf in confs:
            for node in conf.doc.select(include_finder, deep=True, roots=False):
                pattern = node.value
                if not pattern.startswith("/"):
                    pattern = os.path.join(server_root, pattern)
                includes = find_matches(confs, pattern)
                for inc in includes:
                    node.children.extend(inc.doc.children)

        # flatten all content from nested Includes into a main doc
        self.doc = Root(children=flatten(self.main.doc.children, include_finder))
