"""
The filters module allows developers to apply filters to datasources,
by adding them directly or through dependent components like parsers
and combiners. A filter is a simple string, and it matches if it is contained
anywhere within a line.

If a datasource has filters defined, it will return only lines matching at
least one of them. If a datasource has no filters, it will return all lines.

Filters can be added to components like parsers and combiners, to apply consistent
filtering to multiple underlying datasources that are configured as filterable.

Filters aren't applicable to "raw" datasources, which are created with
``kind=RawFileProvider`` and have ``RegistryPoint`` instances with ``raw=True``.

The addition of a single filter can cause a datasource to change from returning
all lines to returning just those that match. Therefore, any filtered
datasource should have at least one filter in the commit introducing it so
downstream components don't inadvertently change its behavior.

The benefit of this fragility is the ability to drastically reduce in-memory
footprint and archive sizes. An additional benefit is the ability to evaluate
only lines known to be free of sensitive information.

Filters added to a ``RegistryPoint`` will be applied to all datasources that
implement it. Filters added to a datasource implementation apply only to that
implementation.

For example, a filter added to ``Specs.ps_auxww`` will apply to
``DefaultSpecs.ps_auxww``, ``InsightsArchiveSpecs.ps_auxww``,
``SosSpecs.ps_auxww``, etc. But a filter added to `DefaultSpecs.ps_auxww` will
only apply to ``DefaultSpecs.ps_auxww``. See the modules in ``insights.specs``
for those classes.

Filtering can be disabled globally by setting the environment variable
``INSIGHTS_FILTERS_ENABLED=False``. This means that no datasources will be
filtered even if filters are defined for them.
"""
import os
import pkgutil
import six
import yaml as ser
from collections import defaultdict

import insights
from insights.core import dr, plugins
from insights.util import parse_bool

_CACHE = {}
FILTERS = defaultdict(set)
DENY_FILTERS = defaultdict(set)
ENABLED = parse_bool(os.environ.get("INSIGHTS_FILTERS_ENABLED"), default=True)


def add_filter(component, patterns):
    """
    Add a filter or list of filters to a component. When the component is
    a datasource, the filter will be directly added to that datasouce.
    In cases when the component is a parser or combiner, the filter will be
    added to underlying filterable datasources by traversing dependency graph.
    A filter is a simple string, and it matches if it is contained anywhere
    within a line.

    Args:
       component (component): The component to filter, can be datasource,
            parser or combiner.
       patterns (str, [str]): A string, list of strings, or set of strings to
            add to the datasource's filters.
    """
    def inner(component, patterns):
        if component in _CACHE:
            del _CACHE[component]

        types = six.string_types + (list, set)
        if not isinstance(patterns, types):
            raise TypeError("Filter patterns must be of type string, list, or set.")

        if isinstance(patterns, six.string_types):
            patterns = set([patterns])
        elif isinstance(patterns, list):
            patterns = set(patterns)

        for pat in patterns:
            if not pat:
                raise Exception("Filter patterns must not be empy.")

        FILTERS[component] |= patterns

    if not plugins.is_datasource(component):
        for dep in dr.run_order(dr.get_dependency_graph(component)):
            if plugins.is_datasource(dep):
                d = dr.get_delegate(dep)
                if d.filterable:
                    inner(dep, patterns)
    else:
        delegate = dr.get_delegate(component)

        if delegate.raw:
            raise Exception("Filters aren't applicable to raw datasources.")

        if not delegate.filterable:
            raise Exception("Filters aren't applicable to %s." % dr.get_name(component))

        inner(component, patterns)


_add_filter = add_filter


def add_deny_filter(component, patterns):
    """
    Add a filter or list of filters to a component. When the component is
    a datasource, the filter will be directly added to that datasouce.
    In cases when the component is a parser or combiner, the filter will be
    added to underlying filterable datasources by traversing dependency graph.
    A filter is a simple string, and it matches if it is contained anywhere
    within a line.

    Args:
       component (component): The component to filter, can be datasource,
            parser or combiner.
       patterns (str, [str]): A string, list of strings, or set of strings to
            add to the datasource's filters.
    """
    def inner(component, patterns):
        if component in _CACHE:
            del _CACHE[component]
        if isinstance(patterns, six.string_types):
            DENY_FILTERS[component].add(patterns)
        elif isinstance(patterns, list):
            DENY_FILTERS[component] |= set(patterns)
        elif isinstance(patterns, set):
            DENY_FILTERS[component] |= patterns
        else:
            raise TypeError("patterns must be string, list, or set.")

    if not plugins.is_datasource(component):
        for dep in dr.run_order(dr.get_dependency_graph(component)):
            if plugins.is_datasource(dep):
                d = dr.get_delegate(dep)
                if d.filterable:
                    inner(dep, patterns)
    else:
        delegate = dr.get_delegate(component)

        if delegate.raw:
            raise Exception("Filters aren't applicable to raw datasources.")

        if not delegate.filterable:
            raise Exception("Filters aren't applicable to %s." % dr.get_name(component))

        inner(component, patterns)


