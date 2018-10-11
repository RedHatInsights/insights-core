"""
This module implements dependency resolution and execution within Red Hat Insights.
"""
from __future__ import print_function

import inspect
import logging
import json
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
from insights.util import defaults, enum, KeyPassingDefaultDict

log = logging.getLogger(__name__)

GROUPS = enum("single", "cluster")

MODULE_NAMES = {}
BASE_MODULE_NAMES = {}

TYPE_OBSERVERS = defaultdict(set)

COMPONENTS_BY_TYPE = defaultdict(set)
DEPENDENCIES = defaultdict(set)
DEPENDENTS = defaultdict(set)
COMPONENTS = defaultdict(lambda: defaultdict(set))

DELEGATES = {}
HIDDEN = set()
IGNORE = defaultdict(set)
ENABLED = defaultdict(lambda: True)


def set_enabled(component, enabled=True):
    """
    Enable a component for evaluation. If set to False, the component is
    skipped, and all components that require it will not execute. If component
    is a fully qualified name string of a callable object instead of the
    callable object itself, the component's module is loaded as a side effect
    of calling this function.

    Args:
        component (str or callable): fully qualified name of the component or
            the component object itself.
        enabled (bool): whether the component is enabled for evaluation.

    Returns:
        None
    """
    ENABLED[get_component(component) or component] = enabled


def is_enabled(component):
    """
    Check to see if a component is enabled.

    Args:
        component (callable): The component to check. The component must
        already be loaded.

    Returns:
        True if the component is enabled. False otherwise.
    """
    return ENABLED[component]


def get_delegate(component):
    return DELEGATES.get(component)


def add_ignore(c, i):
    IGNORE[c].add(i)


def hashable(v):
    try:
        hash(v)
    except:
        return False
    return True


def _get_from_module(name):
    mod, _, n = name.rpartition(".")
    if mod not in sys.modules:
        importlib.import_module(mod)
    return getattr(sys.modules[mod], n)


def _get_from_class(name):
    mod, _, n = name.rpartition(".")
    cls = _get_from_module(mod)
    return getattr(cls, n)


def _get_component(name):
    """
    Returns a class, function, or class method specified by the fully qualified
    name.
    """
    for f in (_get_from_module, _get_from_class):
        try:
            return f(name)
        except:
            pass
    log.debug("Couldn't load %s" % name)


COMPONENT_NAME_CACHE = KeyPassingDefaultDict(_get_component)
get_component = COMPONENT_NAME_CACHE.__getitem__


@defaults(None)
def get_component_type(component):
    return get_delegate(component).type


def get_components_of_type(_type):
    return COMPONENTS_BY_TYPE.get(_type)


@defaults(None)
def get_group(component):
    return get_delegate(component).group


def add_dependent(component, dep):
    DEPENDENTS[component].add(dep)


def get_dependents(component):
    return DEPENDENTS.get(component, set())


@defaults(set())
def get_dependencies(component):
    return get_delegate(component).get_dependencies()


def add_dependency(component, dep):
    get_delegate(component).add_dependency(dep)


class MissingRequirements(Exception):
    def __init__(self, requirements):
        self.requirements = requirements
        super(MissingRequirements, self).__init__(requirements)


class SkipComponent(Exception):
    """
    This class should be raised by components that want to be taken out of
    dependency resolution.
    """
    pass


def get_name(component):
    if six.callable(component):
        name = getattr(component, "__qualname__", component.__name__)
        return '.'.join([component.__module__, name])
    return str(component)


def get_simple_name(component):
    if six.callable(component):
        return component.__name__
    return str(component)


def get_metadata(component):
    return get_delegate(component).metadata if component in DELEGATES else {}


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
        HIDDEN |= set(component)
    else:
        HIDDEN.add(component)


def is_hidden(component):
    return component in HIDDEN


def walk_tree(root, method=get_dependencies):
    for d in method(root):
        yield d
        for c in walk_tree(d, method=method):
            yield c


def walk_dependencies(root, visitor):
    """
    Call visitor on root and all dependencies reachable from it in breadth
    first order.

    Args:
        root (component): component function or class
        visitor (function): signature is `func(component, parent)`.  The
            call on root is `visitor(root, None)`.
    """
    def visit(parent, visitor):
        for d in get_dependencies(parent):
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

    # Add empty dependencies where needed.
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


def _load_components(path, include=".*", exclude="test", continue_on_error=True):
    num_loaded = 0
    if path.endswith(".py"):
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
        if is_pkg:
            num_loaded += _load_components(name, include, exclude, continue_on_error)
        else:
            if do_include(name) and not do_exclude(name):
                _import(name, continue_on_error)
                num_loaded += 1

    return num_loaded


