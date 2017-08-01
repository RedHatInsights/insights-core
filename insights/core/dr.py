"""
This module implements dependency resolution and execution within Red Hat Insights.
"""

import importlib
import inspect
import logging
import pkgutil
import re
import six
import sys
import time
import traceback

from collections import defaultdict
from functools import reduce as _reduce
from insights.contrib.toposort import toposort_flatten
from insights.util import enum

log = logging.getLogger(__name__)

GROUPS = enum("cluster", "single")

MODULE_NAMES = {}
SIMPLE_MODULE_NAMES = {}

TYPE_OBSERVERS = defaultdict(set)

ALIASES = {}
COMPONENT_METADATA = {}
TYPE_OF_COMPONENT = {}
COMPONENTS_BY_TYPE = defaultdict(set)
DEPENDENCIES = defaultdict(set)
DEPENDENTS = defaultdict(set)
COMPONENTS = defaultdict(lambda: defaultdict(set))
GROUP_OF_COMPONENT = {}
COMPONENT_NAME_CACHE = {}

DELEGATES = {}
HIDDEN = set()

ANY_TYPE = object()


def get_component(name):
    """ Returns a class or function specified by the fully qualified name string."""
    try:
        if name not in COMPONENT_NAME_CACHE:
            mod, _, name = name.rpartition(".")
            importlib.import_module(mod)
            COMPONENT_NAME_CACHE[name] = getattr(sys.modules[mod], name)

        return COMPONENT_NAME_CACHE[name]
    except:
        pass


def add_observer(o, _type=ANY_TYPE):
    TYPE_OBSERVERS[_type].add(o)


def observer(_type=ANY_TYPE):
    def inner(func):
        add_observer(func, _type)
        return func
    return inner


class MissingRequirements(Exception):
    def __init__(self, requirements):
        self.requirements = requirements
        super(MissingRequirements, self).__init__(requirements)


class SkipComponent(Exception):
    pass


def get_name(component):
    if six.callable(component):
        return '.'.join([component.__module__, component.__name__])
    return str(component)


def get_simple_name(component):
    if six.callable(component):
        return component.__name__
    return str(component)


def get_metadata(component):
    return COMPONENT_METADATA.get(component, {})


def get_module_name(obj):
    try:
        return inspect.getmodule(obj).__name__
    except:
        return None


def get_simple_module_name(obj):
    try:
        return get_module_name(obj).split(".")[-1]
    except:
        return None


def mark_hidden(component):
    global HIDDEN
    if isinstance(component, (list, set)):
        HIDDEN |= set(component)
    else:
        HIDDEN.add(component)


def is_hidden(component):
    return component in HIDDEN


# TODO: review global vars
def replace(old, new):
    _type = TYPE_OF_COMPONENT[old]
    _group = GROUP_OF_COMPONENT[old]

    for k, v in DEPENDENTS.items():
        if old in v:
            v.discard(old)
            v.add(new)

    for d in DEPENDENTS[old]:
        DEPENDENCIES[_group][d].discard(old)
        DEPENDENCIES[_group][d].add(new)

    COMPONENTS_BY_TYPE[_type].discard(old)

    del ALIASES[old]
    del COMPONENT_METADATA[old]
    del DEPENDENTS[old]
    del GROUP_OF_COMPONENT[old]
    del DEPENDENCIES[_group][old]
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
        for d in DEPENDENCIES[parent]:
            visitor(d, parent)
            visit(d, visitor)

    visitor(root, None)
    visit(root, visitor)


def get_dependency_graph(component):
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
    keys = set(graph)
    frontier = set()
    seen = set()
    while keys:
        frontier.add(keys.pop())
        while frontier:
            component = frontier.pop()
            seen.add(component)
            frontier |= set([d for d in DEPENDENCIES[component] if d in graph])
            frontier |= set([d for d in DEPENDENTS[component] if d in graph])
            frontier -= seen
        yield dict((s, DEPENDENCIES[s]) for s in seen)
        keys -= seen
        seen.clear()


def load_components(path, include=".*", exclude="test"):
    include = re.compile(include).search if include else lambda x: True
    exclude = re.compile(exclude).search if exclude else lambda x: False
    prefix = path.replace('/', '.') + '.'
    for _, name, _ in pkgutil.walk_packages(path=[path], prefix=prefix):
        if include(name) and not exclude(name):
            log.debug("Importing %s" % name)
            importlib.import_module(name)


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
    req_all, req_any = split_requirements(requires)
    pretty_all = [get_name(r) for r in req_all]
    pretty_any = [str([get_name(r) for r in any_list]) for any_list in req_any]
    result = "All: %s" % pretty_all + " Any: " + " Any: ".join(pretty_any)
    return result