_add_deny_filter = add_deny_filter


def get_filters(component):
    """
    Get the set of filters for the given datasource.

    Filters added to a ``RegistryPoint`` will be applied to all datasources that
    implement it. Filters added to a datasource implementation apply only to
    that implementation.

    For example, a filter added to ``Specs.ps_auxww`` will apply to
    ``DefaultSpecs.ps_auxww``, ``InsightsArchiveSpecs.ps_auxww``,
    ``SosSpecs.ps_auxww``, etc. But a filter added to ``DefaultSpecs.ps_auxww``
    will only apply to ``DefaultSpecs.ps_auxww``. See the modules in
    ``insights.specs`` for those classes.

    Args:
        component (a datasource): The target datasource

    Returns:
        set: The set of filters defined for the datasource
    """
    def inner(c, filters=None):
        filters = filters or (set(), set())
        if not ENABLED:
            return filters

        if not plugins.is_datasource(c):
            return filters

        if c in FILTERS:
            allow_filters, deny_filters = filters
            allow_filters |= FILTERS[c]
            filters = (allow_filters, deny_filters)

        if c in DENY_FILTERS:
            allow_filters, deny_filters = filters
            deny_filters |= DENY_FILTERS[c]
            filters = (allow_filters, deny_filters)

        for d in dr.get_dependents(c):
            allow_filters, deny_filters = filters
            dep_accept_filters, dep_deny_filters = inner(d, filters)
            allow_filters |= dep_accept_filters
            deny_filters |= dep_deny_filters
            filters = (allow_filters, deny_filters)
        return filters

    if component not in _CACHE:
        _CACHE[component] = inner(component)
    return _CACHE[component]


def apply_filters(target, lines):
    """
    Applys filters to the lines of a datasource. This function is used only in
    integration tests. Filters are applied in an equivalent but more performant
    way at run time.
    """
    allow_filters, deny_filters = get_filters(target)
    if deny_filters:
        for l in lines:
            if not any(f in l for f in deny_filters):
                yield l
    # TODO: should we use allow filters if there are deny filters or are they mutually exclusive
    # TODO: If we allow both types we need to make sure deny controls, so deny first then allow
    # TODO: As written, deny is exclusive and takes priority
    elif allow_filters:
        for l in lines:
            if any(f in l for f in allow_filters):
                yield l
    else:
        for l in lines:
            yield l


_filename = ".".join(["filters", ser.__name__])
_dumps = ser.dump
_loads = ser.safe_load


def loads(string):
    """Loads the filters dictionary given a string."""
    d = _loads(string)
    for k, v in d.items():
        # TODO: For specs with deny filters, this will always create an empty allow filter list
        FILTERS[dr.get_component(k) or k] = set(v.get('allow', []))
        DENY_FILTERS[dr.get_component(k) or k] = set(v.get('deny', []))


def load(stream=None):
    """
    Loads filters from a stream, normally an open file. If one is
    not passed, filters are loaded from a default location within
    the project.
    """
    if stream:
        loads(stream.read())
    else:
        data = pkgutil.get_data(insights.__name__, _filename)
        return loads(data) if data else None


def dumps():
    """Returns a string representation of the FILTERS dictionary."""
    d = {}
    for k, v in FILTERS.items():
        d[dr.get_name(k)] = {'allow': list(v)}
    # TODO: Deny filters overwrite any allow filters, so file output is mutually exclusive
    for k, v in DENY_FILTERS.items():
        d[dr.get_name(k)] = {'deny': list(v)}
    return _dumps(d)


def dump(stream=None):
    """
    Dumps a string representation of `FILTERS` to a stream, normally an
    open file. If none is passed, `FILTERS` is dumped to a default location
    within the project.
    """
    if stream:
        stream.write(dumps())
    else:
        path = os.path.join(os.path.dirname(insights.__file__), _filename)
        with open(path, "w") as f:
            f.write(dumps())
