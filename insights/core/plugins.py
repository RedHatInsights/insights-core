import logging
import types
from collections import defaultdict
from functools import reduce as _reduce, wraps
from insights.config.factory import get_config
from insights.core import load_package
from insights import settings

data_spec_config = get_config()
log = logging.getLogger(__name__)

RESPONSE_TYPES = ["rule", "metadata", "skip"]

# Only used in test suite for plugin validation
SYMBOLIC_NAME_FILTER_MAPPING = defaultdict(lambda: defaultdict(list))

# Data structures that hold different sets of plugin metadata
# These are all populated via decorators while loading plugins
NAME_TO_FILTER_MAP = defaultdict(set)
PARSERS = defaultdict(list)
PARSER_FUNCS = {}
SHARED_PARSERS = []
PLUGINS = defaultdict(lambda: {
    "module": None,
    "parsers": [],
    "reducers": [],
    "cluster_reducers": []
})
REDUCERS = {}
CLUSTER_REDUCERS = {}

TYPE_OF_COMPONENT = {}
COMPONENTS_BY_TYPE = defaultdict(set)
COMPONENT_DEPENDENCIES = defaultdict(set)
EMITTERS = set()
DELEGATES = {}


def cluster_reducers():
    return [k.rpartition(".")[-1] for k, v in PLUGINS.iteritems() if v["cluster_reducers"]]


def single_reducers():
    return [k.rpartition(".")[-1] for k, v in PLUGINS.iteritems() if not v["cluster_reducers"]]


def load(package_name, pattern_list=None):
    loaded = load_package(package_name, pattern_list)
    build_filter_map()
    return loaded


def build_filter_map():
    for name, plugins in PARSERS.iteritems():
        filter_list = [f for plugin in plugins for f in plugin.filters]
        # TODO: Make all large files filtered so we can test for the thing below
        # if data_spec_config.is_large(name) and len(filter_list) == 0:
        #     raise Exception("Registering %s requires specifying at least one filter" % name)
        NAME_TO_FILTER_MAP[name] = set(filter_list)


def get_name(plugin):
    return plugin.__module__.rpartition(".")[-1]


def add_to_map(name, handler, filters, shared=False):

    handler.shared = shared or "insights.parsers" in handler.__module__
    if handler.shared:
        SHARED_PARSERS.append(handler)

    PARSERS[name].append(handler)

    handler.filters = filters if filters else []

    plugin_name = "{0}.{1}".format(handler.__module__, handler.__name__)
    SYMBOLIC_NAME_FILTER_MAPPING[name][bool(filters)].append(plugin_name)


def get_parsers(name, mapping=PARSERS):
    return mapping.get(name, [])


def inject_host(r, host):
    if isinstance(r, types.StringTypes):
        return {r: host}
    elif isinstance(r, types.DictType):
        keys = r.keys()
        if len(keys) != 1:
            raise Exception("Cluster parser response can't have multiple keys")
        parser_key = keys[0]
        if not isinstance(r[parser_key], types.DictType):
            v = r[parser_key]
            r[parser_key] = {"value": v}
        r[parser_key]["host"] = host
        return r


def register_cluster_parser(name, func, filters=[]):
    @wraps(func)
    def host_inject_wrapper(context):
        r = func(context)
        return inject_host(r, context.hostname) if r else None
    register_parser(name, host_inject_wrapper, filters, cluster=True)


def register_parser(name, func, filters=None, shared=False, cluster=False):
    '''
    Associate a mapping function to a sosreport file.

    .. py:attribute:: name

       The alias used to identify the sosreport file ``func`` will process.

    .. py:attribute:: func

       Parser function which will process the file identified by ``name``.

    .. py:attribute:: filters

       Strings used to identify (and filter) lines from large format files
       that the plugin requires.  These filters are used to created
       uploader server lists used to filter out non-matching lines from being
       collected during a client upload.

    .. py:attribute:: shared

       Parser function will be added to the shared parser namespace. The output
       of this parser will be available to all combiners and rules.

    '''

    if not isinstance(filters, types.ListType):
        raise TypeError("Require a '{0}' object but received a '{1}'.".format(
            types.ListType.__name__, type(filters).__name__))

    try:
        log.debug("registering [%s] to [%s]", ".".join([func.__module__, func.__name__]), name)
        add_to_map(name, func, filters, shared=shared)
        func.serializable_id = "#".join([func.__module__, func.__name__])
        func.consumers = set()
        add_symbolic_name(func, name)
        PARSER_FUNCS[func.serializable_id] = func
        p = PLUGINS[func.__module__]
        p["parsers"].append(func)
        p["module"] = func.__module__

        # Need to add already-registered rules defined in same module to consumer list
        # Should only happen if a @rule is defined above a @parser in the same module
        f_module = func.__module__
        for r in [r for r in REDUCERS.values() if r.__module__ == f_module]:
            func.consumers.add(r)
        shared = shared or ('parsers' in func.__module__)
        component_type = cluster_parser if cluster else parser
        register_component(func, func, component_type,
                           requires=None,
                           optional=None,
                           shared=shared,
                           cluster=cluster,
                           emitter=False)
    except Exception:
        log.exception("Failed to register parser: %s", func.__name__)
        raise


