"""
This module implements an inversion of control framework. It allows
dependencies among functions and classes to be declared with decorators and the
resulting dependency graphs to be executed.

A decorator used to declare dependencies is called a :class:`ComponentType`, a
decorated function or class is called a component, and a collection of
interdependent components is called a graph.

In the example below, ``needs`` is a :class:`ComponentType`, ``one``, ``two``,
and ``add`` are components, and the relationship formed by their dependencies
is a graph.

    .. code-block:: python

       from insights import dr

       class needs(dr.ComponentType):
           pass

       @needs()
       def one():
           return 1

       @needs()
       def two():
           return 2

       @needs(one, two)
       def add(a, b):
           return a + b

       results = dr.run(add)

Once all components have been imported, the graphs they form can be run. To
execute a graph, ``dr`` sorts its components into an order that guarantees
dependencies are tried before dependents. Components that raise exceptions are
considered invalid, and their dependents will not be executed. If a component
is skipped because of a missing dependency, its dependents also will not be
executed.

During evaluation, results are accumulated into an object called a
:class:`Broker`, which is just a fancy dictionary. Brokers can be inspected
after a run for results, exceptions, tracebacks, and execution times. You also
can register callbacks with a broker that get invoked after the attempted
execution of every component, so you can inspect it during an evaluation
instead of at the end.
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
from insights.core.blacklist import BLACKLISTED_SPECS
from insights.core.exceptions import BlacklistedSpec, MissingRequirements, ParseException, SkipComponent
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
    skipped, and all components that require it will not execute.

    If component is a fully qualified name string of a callable object
    instead of the callable object itself, the component's module is loaded
    as a side effect of calling this function.

    Args:
        component (str or callable): fully qualified name of the component or
            the component object itself.
        enabled (bool): whether the component is enabled for evaluation.

    Returns:
        None
    """
    if isinstance(component, six.string_types):
        component = get_component(component)

    if component:
        ENABLED[component] = enabled


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


def _import_component(name):
    """
    Returns a class, function, or class method specified by the fully qualified
    name.
    """
    for f in (_get_from_module, _get_from_class):
        try:
            return f(name)
        except:
            pass


COMPONENT_IMPORT_CACHE = KeyPassingDefaultDict(_import_component)


def get_component(name):
    """ Returns the class or function specified, importing it if necessary. """
    return COMPONENT_IMPORT_CACHE[name]


def _find_component(name):
    for d in DELEGATES:
        if get_name(d) == name:
            return d


COMPONENTS_BY_NAME = KeyPassingDefaultDict(_find_component)


def get_component_by_name(name):
    """
    Look up a component by its fully qualified name. Return None if the
    component hasn't been loaded.
    """
    return COMPONENTS_BY_NAME[name]


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


def get_name(component):
    """
    Attempt to get the string name of component, including module and class if
    applicable.
    """
    if six.callable(component):
        name = getattr(component, "__qualname__", component.__name__)
        return '.'.join([component.__module__, name])
    return str(component)


def get_simple_name(component):
    if six.callable(component):
        return component.__name__
    return str(component)


def get_metadata(component):
    """
    Return any metadata dictionary associated with the component. Defaults to
    an empty dictionary.
    """
    return get_delegate(component).metadata if component in DELEGATES else {}


def get_tags(component):
    """
    Return the set of tags associated with the component. Defaults to
    ``set()``.
    """
    return get_delegate(component).tags if component in DELEGATES else set()


def get_links(component):
    """
    Return the dictionary of links associated with the component. Defaults to
    ``dict()``.
    """
    return get_delegate(component).links if component in DELEGATES else dict()


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
    """
    Generate a component's graph of dependencies, which can be passed to
    :func:`run` or :func:`run_incremental`.
    """
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


