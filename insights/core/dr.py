"""
This module implements dependency resolution and execution within Red Hat Insights.
"""

import inspect
import logging
import os
import pkgutil
import re
import six
import sys
import time
import traceback

from collections import defaultdict
from functools import reduce as _reduce
from insights.contrib import importlib
from insights.contrib.toposort import toposort_flatten
from insights.util import enum

try:
    from insights.core import fava
except:
    fava = None

log = logging.getLogger(__name__)

GROUPS = enum("single", "cluster")

MODULE_NAMES = {}
BASE_MODULE_NAMES = {}

TYPE_OBSERVERS = defaultdict(set)

ADDED_DEPENDENCIES = defaultdict(list)
ALIASES_BY_COMPONENT = {}
ALIASES = {}
COMPONENT_METADATA = {}
TYPE_OF_COMPONENT = {}
COMPONENTS_BY_TYPE = defaultdict(set)
DEPENDENCIES = defaultdict(set)
DEPENDENTS = defaultdict(set)
COMPONENTS = defaultdict(lambda: defaultdict(set))
GROUP_OF_COMPONENT = {}

DELEGATES = {}
HIDDEN = set()

ANY_TYPE = object()
COMPONENT_NAME_CACHE = {}


def resolve_alias(c):
    return ALIASES.get(c, c)


def resolve_aliases(graph):
    if isinstance(graph, dict):
        g = {}
        for k, v in graph.items():
            g[k] = set(resolve_alias(d) for d in v)
        return g

    if isinstance(graph, list):
        return [resolve_alias(c) for c in graph]

    if isinstance(graph, set):
        return set(resolve_alias(c) for c in graph)

    return resolve_alias(graph)


def get_alias(component):
    return ALIASES_BY_COMPONENT.get(component)


def _get_from_module(name):
    mod, _, n = name.rpartition(".")
    if mod not in sys.modules:
        importlib.import_module(mod)
    return getattr(sys.modules[mod], n)


def _get_from_class(name):
    mod, _, n = name.rpartition(".")
    cls = _get_from_module(mod)
    return getattr(cls, n)


def get_component(name):
    """ Returns a class, function, or class method specified by the fully
        qualified name string.
    """
    if name in COMPONENT_NAME_CACHE:
        return COMPONENT_NAME_CACHE[name]

    try:
        COMPONENT_NAME_CACHE[name] = _get_from_module(name)
    except:
        try:
            COMPONENT_NAME_CACHE[name] = _get_from_class(name)
        except:
            log.debug("Couldn't load %s" % name)
            COMPONENT_NAME_CACHE[name] = None
    return COMPONENT_NAME_CACHE[name]


def get_component_type(component):
    component = resolve_alias(component)
    return TYPE_OF_COMPONENT.get(component)


def get_group(component):
    component = resolve_alias(component)
    return GROUP_OF_COMPONENT.get(component)


def get_dependencies(component):
    component = resolve_alias(component)
    return set(resolve_alias(d) for d in DEPENDENCIES.get(component, set()))


def get_dependents(component):
    deps = set(resolve_alias(d) for d in DEPENDENTS.get(component, set()))
    if component in ALIASES:
        deps |= get_dependents(ALIASES[component])
    return deps


def add_dependency(component, dep):
    DEPENDENTS[dep].add(component)
    DEPENDENCIES[component].add(dep)
    ADDED_DEPENDENCIES[component].append(dep)


def get_added_dependencies(component):
    return ADDED_DEPENDENCIES.get(component, [])


def add_observer(o, component_type=ANY_TYPE):
    TYPE_OBSERVERS[component_type].add(o)


def observer(component_type=ANY_TYPE):
    def inner(func):
        add_observer(func, component_type)
        return func
    return inner


class MissingRequirements(Exception):
    def __init__(self, requirements):
        self.requirements = requirements
        super(MissingRequirements, self).__init__(requirements)


class SkipComponent(Exception):
    """ This class should be raised by components that want to be taken out of
        dependency resolution.
    """
    pass


def get_name(component):
    component = resolve_alias(component)
    if six.callable(component):
        if hasattr(component, "__qualname__"):
            return component.__qualname__
        return '.'.join([component.__module__, component.__name__])
    return str(component)


def get_simple_name(component):
    component = resolve_alias(component)
    if six.callable(component):
        return component.__name__
    return str(component)


def get_metadata(component):
    component = resolve_alias(component)
    return COMPONENT_METADATA.get(component, {})


def get_module_name(obj):
    try:
        return inspect.getmodule(obj).__name__
    except:
        return None


def get_base_module_name(obj):
    try:
        return get_module_name(obj).split(".")[-1]
    except:
        return None


