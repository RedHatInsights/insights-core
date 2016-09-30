import logging
import types
from collections import defaultdict
from functools import wraps
from falafel.config.factory import get_config
from falafel.core import load_package

data_spec_config = get_config()
log = logging.getLogger(__name__)

RESPONSE_TYPES = ["rule", "metadata"]

# Only used in test suite for plugin validation
SYMBOLIC_NAME_FILTER_MAPPING = defaultdict(lambda: defaultdict(list))

# Data structures that hold different sets of plugin metadata
# These are all populated via decorators while loading plugins
NAME_TO_FILTER_MAP = defaultdict(set)
MAPPERS = defaultdict(list)
MAPPER_FUNCS = {}
SHARED_MAPPERS = []
PLUGINS = defaultdict(lambda: {
    "module": None,
    "mappers": [],
    "reducers": [],
    "cluster_reducers": []
})
REDUCERS = {}
CLUSTER_REDUCERS = {}


def cluster_reducers():
    return [k.rpartition(".")[-1] for k, v in PLUGINS.iteritems() if v["cluster_reducers"]]


def single_reducers():
    return [k.rpartition(".")[-1] for k, v in PLUGINS.iteritems() if not v["cluster_reducers"]]


def load(package_name, pattern_list=None):
    loaded = load_package(package_name, pattern_list)
    build_filter_map()
    return loaded


def build_filter_map():
    for name, plugins in MAPPERS.iteritems():
        filter_list = [f for plugin in plugins for f in plugin.filters]
        # TODO: Make all large files filtered so we can test for the thing below
        # if data_spec_config.is_large(name) and len(filter_list) == 0:
        #     raise Exception("Registering %s requires specifying at least one filter" % name)
        NAME_TO_FILTER_MAP[name] = set(filter_list)


def get_name(plugin):
    return plugin.__module__.rpartition(".")[-1]


def add_to_map(name, handler, filters, shared=False):

    handler.shared = shared or "falafel.mappers" in handler.__module__
    if handler.shared:
        SHARED_MAPPERS.append(handler)

    MAPPERS[name].append(handler)

    handler.filters = filters if filters else []

    plugin_name = "{0}.{1}".format(handler.__module__, handler.__name__)
    SYMBOLIC_NAME_FILTER_MAPPING[name][bool(filters)].append(plugin_name)


def get_mappers(name, mapping=MAPPERS):
    return mapping.get(name, [])


def inject_host(r, host):
    if isinstance(r, types.StringTypes):
        return {r: host}
    elif isinstance(r, types.DictType):
        keys = r.keys()
        if len(keys) != 1:
            raise Exception("Cluster mapper response can't have multiple keys")
        mapper_key = keys[0]
        if not isinstance(r[mapper_key], types.DictType):
            v = r[mapper_key]
            r[mapper_key] = {"value": v}
        r[mapper_key]["host"] = host
        return r


def register_cluster_mapper(path, func, filters=[]):
    @wraps(func)
    def host_inject_wrapper(context):
        r = func(context)
        return inject_host(r, context.hostname) if r else None
    register_mapper(path, host_inject_wrapper, filters)