def load_components(*paths, **kwargs):
    """
    Loads all components on the paths. Each path should be a package or module.
    All components beneath a path are loaded.

    Args:
        paths (str): A package or module to load

    Keyword Args:
        include (str): A regular expression of packages and modules to include.
            Defaults to '.*'
        exclude (str): A regular expression of packges and modules to exclude.
            Defaults to 'test'
        continue_on_error (bool): If True, continue importing even if something
            raises an ImportError. If False, raise the first ImportError.

    Returns:
        int: The total number of modules loaded.

    Raises:
        ImportError
    """
    num_loaded = 0
    for path in paths:
        num_loaded += _load_components(path, **kwargs)
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


def register_component(delegate):
    component = delegate.component

    dependencies = delegate.get_dependencies()
    DEPENDENCIES[component] = dependencies
    COMPONENTS[delegate.group][component] |= dependencies

    COMPONENTS_BY_TYPE[delegate.type].add(component)
    for k, v in COMPONENTS_BY_TYPE.items():
        if issubclass(delegate.type, k) and delegate.type is not k:
            v.add(component)
    DELEGATES[component] = delegate

    MODULE_NAMES[component] = get_module_name(component)
    BASE_MODULE_NAMES[component] = get_base_module_name(component)


class ComponentType(object):
    """
    ComponentType is the base class for all component type decorators.
    """

    requires = []
    optional = []
    metadata = {}
    group = GROUPS.single

    def __init__(self, *deps, **kwargs):
        """
        This constructor is the parameterized part of a decorator.
        For Example:
            class my_component_type(ComponentType):
                pass

            # A my_component_type instance is created whose __call__ function
            # gets passed `my_func`.
            @my_component_type("I need this")
            def my_func(thing):
                return "stuff"

        Override it in a subclass if you want a specialized decorator interface,
        but always remember to invoke the super class constructor.
        """
        for k, v in kwargs.items():
            setattr(self, k, v)

        self.component = None
        self.requires = []
        self.at_least_one = []
        self.deps = []
        self.type = self.__class__

        deps = list(deps) or kwargs.get("requires", [])

        requires = list(self.__class__.requires) + deps
        for d in requires:
            if isinstance(d, list):
                self.at_least_one.append(d)
                self.deps.extend(d)
            else:
                self.requires.append(d)
                self.deps.append(d)

        self.optional = list(self.__class__.optional)
        optional = kwargs.get("optional", [])
        if optional and not isinstance(optional, list):
            optional = [optional]
        self.optional.extend(optional)

        self.deps.extend(self.optional)

        self.dependencies = set(self.deps)

        self.metadata = {}
        self.metadata.update(self.__class__.metadata)
        self.metadata.update(kwargs.get("metadata", {}) or {})

        self.group = kwargs.get("group", self.__class__.group)
        if kwargs.get("cluster", False):
            self.group = GROUPS.cluster

    def __call__(self, component):
        """
        This function is the part of the decorator that receives the function
        or class.
        """
        self.component = component
        self.__name__ = component.__name__
        self.__module__ = component.__module__
        self.__doc__ = component.__doc__
        self.__qualname__ = getattr(component, "__qualname__", None)
        for d in self.dependencies:
            add_dependent(d, component)
        register_component(self)
        return component

    def invoke(self, results):
        """
        Handles invocation of the component. The default implementation invokes
        it with positional arguments based on order of dependency declaration.
        """
        args = [results.get(d) for d in self.deps]
        return self.component(*args)

    def get_missing_dependencies(self, broker):
        """
        Gets required and at-least-one dependencies not provided by the broker.
        """
        missing_required = [r for r in self.requires if r not in broker]
        missing_at_least_one = [d for d in self.at_least_one if not set(d).intersection(broker)]
        if missing_required or missing_at_least_one:
            return (missing_required, missing_at_least_one)

    def process(self, broker):
        """
        Ensures dependencies have been met before delegating to `self.invoke`.
        """
        if any(i in broker for i in IGNORE.get(self.component, [])):
            raise SkipComponent()
        missing = self.get_missing_dependencies(broker)
        if missing:
            raise MissingRequirements(missing)
        return self.invoke(broker)

    def get_dependencies(self):
        return self.dependencies

    def add_dependency(self, dep):
        group = self.group
        self.at_least_one[0].append(dep)
        self.deps.append(dep)
        self.dependencies.add(dep)
        add_dependent(dep, self.component)

        DEPENDENCIES[self.component].add(dep)
        COMPONENTS[group][self.component].add(dep)