def register_component(component, delegate, component_type,
        requires=None, optional=None, group=GROUPS.single, alias=None, metadata={}):

    if requires:
        _all, _any = split_requirements(requires)
        _all = set(_all)
        _any = set(i for o in _any for i in o)
    else:
        _all, _any = set(), set()
    _optional = set(optional) if optional else set()

    dependencies = _all | _any | _optional
    for d in dependencies:
        DEPENDENTS[d].add(component)

    DEPENDENCIES[component] |= dependencies
    COMPONENTS[group][component] |= dependencies

    TYPE_OF_COMPONENT[component] = component_type
    GROUP_OF_COMPONENT[component] = group
    COMPONENTS_BY_TYPE[component_type].add(component)
    DELEGATES[component] = delegate
    MODULE_NAMES[component] = get_module_name(component)
    SIMPLE_MODULE_NAMES[component] = get_simple_module_name(component)
    COMPONENT_METADATA[component] = metadata

    if alias:
        msg = "Alias %s already registered!"
        if alias in ALIASES:
            raise Exception(msg % alias)
        if component in ALIASES:
            raise Exception(msg % get_name(component))

        ALIASES[alias] = component
        ALIASES[component] = alias


class Broker(object):
    def __init__(self, cleanup=False):
        self.instances = {}
        self.missing_dependencies = {}
        self.exceptions = defaultdict(list)
        self.tracebacks = {}
        self.exec_times = {}

        self.observers = defaultdict(set)
        self.observers[ANY_TYPE] = set()
        for k, v in TYPE_OBSERVERS.items():
            self.observers[k] = set(v)

    def observer(self, _type=ANY_TYPE):
        def inner(func):
            self.add_observer(func, _type)
            return func
        return inner

    def add_observer(self, o, _type=ANY_TYPE):
        self.observers[_type].add(o)

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
            self.missing_dependencies[component] = ex.requirements
        else:
            self.exceptions[component].append(ex)
            self.tracebacks[ex] = tb

    def keys(self):
        return self.instances.keys()

    def items(self):
        return self.instances.items()

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
    d = set(d.keys())
    req_all = [r for r in req_all if r not in d]
    req_any = [r for r in req_any if set(r).isdisjoint(d)]
    if req_all or req_any:
        return req_all, req_any
    else:
        return None


def default_executor(func, broker, requires=[], optional=[]):
    missing_requirements = get_missing_requirements(requires, broker)
    if missing_requirements:
        raise MissingRequirements(missing_requirements)
    return func(broker)


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

    def decorator(requires=None,
                  optional=None,
                  group=group,
                  executor=executor,
                  alias=None,
                  metadata={}):
        requires = requires or []
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

            register_component(func, __f, decorator,
                               requires=requires,
                               optional=optional,
                               group=group,
                               alias=alias,
                               metadata=component_metadata)
            return func
        return _f

    if name:
        decorator.__name__ = name
    return decorator


def run_order(components, broker):
    """ Returns components in an order that satisfies their dependency
        relationships.
    """
    return toposort_flatten(components)


def run(components, broker=None):
    """ Executes components in an order that satisfies their dependency
        relationships.
    """
    broker = broker or Broker()

    for component in run_order(components, broker):
        try:
            if component not in broker and component in DELEGATES:
                log.info("Calling %s" % get_name(component))

                start = time.time()
                result = DELEGATES[component](broker)
                broker.exec_times[component] = time.time() - start
                broker[component] = result
        except MissingRequirements as mr:
            broker.add_exception(component, mr)
        except SkipComponent:
            log.debug(traceback.format_exc())
        except Exception as ex:
            log.debug(ex)
            broker.add_exception(component, ex, traceback.format_exc())
        finally:
            broker.fire_observers(component)

    return broker


def run_incremental(components, broker=None):
    """ Executes components in an order that satisfies their dependency
        relationships. Disjoint subgraphs are executed one at a time and
        a broker containing the results for each is yielded. If a broker
        is passed here, its instances are used to seed the broker used
        to run each subgraph.
    """
    seed_broker = broker or Broker()
    for graph in get_subgraphs(components):
        broker = Broker()
        broker.instances = dict(seed_broker.instances)
        yield run(graph, broker)