def register_mapper(name, func, filters=None, shared=False):
    '''
    Associate a mapping function to a sosreport file.

    .. py:attribute:: name

       The alias used to identify the sosreport file ``func`` will process.

    .. py:attribute:: func

       Mapper function which will process the file identified by ``name``.

    .. py:attribute:: filters

       Strings used to identify (and filter) lines from large format files
       that the plugin requires.  These filters are used to created
       uploader server lists used to filter out non-matching lines from being
       collected during a client upload.

    .. py:attribute:: shared

       Mapper function will be added to the shared mapper namespace. The output
       of this mapper will be available to all reducers.

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
        MAPPER_FUNCS[func.serializable_id] = func
        p = PLUGINS[func.__module__]
        p["mappers"].append(func)
        p["module"] = func.__module__

        # Need to add already-registered reducers defined in same module to consumer list
        # Should only happen if a @reducer is defined above a @mapper in the same module
        f_module = func.__module__
        for r in [r for r in REDUCERS.values() if r.__module__ == f_module]:
            func.consumers.add(r)
        func._requires = set()
        func._reducer = False
    except Exception:
        log.exception("Failed to register mapper: %s", func.__name__)
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


def mapper(filename, filters=[], shared=False):
    """
    Convenience decorator for mapper callables.

    :param str filename: symbolic name of the file to register against
    :param list filters: list of plain strings that should be kept when removing
        lines from a large-format file

    Registering a mapper for /var/log/messages ::

      @mapper('messages', ['interesting_plain_text_indicator'])
      def my_func(context):
          pass

    Registering a mapper for dmidecode ::

      @mapper('dmidecode')
      def my_func(context):
          pass

    """
    def _register(func):
        register_mapper(filename, func, filters, shared=shared)
        return func

    return _register


def cluster_mapper(filename, filters=[]):
    """
    Convenience decorator for mapper callables in clustered modules.

    See the mapper decorator for a description of parameters and registration.

    Since cluster reducers need to be host-aware, mappers need to include
    the hostname in all responses so the reducer can differentiate between
    hosts.  This can be cumbersome, therefore the @cluster_mapper has been
    added.  It will inject the hostname into the response returned from a
    mapper that uses the @cluster_mapper decorator.

    There are three cases based on what type is returned by a mapper:

    1. String e.g. "FOOBAR" -> {
    "FOOBAR": hostname
    }
    2. Shallow map e.g. {"FOO": "BAR"} -> {
    "FOO": {"host": hostname, "value": "BAR"}
    }
    3. Deep map e.g. {"FOO": {"BAR": 1, "BAZ": 2}} -> {
    "FOO": {"host": hostname, "FOO": 1, "BAZ": 2}
    }

    NOTE: Mapper shallow dict responses must only have one key, which
    represents a sort of "mapper key" to be later referenced in the reducer.
    If multiple keys are used, an error will be thrown.
    """
    def _register(func):
        register_cluster_mapper(filename, func, filters)
        return func

    return _register


def visit_mappers(root, visitor=None):
    """
    Call visitor on all mappers reachable from root.

    :param function root: non shared reducer function
    :param function visitor: function to call on each mapper that is
        reachable as a dependency of root.

    Returns root's dependency tree.
    """

    # ensure root is a non-shared reducer
    if not root._reducer or root.shared:
        log.warn("Tried to visit mapper or shared reducer as visitor %s", root)
        return

    def _visit_mappers(parent, deps, visitor):
        if not parent._requires or not parent._reducer:
            return deps
        for r in parent._requires:
            if not r._reducer:
                if visitor:
                    visitor(r)
                deps[r] = 1
            elif r.shared:
                deps[r] = _visit_mappers(r, {}, visitor)
        return deps

    deps = _visit_mappers(root, {}, visitor)

    # Non-shared mappers defined in same module are implicitly consumed
    root_module = root.__module__
    for mappers in MAPPERS.values():
        for m in mappers:
            if m.__module__ == root_module:
                if visitor:
                    visitor(m)
                deps[m] = 1
    return deps


def generate_dependency_tree(f):
    """
    Generate the dependency tree of non shared reducer f.

    This is currently only used for debugging.
    """

    return visit_mappers(f)


def register_consumer(c):
    """ Register non shared reducers as consumers of mappers. """

    def register(mapper):
        mapper.consumers.add(c)

    visit_mappers(c, register)


def reducer(requires=None, optional=None, cluster=False, shared=False):
    def _f(func):
        @wraps(func)
        def __f(local, shared):
            missing_requirements = get_missing_requirements(requires, shared)
            if not requires or not missing_requirements:
                if cluster:
                    return func(box(local), shared)
                else:
                    return func(local, shared)
            else:
                log.debug("Reducer [%s] is missing requirements: %s",
                          func.__module__,
                          stringify_requirements(missing_requirements))
        if cluster:
            register_cluster_reducer(__f)
        else:
            register_reducer(__f)

        if requires:
            _all, _any = split_requirements(requires)
            __f._any = _any
            _all = set(_all)
            _any = set(i for o in _any for i in o)
        else:
            __f._any = []
            _all, _any = set(), set()
        _optional = set(optional) if optional else set()
        __f._all, __f._optional = _all, _optional
        __f._requires = (_all | _any | _optional)
        __f.shared = shared
        __f.cluster = cluster
        __f._reducer = True
        if not shared:
            register_consumer(__f)
            __f._dependency_tree = generate_dependency_tree(__f)
        return __f
    return _f


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
    r.update(kwargs)
    return r


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