def add_symbolic_name(f, name):
    if not hasattr(f, "symbolic_names"):
        f.symbolic_names = []
    f.symbolic_names.append(name)


def register_reducer(func):
    REDUCERS[get_name(func)] = func
    func.serializable_id = "#".join([func.__module__, func.__name__])
    p = PLUGINS[func.__module__]
    p["reducers"].append(func)
    p["module"] = func.__module__


def register_cluster_reducer(func):
    CLUSTER_REDUCERS[get_name(func)] = func
    func.serializable_id = "#".join([func.__module__, func.__name__])
    p = PLUGINS[func.__module__]
    p["cluster_reducers"].append(func)
    p["module"] = func.__module__


def parser(filename, filters=[], shared=False):
    """
    Convenience decorator for parser callables.

    :param str filename: symbolic name of the file to register against
    :param list filters: list of plain strings that should be kept when removing
        lines from a large-format file

    Registering a parser for /var/log/messages ::

      @parser('messages', ['interesting_plain_text_indicator'])
      def my_func(context):
          pass

    Registering a parser for dmidecode ::

      @parser('dmidecode')
      def my_func(context):
          pass

    """
    def _register(func):
        register_parser(filename, func, filters, shared=shared)
        return func

    return _register


def cluster_parser(filename, filters=[]):
    """
    Convenience decorator for parser callables in clustered modules.

    See the parser decorator for a description of parameters and registration.

    Since cluster rules need to be host-aware, parsers need to include
    the hostname in all responses so the rule can differentiate between
    hosts.  This can be cumbersome, therefore the @cluster_parser has been
    added.  It will inject the hostname into the response returned from a
    parser that uses the @cluster_parser decorator.

    There are three cases based on what type is returned by a parser:

    1. String e.g. "FOOBAR" -> {
    "FOOBAR": hostname
    }
    2. Shallow map e.g. {"FOO": "BAR"} -> {
    "FOO": {"host": hostname, "value": "BAR"}
    }
    3. Deep map e.g. {"FOO": {"BAR": 1, "BAZ": 2}} -> {
    "FOO": {"host": hostname, "FOO": 1, "BAZ": 2}
    }

    NOTE: Parser shallow dict responses must only have one key, which
    represents a sort of "parser key" to be later referenced in the rule.
    If multiple keys are used, an error will be thrown.
    """
    def _register(func):
        register_cluster_parser(filename, func, filters)
        return func

    return _register


def walk_dependencies(root, visitor):
    """
    Call visitor on all dependencies reachable from root.

    :param function root: rule function
    :param function visitor: function to call on each dependencies that is
        reachable from root.
    """

    def _visit_parsers(parent, visitor):
        requires = COMPONENT_DEPENDENCIES[parent]
        for r in requires:
            visitor(parent, r)
            if r.shared:
                _visit_parsers(r, visitor)

    _visit_parsers(root, visitor)

    # Non-shared parsers defined in same module are implicitly consumed
    root_module = root.__module__
    for parsers in PARSERS.values():
        for m in parsers:
            if m.__module__ == root_module:
                visitor(root, m)


def get_dependency_graph(component):
    graph = defaultdict(set)

    def visitor(parent, component):
        graph[parent].add(component)

    walk_dependencies(component, visitor)

    graph = dict(graph)
    # Find all items that don't depend on anything.
    extra_items_in_deps = _reduce(set.union, graph.values()) - set(graph.keys())
    # Add empty dependences where needed.
    graph.update({item: set() for item in extra_items_in_deps})
    return graph