def get_dependency_specs(component):
    """
    Get the dependency specs of the specified `component`. Only `requires` and
    `at_least_one` specs will be returned. The `optional` specs is not
    considered in this function.

    Arguments:
        component (callable): The component to check. The component must
            already be loaded.

    Returns:
        list: The `requires` and `at_least_one` spec sets of the `component`.

    The return list is in the following format::

         [
             requires_1,
             requires_2,
             (at_least_one_11, at_least_one_12),
             (at_least_one_21, [req_alo22, (alo_23, alo_24)]),
         ]

        Note:
         - The 'requires_1' and 'requires_2' are `requires` specs.
           Each of them are required.
         - The 'at_least_one_11' and 'at_least_one_12' are `at_least_one`
           specs in the same at least one set.
           At least one of them is required
         - The 'alo_23' and 'alo_24' are `at_least_one` specs and
           together with the 'req_alo22' are `requires` for the
           sub-set. This sub-set specs and the 'at_least_one_21' are
           `at_least_one` specs in the same at least one set.
    """
    def get_requires(comp):
        req = list()
        for cmp in get_delegate(comp).requires:
            if get_name(cmp).startswith("insights.specs."):
                cmpn = get_simple_name(cmp)
                req.append(cmpn) if cmpn not in req else None
            else:
                union = get_requires(cmp) + get_at_least_one(cmp)
                req.extend([ss for ss in union if ss not in req])
        return req

    def get_at_least_one(comp):
        alo = list()
        for cmps in get_delegate(comp).at_least_one:
            salo = list()
            for cmp in cmps:
                ssreq = get_requires(cmp)
                ssalo = get_at_least_one(cmp)
                if ssreq and ssalo:
                    # they are mixed and in the same `requires` level
                    salo.append([ss for ss in ssreq + ssalo if ss not in salo])
                else:
                    # no mixed, just add them one by one
                    salo.extend([ss for ss in ssreq or ssalo if ss not in salo])
            alo.append(tuple(salo))
        return alo

    return get_requires(component) + get_at_least_one(component)


def is_registry_point(component):
    return type(component).__name__ == "RegistryPoint"


def get_registry_points(component):
    """
    Loop through the dependency graph to identify the corresponding spec registry
    points for the component. This is primarily used by datasources and returns a
    `set`. In most cases only one registry point will be included in the set, but
    in some cases more than one.

    Args:
        component (callable): The component object

    Returns:
        (set): A list of the registry points found.
    """
    reg_points = set()

    if is_registry_point(component):
        reg_points.add(component)
    else:
        for dep in get_dependents(component):
            if is_registry_point(dep):
                reg_points.add(dep)
            else:
                dep_reg_pts = get_registry_points(dep)
                if dep_reg_pts:
                    reg_points.update(dep_reg_pts)

    return reg_points


def get_subgraphs(graph=None):
    """
    Given a graph of possibly disconnected components, generate all graphs of
    connected components. graph is a dictionary of dependencies. Keys are
    components, and values are sets of components on which they depend.
    """
    graph = graph or DEPENDENCIES
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
    except BaseException:
        if not continue_on_error:
            raise


def _load_components(path, include=".*", exclude="\\.tests", continue_on_error=True):
    do_include = re.compile(include).search if include else lambda x: True
    do_exclude = re.compile(exclude).search if exclude else lambda x: False

    num_loaded = 0
    if path.endswith(".py"):
        path, _ = os.path.splitext(path)

    path = path.rstrip("/").replace("/", ".")
    if do_exclude(path):
        return 0

    package = _import(path, continue_on_error)
    if not package:
        return 0

    num_loaded += 1

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


