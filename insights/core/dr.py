""" This module implements dependency resolution within Red Hat Insights."""

import importlib
import inspect
import logging
import pkgutil
import pprint
import re
import six
import traceback

from collections import defaultdict
from functools import reduce as _reduce
from insights.contrib.toposort import toposort_flatten
from insights.util import enum

log = logging.getLogger(__name__)

GROUPS = enum("cluster", "single")

MODULE_NAMES = dict()
SIMPLE_MODULE_NAMES = dict()

ALIASES = dict()
TYPE_OF_COMPONENT = dict()
COMPONENTS_BY_TYPE = defaultdict(set)
DEPENDENCIES = defaultdict(set)
COMPONENTS = defaultdict(lambda: defaultdict(set))
DEPENDENTS = defaultdict(set)
DELEGATES = dict()


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
        requires=None, optional=None, group=GROUPS.single, alias=None):

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
    COMPONENTS_BY_TYPE[component_type].add(component)
    DELEGATES[component] = delegate
    MODULE_NAMES[component] = get_module_name(component)
    SIMPLE_MODULE_NAMES[component] = get_simple_module_name(component)

    if alias:
        msg = "Alias %s already registered!"
        if alias in ALIASES:
            raise Exception(msg % alias)
        if component in ALIASES:
            raise Exception(msg % get_name(component))

        ALIASES[alias] = component
        ALIASES[component] = alias


class Broker(object):

    def __init__(self):
        self.instances = dict()
        self.missing_dependencies = dict()
        self.exceptions = defaultdict(list)
        self.tracebacks = dict()

    def add_exception(self, component, ex, tb=None):
        if isinstance(ex, MissingRequirements):
            self.missing_dependencies[component] = ex.requirements
        else:
            self.exceptions[component].append(ex)
            self.tracebacks[ex] = tb

    def keys(self):
        return self.instances.keys()

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
                       executor=default_executor):
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

        Returns:
            A decorator function used to define components of the new type.
    """

    def decorator(requires=None, optional=None, group=group, executor=executor, alias=None):
        requires = requires or []
        optional = optional or []

        requires.extend(auto_requires)
        optional.extend(auto_optional)

        def _f(func):
            @six.wraps(func)
            def __f(broker):
                return executor(func, broker, requires, optional)

            register_component(func, __f, decorator,
                               requires=requires,
                               optional=optional,
                               group=group,
                               alias=alias)
            return func
        return _f

    if name:
        decorator.__name__ = name
    return decorator


def run_order(components):
    """ Returns components in an order that satisfies their dependency
        relationships.
    """
    return toposort_flatten(components)


def run(components, broker=None):
    """ Executes components in an order that satisfies their dependency
        relationships.
    """
    broker = broker or Broker()

    for component in run_order(components):
        try:
            if component not in broker and component in DELEGATES:
                log.debug("Calling %s" % get_name(component))
                result = DELEGATES[component](broker)
                log.debug("Result: %s" % pprint.pformat(result))
                broker[component] = result
        except MissingRequirements as mr:
            broker.add_exception(component, mr)
        except SkipComponent:
            log.debug(traceback.format_exc())
        except Exception as ex:
            log.exception(ex)
            broker.add_exception(component, ex, traceback.format_exc())

    return broker