def group_by_type(components):
    graph = defaultdict(set)
    for c in components:
        graph[TYPE_OF_COMPONENT[c]].add(c)
    return dict(graph)


def split_requirements(requires):
    req_all = []
    req_any = []
    for r in requires:
        if isinstance(r, list):
            req_any.append(r)
        else:
            req_all.append(r)
    return req_all, req_any


def stringify_requirements(requires):
    if isinstance(requires, tuple):
        req_all, req_any = requires
    else:
        req_all, req_any = split_requirements(requires)
    pretty_all = [r.serializable_id for r in req_all]
    pretty_any = [str([r.serializable_id for r in any_list]) for any_list in req_any]
    return "All: %s" % pretty_all + " Any: " + " Any: ".join(pretty_any)


def get_missing_requirements(requires, d):
    if not requires:
        return None
    req_all, req_any = split_requirements(requires)
    d = set(d.keys())
    req_all = [r for r in req_all if r not in d]
    req_any = [r for r in req_any if set(r).isdisjoint(d)]
    if not req_all and not req_any:
        return None
    else:
        return req_all, req_any


def box(data):
    return dict((k, box_value(v)) for k, v in data.iteritems())


def box_value(v):
    if v:
        if isinstance(v, types.StringTypes):
            return [v]
        elif isinstance(v, types.DictType):
            return [v]
        else:
            return v
    else:
        return []


def register_consumer(c):
    """ Register rules as consumers of parsers. """

    def register(parent, component):
        if not component._reducer:
            component.consumers.add(c)

    walk_dependencies(c, register)


def register_component(
        component,
        delegate,
        component_type,
        requires=None,
        optional=None,
        shared=True,
        cluster=False,
        emitter=False):
    """
    Registers any component that is not a parser or cluster_parser.

    This is a single registration interface for combiners, rules, cluster_rules,
    etc.

    Args:
        component: function or class decorated as a component
        delegate: function that wraps the component to enforce met dependencies
        component_type: parser, rule, combiner, etc.
        requires: list of components the component needs
        optional: list of optional components the component can use
        shared: True for parsers and combiners
        cluster: True for cluster parsers and cluster rules
        emitter: True for components that return make_response(...)
    """
    is_reducer = component_type not in (parser, cluster_parser)
    if is_reducer:
        if cluster:
            register_cluster_reducer(component)
        else:
            register_reducer(component)

    component._reducer = is_reducer
    component.shared = shared
    component.cluster = cluster

    TYPE_OF_COMPONENT[component] = component_type
    COMPONENTS_BY_TYPE[component_type].add(component)
    DELEGATES[component] = delegate

    if requires:
        _all, _any = split_requirements(requires)
        _all = set(_all)
        _any = set(i for o in _any for i in o)
    else:
        _all, _any = set(), set()
    _optional = set(optional) if optional else set()

    COMPONENT_DEPENDENCIES[component] |= (_all | _any | _optional)

    if emitter:
        EMITTERS.add(component)
        register_consumer(component)


def default_executor(func,
                     local,
                     broker,
                     shared=True,
                     cluster=False,
                     emitter=False):
    if cluster:
        return func(box(local), broker)
    else:
        return func(local, broker)