def _register_component(delegate):
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

    For Example:

    .. code-block:: python

       class my_component_type(ComponentType):
           pass

       @my_component_type(SshDConfig, InstalledRpms, [ChkConfig, UnitFiles], optional=[IPTables, IpAddr])
       def my_func(sshd_config, installed_rpms, chk_config, unit_files, ip_tables, ip_addr):
           return installed_rpms.newest("bash")

    Notice that the arguments to ``my_func`` correspond to the dependencies in
    the ``@my_component_type`` and are in the same order.

    When used, a ``my_component_type`` instance is created whose
    ``__init__`` gets passed dependencies and whose ``__call__`` gets
    passed the component to run if dependencies are met.

    Parameters to the decorator have these forms:

    ============  ===============================  ==========================
    Criteria      Example Decorator Arguments      Description
    ============  ===============================  ==========================
    Required      ``SshDConfig, InstalledRpms``    A regular argument
    At Least One  ``[ChkConfig, UnitFiles]``       An argument as a list
    Optional      ``optional=[IPTables, IpAddr]``  A list following optional=
    ============  ===============================  ==========================

    If a parameter is required, the value provided for it is guaranteed not to
    be ``None``. In the example above, ``sshd_config`` and ``installed_rpms``
    will not be ``None``.

    At least one of the arguments to parameters of an "at least one"
    list will not be ``None``. In the example, either or both of ``chk_config``
    and unit_files will not be ``None``.

    Any or all arguments for optional parameters may be ``None``.

    The following keyword arguments may be passed to the decorator:

    Attributes:
        requires (list): a list of components that all components decorated with
            this type will implicitly require. Additional components passed to
            the decorator will be appended to this list.
        optional (list): a list of components that all components decorated with
            this type will implicitly depend on optionally. Additional components
            passed as ``optional`` to the decorator will be appended to this list.
        metadata (dict): an arbitrary dictionary of information to associate
            with the component you're decorating. It can be retrieved with
            ``get_metadata``.
        tags (list): a list of strings that categorize the component. Useful for
            formatting output or sifting through results for components you care
            about.
        group: ``GROUPS.single`` or ``GROUPS.cluster``. Used to organize
            components into "groups" that run together with :func:`insights.core.dr.run`.
        cluster (bool): if ``True`` will put the component into the
            ``GROUPS.cluster`` group. Defaults to ``False``. Overrides ``group``
            if ``True``.

    """

    requires = []
    """
    a list of components that all components decorated with this type will
    implicitly require. Additional components passed to the decorator will be
    appended to this list.
    """
    optional = []
    """
    a list of components that all components decorated with this type will
    implicitly depend on optionally. Additional components passed as
    ``optional`` to the decorator will be appended to this list.
    """
    metadata = {}
    """
    an arbitrary dictionary of information to associate with the component
    you're decorating. It can be retrieved with ``get_metadata``.
    """
    tags = []
    """
    a list of strings that categorize the component. Useful for formatting
    output or sifting through results for components you care about.
    """
    group = GROUPS.single
    """
    group: ``GROUPS.single`` or ``GROUPS.cluster``. Used to organize components
    into "groups" that run together with :func:`insights.core.dr.run`.
    """

    def __init__(self, *deps, **kwargs):
        """
        This constructor is the parameterized part of a decorator.
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

        tags = []
        tags.extend(self.__class__.tags)
        tags.extend(kwargs.get("tags", []) or [])
        self.tags = set(tags)

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
        _register_component(self)
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
    """
    The Broker is a fancy dictionary that keeps up with component instances as
    a graph is evaluated. It's the state of the evaluation. Once a graph has
    executed, the broker will contain everything about the evaluation:
    component instances, timings, exceptions, and tracebacks.

    You can either inspect the broker at the end of an evaluation, or you can
    register callbacks with it, and they'll get invoked after each component
    is called.

    Attributes:
        instances (dict): the component instances with components as keys.
        missing_requirements (dict): components that didn't have their dependencies
            met. Values are a two-tuple. The first element is the list of
            required dependencies that were missing. The second element is the
            list of "at least one" dependencies that were missing. For more
            information on dependency types, see the :class:`ComponentType`
            docs.
        exceptions (defaultdict(list)): Components that raise any type of
            exception except :class:`SkipComponent` during evaluation. The key
            is the component, and the value is a list of exceptions. It's a
            list because some components produce multiple instances.
        tracebacks (dict): keys are exceptions and values are their text
            tracebacks.
        exec_times (dict): component -> float dictionary where values are the
            number of seconds the component took to execute. Calculated using
            :func:`time.time`. For components that produce multiple instances,
            the execution time here is the sum of their individual execution
            times.
        store_skips (bool): Weather to store skips in the broker or not.
    """
    def __init__(self, seed_broker=None):
        self.instances = dict(seed_broker.instances) if seed_broker else {}
        self.missing_requirements = {}
        self.exceptions = defaultdict(list)
        self.tracebacks = {}
        self.exec_times = {}
        self.store_skips = False

        self.observers = defaultdict(set)
        if seed_broker is not None:
            self.observers.update(seed_broker.observers)
        else:
            self.observers[ComponentType] = set()
            for k, v in TYPE_OBSERVERS.items():
                self.observers[k] |= set(v)

    def observer(self, component_type=ComponentType):
        """
        You can use ``@broker.observer()`` as a decorator to your callback
        instead of :func:`Broker.add_observer`.
        """
        def inner(func):
            self.add_observer(func, component_type)
            return func
        return inner

    def add_observer(self, o, component_type=ComponentType):
        """
        Add a callback that will get invoked after each component is called.

        Args:
            o (func): the callback function

        Keyword Args:
            component_type (ComponentType): the :class:`ComponentType` to observe.
                The callback will fire any time an instance of the class or its
                subclasses is invoked.
        The callback should look like this:

        .. code-block:: python

            def callback(comp, broker):
                value = broker.get(comp)
                # do something with value
                pass

        """

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
        """
        Return all of the instances of :class:`ComponentType` ``_type``.
        """
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
    """
    .. deprecated:: 1.x
    """
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
    """
    Add a callback that will get invoked after each component is called.

    Args:
        o (func): the callback function

    Keyword Args:
        component_type (ComponentType): the :class:`ComponentType` to observe.
            The callback will fire any time an instance of the class or its
            subclasses is invoked.

    The callback should look like this:

    .. code-block:: python

        def callback(comp, broker):
            value = broker.get(comp)
            # do something with value
            pass

    """

    TYPE_OBSERVERS[component_type].add(o)