def mark_hidden(component):
    global HIDDEN
    if isinstance(component, (list, set)):
        HIDDEN |= set(resolve_alias(c) for c in component)
    else:
        component = resolve_alias(component)
        HIDDEN.add(component)


def is_hidden(component):
    component = resolve_alias(component)
    return component in HIDDEN


def replace(old, new):
    _type = TYPE_OF_COMPONENT[old]
    _group = GROUP_OF_COMPONENT[old]

    for k, v in DEPENDENTS.items():
        if old in v:
            v.discard(old)
            v.add(new)

    for d in DEPENDENTS[old]:
        DEPENDENCIES[d].discard(old)
        DEPENDENCIES[d].add(new)

    COMPONENTS_BY_TYPE[_type].discard(old)
    COMPONENT_NAME_CACHE[get_name(new)] = new

    if old in ALIASES_BY_COMPONENT:
        a = ALIASES_BY_COMPONENT[old]
        del ALIASES_BY_COMPONENT[old]
        del ALIASES[a]

    if old in DEPENDENTS:
        del DEPENDENTS[old]

    if old in ADDED_DEPENDENCIES:
        deps = ADDED_DEPENDENCIES[old]
        del ADDED_DEPENDENCIES[old]
        ADDED_DEPENDENCIES[new] = deps

    HIDDEN.discard(old)

    del COMPONENT_METADATA[old]
    del GROUP_OF_COMPONENT[old]
    del DEPENDENCIES[old]
    del COMPONENTS[_group][old]
    del TYPE_OF_COMPONENT[old]
    del DELEGATES[old]


def walk_dependencies(root, visitor):
    """ Call visitor on root and all dependencies reachable from it in breadth
        first order.

        :param component root: component function or class
        :param function visitor: signature is `func(component, parent)`.
            The call on root is `visitor(root, None)`.
    """
    def visit(parent, visitor):
        for d in get_dependencies(parent):
            visitor(d, parent)
            visit(d, visitor)

    visitor(root, None)
    visit(root, visitor)


def get_dependency_graph(component):
    component = resolve_alias(component)
    if component not in DEPENDENCIES:
        raise Exception("%s is not a registered component." % get_name(component))

    if not DEPENDENCIES[component]:
        return {component: set()}

    graph = defaultdict(set)

    def visitor(c, parent):
        if parent is not None:
            graph[parent].add(c)

    walk_dependencies(component, visitor)

    graph = dict(graph)

    # Find all items that don't depend on anything.
    extra_items_in_deps = _reduce(set.union, graph.values(), set()) - set(graph.keys())

    # Add empty dependences where needed.
    graph.update(dict((item, set()) for item in extra_items_in_deps))

    return graph


def get_subgraphs(graph=DEPENDENCIES):
    graph = resolve_aliases(graph)
    keys = set(graph)
    frontier = set()
    seen = set()
    while keys:
        frontier.add(keys.pop())
        while frontier:
            component = frontier.pop()
            seen.add(component)
            frontier |= set([d for d in get_dependencies(component) if d in graph])
            frontier |= set([d for d in get_dependents(component) if d in graph])
            frontier -= seen
        yield dict((s, get_dependencies(s)) for s in seen)
        keys -= seen
        seen.clear()


def _import(path, continue_on_error):
    log.debug("Importing %s" % path)
    try:
        return importlib.import_module(path)
    except Exception as ex:
        log.exception(ex)
        if not continue_on_error:
            raise


def load_components(path, include=".*", exclude="test", continue_on_error=True):
    num_loaded = 0
    if path.endswith((".py", ".fava")):
        path, _ = os.path.splitext(path)

    path = path.rstrip("/").replace("/", ".")

    package = _import(path, continue_on_error)
    if not package:
        return 0

    num_loaded += 1

    do_include = re.compile(include).search if include else lambda x: True
    do_exclude = re.compile(exclude).search if exclude else lambda x: False

    if not hasattr(package, "__path__"):
        return num_loaded

    prefix = package.__name__ + "."
    for _, name, is_pkg in pkgutil.iter_modules(path=package.__path__, prefix=prefix):
        if not name.startswith(prefix):
            name = prefix + name
        if do_include(name) and not do_exclude(name):
            if is_pkg:
                num_loaded += load_components(name, include, exclude, continue_on_error)
            else:
                _import(name, continue_on_error)
                num_loaded += 1

    return num_loaded


def first_of(dependencies, broker):
    for d in dependencies:
        if d in broker:
            return broker[d]


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
    pretty_all = [get_name(r) for r in req_all]
    pretty_any = [str([get_name(r) for r in any_list]) for any_list in req_any]
    result = "All: %s" % pretty_all + " Any: " + " Any: ".join(pretty_any)
    return result