def new_component_type(name=None,
                       auto_requires=[],
                       auto_optional=[],
                       shared=True,
                       cluster=False,
                       emitter=False,
                       executor=default_executor):
    """
    Factory that creates component decorators.

    The functions this factory produces are decorators for combiners,
    rules, cluster rules, etc. They don't yet define parsers or cluster_parsers.

    Args:
        name (str): the name of the component type the produced decorator
            will define
        auto_requires (list): All decorated components automatically have
            this requires spec. Anything specified when decorating a component
            is added to this spec.
        auto_optional (list): All decorated components automatically have
            this optional spec. Anything specified when decorating a component
            is added to this spec.
        shared (bool): the component should be used outside its defining module?
        cluster (bool): the component should be run for multi-node archives?
        emitter (bool): the components returns make_response(...)?
        executor (func): an optional function that controls how a component is
            executed. It can impose restrictions on return value types, perform
            component type specific exception handling, etc. The signature is
            `executor(component, broker, shared=?, cluster=?, emitter=?)`. The
            default behavior is to directly call `func(broker)`.

    Returns:
        A decorator function used to define components of the new type
    """

    def decorator(requires=None, optional=None, executor=executor):
        requires = requires or []
        optional = optional or []

        requires.extend(auto_requires)
        optional.extend(auto_optional)

        def _f(func):
            @wraps(func)
            def __f(local, broker):
                missing_requirements = get_missing_requirements(requires, broker)
                if not requires or not missing_requirements:
                    if executor:
                        return executor(func, local, broker, shared=shared, cluster=cluster, emitter=emitter)
                    return func(local, broker)
                else:
                    log.debug("Component [%s] is missing requirements: %s",
                              func.__module__,
                              stringify_requirements(missing_requirements))
                    if emitter:
                        rule_name = ".".join([func.__module__, func.__name__])
                        log.debug("Component %s is being skipped due to missing requirements", rule_name)
                        return make_skip(rule_name,
                                         reason="MISSING_REQUIREMENTS",
                                         details=missing_requirements)
            register_component(func, __f, decorator,
                               requires=requires,
                               optional=optional,
                               shared=shared,
                               cluster=cluster,
                               emitter=emitter)
            return func
        return _f
    if name:
        decorator.__name__ = name
    return decorator


data_provider = new_component_type("combiner", shared=True, cluster=False, emitter=False)
""" Defines a component that a `Parser` will consume."""

combiner = new_component_type("combiner", shared=True, cluster=False, emitter=False)
""" Combines several parsers or other combiners."""

cluster_rule = new_component_type("cluster_rule", shared=False, cluster=True, emitter=True)
""" A rule that can see parser and combiner results for all hosts in a cluster."""

rule = new_component_type("rule", shared=False, cluster=False, emitter=True)
""" A component that can see all parsers and combiners for a single host."""

condition = new_component_type("condition", shared=True, cluster=False, emitter=False)
""" A component used within rules that allows automated statistical analysis."""

incident = new_component_type("incident", shared=True, cluster=False, emitter=False)
""" A component used within rules that allows automated statistical analysis."""


def make_skip(rule_fqdn, reason, details=None):
    return {"rule_fqdn": rule_fqdn,
            "reason": reason,
            "details": details,
            "type": "skip"}


def make_response(error_key, **kwargs):
    """ Returns a JSON document approprate as a rule plugin final
    result.

    :param str error_key: The error name identified by the plugin
    :param \*\*kwargs: Strings to pass additional information to the frontend for
          rendering more complete messages in a customer system report.


    Given::

        make_response("CRITICAL_ERROR", cpu_number=2, cpu_type="intel")

    The response will be the JSON string ::

        {
            "type": "rule",
            "error_key": "CRITICAL_ERROR",
            "cpu_number": 2,
            "cpu_type": "intel"
        }
    """

    if "error_key" in kwargs or "type" in kwargs:
        raise Exception("Can't use an invalid argument for make_response")

    r = {
        "type": "rule",
        "error_key": error_key
    }
    kwargs.update(r)

    # using str() avoids many serialization issues and runs in about 75%
    # of the time as json.dumps
    detail_length = len(str(kwargs))

    if detail_length > settings.defaults["max_detail_length"]:
        log.error("Length of data in make_response is too long.", extra={
            "max_detail_length": settings.defaults["max_detail_length"],
            "error_key": error_key,
            "len": detail_length
        })
        r["max_detail_length_error"] = detail_length
        return r

    return kwargs


def make_metadata(**kwargs):
    if "type" in kwargs:
        raise Exception("Can't use an invalid argument for make_metadata")

    r = {"type": "metadata"}
    r.update(kwargs)
    return r


class ValidationException(Exception):
    def __init__(self, msg, r=None):
        if r:
            msg = "%s: %s" % (msg, r)
        super(ValidationException, self).__init__(msg)


def validate_response(r):
    if not isinstance(r, types.DictType):
        raise ValidationException("Response is not a dict", type(r))
    if "type" not in r:
        raise ValidationException("Response requires 'type' key", r)
    if r["type"] not in RESPONSE_TYPES:
        raise ValidationException("Invalid response type", r["type"])
    if r["type"] == "rule":
        error_key = r.get("error_key")
        if not error_key:
            raise ValidationException("Rule response missing error_key", r)
        elif not isinstance(error_key, types.StringTypes):
            raise ValidationException("Response contains invalid error_key type", type(error_key))