def observer(component_type=ComponentType):
    """
    You can use ``@broker.observer()`` as a decorator to your callback
    instead of :func:`add_observer`.
    """
    def inner(func):
        add_observer(func, component_type)
        return func
    return inner


def run_order(graph):
    """
    Returns components in an order that satisfies their dependency
    relationships.
    """
    return toposort_flatten(graph, sort=False)


def determine_components(components):
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


_determine_components = determine_components


def run_components(ordered_components, components, broker):
    """
    Runs a list of preordered components using the provided broker.

    This function allows callers to order components themselves and cache the
    result so they don't incur the toposort overhead on every run.
    """
    for component in ordered_components:
        start = time.time()
        try:
            if (component not in broker and component in components and
               component in DELEGATES and
               is_enabled(component)):
                log.info("Trying %s" % get_name(component))
                result = DELEGATES[component].process(broker)
                broker[component] = result
        except BlacklistedSpec as bs:
            for x in get_registry_points(component):
                BLACKLISTED_SPECS.append(str(x).split('.')[-1])
            broker.add_exception(component, bs, traceback.format_exc())
        except MissingRequirements as mr:
            if log.isEnabledFor(logging.DEBUG):
                name = get_name(component)
                reqs = stringify_requirements(mr.requirements)
                log.debug("%s missing requirements %s" % (name, reqs))
            broker.add_exception(component, mr)
        except ParseException as pe:
            log.warning(pe)
            broker.add_exception(component, pe, traceback.format_exc())
        except SkipComponent as sc:
            if broker.store_skips:
                log.warning(sc)
                broker.add_exception(component, sc, traceback.format_exc())
            else:
                pass
        except Exception as ex:
            tb = traceback.format_exc()
            log.warning(tb)
            broker.add_exception(component, ex, tb)
        finally:
            broker.exec_times[component] = time.time() - start
            broker.fire_observers(component)

    return broker


def run(components=None, broker=None):
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
    components = components or COMPONENTS[GROUPS.single]
    components = determine_components(components)
    broker = broker or Broker()
    return run_components(run_order(components), components, broker)


def generate_incremental(components=None, broker=None):
    components = components or COMPONENTS[GROUPS.single]
    components = determine_components(components)
    for graph in get_subgraphs(components):
        yield graph, broker or Broker()


def run_incremental(components=None, broker=None):
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
    for graph, _broker in generate_incremental(components, broker):
        yield run(graph, broker=_broker)


def run_all(components=None, broker=None, pool=None):
    if pool:
        futures = []
        for graph, _broker in generate_incremental(components, broker):
            futures.append(pool.submit(run, graph, _broker))
        return [f.result() for f in futures]
    else:
        return list(run_incremental(components=components, broker=broker))