def register_component(component, delegate, component_type,
                       requires=None,
                       optional=None,
                       group=GROUPS.single,
                       alias=None,
                       metadata={}):

    if requires:
        _all, _any = split_requirements(requires)
        _all = set(_all)
        _any = set(i for o in _any for i in o)
    else:
        _all, _any = set(), set()
    _optional = set(optional) if optional else set()

    dependencies = _all | _any | _optional
    dependencies = set(resolve_alias(d) for d in dependencies)
    for d in dependencies:
        DEPENDENTS[d].add(component)

    DEPENDENCIES[component] |= dependencies
    COMPONENTS[group][component] |= dependencies

    TYPE_OF_COMPONENT[component] = component_type
    GROUP_OF_COMPONENT[component] = group
    COMPONENTS_BY_TYPE[component_type].add(component)
    DELEGATES[component] = delegate
    MODULE_NAMES[component] = get_module_name(component)
    BASE_MODULE_NAMES[component] = get_base_module_name(component)
    COMPONENT_METADATA[component] = metadata

    if fava:
        fava.add_shared_parser(component.__name__, component)

    if alias:
        msg = "%s replacing alias '%s' registered to %s."
        if alias in ALIASES:
            log.info(msg % (get_name(component), alias, get_name(ALIASES[alias])))

        ALIASES[alias] = component
        ALIASES_BY_COMPONENT[component] = alias

    name = get_name(component)
    if name.startswith("__main__."):
        old = COMPONENT_NAME_CACHE.get(name)
        if old:
            replace(old, component)
        else:
            COMPONENT_NAME_CACHE[name] = component


class Broker(object):
    def __init__(self, seed_broker=None):
        self.instances = dict(seed_broker.instances) if seed_broker else {}
        self.missing_requirements = {}
        self.exceptions = defaultdict(list)
        self.tracebacks = {}
        self.exec_times = {}

        self.observers = defaultdict(set)
        self.observers[ANY_TYPE] = set()
        for k, v in TYPE_OBSERVERS.items():
            self.observers[k] = set(v)

    def observer(self, component_type=ANY_TYPE):
        def inner(func):
            self.add_observer(func, component_type)
            return func
        return inner

    def add_observer(self, o, component_type=ANY_TYPE):
        self.observers[component_type].add(o)

    def fire_observers(self, component):
        _type = TYPE_OF_COMPONENT.get(component, None)
        if not _type:
            return

        for o in self.observers.get(_type, set()) | self.observers[ANY_TYPE]:
            try:
                o(component, self)
            except Exception as e:
                log.exception(e)

    def add_exception(self, component, ex, tb=None):
        if isinstance(ex, MissingRequirements):
            self.missing_requirements[component] = ex.requirements
        else:
            self.exceptions[component].append(ex)
            self.tracebacks[ex] = tb

    def keys(self):
        return self.instances.keys()

    def items(self):
        return self.instances.items()

    def get_by_type(self, _type):
        r = {}
        for k, v in self.items():
            if get_component_type(k) is _type:
                r[k] = v
        return r

    def __contains__(self, component):
        if component in self.instances:
            return True

        alias = ALIASES.get(component)

        if alias and alias in self.instances:
            return True
        return False

    def __setitem__(self, component, instance):
        msg = "Already exists in broker with key: %s"
        if component in self.instances:
            raise KeyError(msg % get_name(component))

        alias = ALIASES.get(component)
        if alias and alias in self.instances:
            raise KeyError(msg % get_name(alias))

        self.instances[component] = instance

    def __delitem__(self, component):
        if component in self.instances:
            del self.instances[component]
            return

        alias = ALIASES.get(component)
        if alias and alias in self.instances:
            del self.instances[alias]

    def __getitem__(self, component):
        if component in self.instances:
            return self.instances[component]

        alias = ALIASES.get(component)
        if alias and alias in self.instances:
            return self.instances[alias]

        raise KeyError("Unknown component: %s" % get_name(component))

    def get(self, component, default=None):
        try:
            return self[component]
        except KeyError:
            return default


def get_missing_requirements(requires, d):
    if not requires:
        return None
    req_all, req_any = split_requirements(requires)
    req_all = resolve_aliases(req_all)
    req_any = [resolve_aliases(c) for c in req_any]
    d = set(d.keys())
    req_all = [r for r in req_all if r not in d]
    req_any = [r for r in req_any if set(r).isdisjoint(d)]
    if req_all or req_any:
        return req_all, req_any
    else:
        return None