class Broker(object):
    def __init__(self, seed_broker=None):
        self.instances = dict(seed_broker.instances) if seed_broker else {}
        self.missing_requirements = {}
        self.exceptions = defaultdict(list)
        self.tracebacks = {}
        self.exec_times = {}

        self.observers = defaultdict(set)
        if seed_broker is not None:
            self.observers.update(seed_broker.observers)
        else:
            self.observers[ComponentType] = set()
            for k, v in TYPE_OBSERVERS.items():
                self.observers[k] |= set(v)

    def observer(self, component_type=ComponentType):
        def inner(func):
            self.add_observer(func, component_type)
            return func
        return inner

    def add_observer(self, o, component_type=ComponentType):
        self.observers[component_type].add(o)

    def fire_observers(self, component):
        _type = get_component_type(component)
        if not _type:
            return

        for k, v in self.observers.items():
            if issubclass(_type, k):
                for o in v:
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

    def __iter__(self):
        return iter(self.instances)

    def keys(self):
        return self.instances.keys()

    def items(self):
        return self.instances.items()

    def values(self):
        return self.instances.values()

    def get_by_type(self, _type):
        r = {}
        for k, v in self.items():
            if get_component_type(k) is _type:
                r[k] = v
        return r

    def __contains__(self, component):
        return component in self.instances

    def __setitem__(self, component, instance):
        msg = "Already exists in broker with key: %s"
        if component in self.instances:
            raise KeyError(msg % get_name(component))

        self.instances[component] = instance

    def __delitem__(self, component):
        if component in self.instances:
            del self.instances[component]
            return

    def __getitem__(self, component):
        if component in self.instances:
            return self.instances[component]

        raise KeyError("Unknown component: %s" % get_name(component))

    def get(self, component, default=None):
        try:
            return self[component]
        except KeyError:
            return default

    def print_component(self, component_type):
        print(json.dumps(
            dict((get_name(c), self[c])
                 for c in sorted(self.get_by_type(component_type), key=get_name))))


def get_missing_requirements(func, requires, d):
    if not requires:
        return None
    if any(i in d for i in IGNORE.get(func, [])):
        raise SkipComponent()
    req_all, req_any = split_requirements(requires)
    d = set(d.keys())
    req_all = [r for r in req_all if r not in d]
    req_any = [r for r in req_any if set(r).isdisjoint(d)]
    if req_all or req_any:
        return req_all, req_any
    else:
        return None


def add_observer(o, component_type=ComponentType):
    TYPE_OBSERVERS[component_type].add(o)


def observer(component_type=ComponentType):
    def inner(func):
        add_observer(func, component_type)
        return func
    return inner


def run_order(components):
    """
    Returns components in an order that satisfies their dependency
    relationships.
    """
    return toposort_flatten(components, sort=False)


def _determine_components(components):
    if isinstance(components, dict):
        return components

    if hashable(components) and components in COMPONENTS_BY_TYPE:
        components = get_components_of_type(components)

    if isinstance(components, (list, set)):
        graph = {}
        for c in components:
            graph.update(get_dependency_graph(c))
        return graph

    if hashable(components) and components in DELEGATES:
        return get_dependency_graph(components)

    if hashable(components) and components in COMPONENTS:
        return COMPONENTS[components]


def run(components=COMPONENTS[GROUPS.single], broker=None):
    """
    Executes components in an order that satisfies their dependency
    relationships.

    Keyword Args:
        components: Can be one of a dependency graph, a single component, a
            component group, or a component type. If it's anything other than a
            dependency graph, the appropriate graph is built for you and before
            evaluation.
        broker (Broker): Optionally pass a broker to use for evaluation. One is
            created by default, but it's often useful to seed a broker with an
            initial dependency.
    Returns:
        Broker: The broker after evaluation.
    """
    components = _determine_components(components)
    broker = broker or Broker()

    for component in run_order(components):
        start = time.time()
        try:
            if component not in broker and component in DELEGATES and is_enabled(component):
                log.info("Trying %s" % get_name(component))
                result = DELEGATES[component].process(broker)
                broker[component] = result
        except MissingRequirements as mr:
            if log.isEnabledFor(logging.DEBUG):
                name = get_name(component)
                reqs = stringify_requirements(mr.requirements)
                log.debug("%s missing requirements %s" % (name, reqs))
            broker.add_exception(component, mr)
        except SkipComponent:
            pass
        except Exception as ex:
            tb = traceback.format_exc()
            log.warn(tb)
            broker.add_exception(component, ex, tb)
        finally:
            broker.exec_times[component] = time.time() - start
            broker.fire_observers(component)

    return broker


def run_incremental(components=COMPONENTS[GROUPS.single], broker=None):
    """
    Executes components in an order that satisfies their dependency
    relationships. Disjoint subgraphs are executed one at a time and a broker
    containing the results for each is yielded. If a broker is passed here, its
    instances are used to seed the broker used to hold state for each sub
    graph.

    Keyword Args:
        components: Can be one of a dependency graph, a single component, a
            component group, or a component type. If it's anything other than a
            dependency graph, the appropriate graph is built for you and before
            evaluation.
        broker (Broker): Optionally pass a broker to use for evaluation. One is
            created by default, but it's often useful to seed a broker with an
            initial dependency.
    Yields:
        Broker: the broker used to evaluate each subgraph.
    """
    components = _determine_components(components)
    seed_broker = broker or Broker()
    for graph in get_subgraphs(components):
        broker = Broker(seed_broker)
        yield run(graph, broker=broker)