def broker_executor(func, broker, requires=[], optional=[]):
    missing_requirements = get_missing_requirements(requires, broker)
    if missing_requirements:
        raise MissingRequirements(missing_requirements)
    return func(broker)


def default_executor(func, broker, requires=[], optional=[]):
    """ Use this executor if your component signature matches your
        dependency list. Can be used on individual components or
        in component type definitions.
    """
    missing_requirements = get_missing_requirements(requires, broker)
    if missing_requirements:
        raise MissingRequirements(missing_requirements)
    args = []
    for r in requires:
        if isinstance(r, list):
            args.extend(r)
        else:
            args.append(r)
    args.extend(optional)
    args = [broker.get(a) for a in args]
    return func(*args)


def new_component_type(name=None,
                       auto_requires=[],
                       auto_optional=[],
                       group=GROUPS.single,
                       executor=default_executor,
                       type_metadata={}):
    """ Factory that creates component decorators.

        The functions this factory produces are decorators for parsers, combiners,
        rules, cluster rules, etc.

        Args:
            name (str): the name of the component type the produced decorator
                will define
            auto_requires (list): All decorated components automatically have
                this requires spec. Anything specified when decorating a component
                is added to this spec.
            auto_optional (list): All decorated components automatically have
                this optional spec. Anything specified when decorating a component
                is added to this spec.
            group (type): any symbol to group this component with similar components
                in the dependency list. This will be used when calling run to
                select the set of components to be executed: run(COMPONENTS[group])
            executor (func): an optional function that controls how a component is
                executed. It can impose restrictions on return value types, perform
                component type specific exception handling, etc. The signature is
                `executor(component, broker, requires=?, optional=?)`.
                The default behavior is to call `default_executor`.
            type_metadata (dict): an arbitrary dictionary to associate with all
                components of this type.

        Returns:
            A decorator function used to define components of the new type.
    """

    def decorator(*requires, **kwargs):
        optional = kwargs.get("optional", None)
        the_group = kwargs.get("group", group)
        alias = kwargs.get("alias", None)
        component_type = kwargs.get("component_type", None)
        metadata = kwargs.get("metadata", {})

        requires = list(requires) or kwargs.get("requires", [])
        optional = optional or []

        requires.extend(auto_requires)
        optional.extend(auto_optional)

        component_metadata = {}
        component_metadata.update(type_metadata)
        component_metadata.update(metadata)

        def _f(func):
            @six.wraps(func)
            def __f(broker):
                return executor(func, broker, requires, optional)

            register_component(func, __f, component_type or decorator,
                               requires=requires,
                               optional=optional,
                               group=the_group,
                               alias=alias,
                               metadata=component_metadata)
            return func
        return _f

    if name:
        decorator.__name__ = name
        s = inspect.stack()
        frame = s[1][0]
        mod = inspect.getmodule(frame) or sys.modules.get("__main__")
        if mod:
            decorator.__module__ = mod.__name__
            setattr(mod, name, decorator)

    return decorator


def run_order(components, broker):
    """ Returns components in an order that satisfies their dependency
        relationships.
    """
    return toposort_flatten(resolve_aliases(components))


def run(components=COMPONENTS[GROUPS.single], broker=None):
    """ Executes components in an order that satisfies their dependency
        relationships.
    """
    broker = broker or Broker()

    for component in run_order(components, broker):
        start = time.time()
        try:
            if component not in broker and component in DELEGATES:
                log.info("Trying %s" % get_name(component))
                result = DELEGATES[component](broker)
                broker[component] = result
        except MissingRequirements as mr:
            if log.isEnabledFor(logging.DEBUG):
                name = get_name(component)
                reqs = stringify_requirements(mr.requirements)
                log.debug("%s missing requirements %s" % (name, reqs))
            broker.add_exception(component, mr)
        except SkipComponent:
            if log.isEnabledFor(logging.DEBUG):
                log.debug("%s raised SkipComponent" % get_name(component))
        except Exception as ex:
            if log.isEnabledFor(logging.DEBUG):
                log.debug(ex)
            broker.add_exception(component, ex, traceback.format_exc())
        finally:
            broker.exec_times[component] = time.time() - start
            broker.fire_observers(component)

    return broker


def run_incremental(components=COMPONENTS[GROUPS.single], broker=None):
    """ Executes components in an order that satisfies their dependency
        relationships. Disjoint subgraphs are executed one at a time and
        a broker containing the results for each is yielded. If a broker
        is passed here, its instances are used to seed the broker used
        to hold state for each sub graph.
    """
    seed_broker = broker or Broker()
    for graph in get_subgraphs(components):
        broker = Broker(seed_broker)
        yield run(graph, broker)
