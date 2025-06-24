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
FILTERS = defaultdict(dict)
ENABLED = parse_bool(os.environ.get("INSIGHTS_FILTERS_ENABLED"), default=True)
MAX_MATCH = 10000


def add_filter(component, patterns, max_match=MAX_MATCH):
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
       max_match (int): A int, the maximum matched lines to filter out.
            MAX_MATCH by default.
    """

    def get_dependency_datasources(comp):
        """Get (all) the first depended datasource"""
        dep_ds = set()
        if plugins.is_datasource(comp):
            dep_ds.add(comp)
            return dep_ds
        for dep in dr.get_dependencies(comp):
            dep_ds.update(get_dependency_datasources(dep))
        return dep_ds

    def none_max(a, b):
        return a if b is None else b if a is None else max(a, b)

    def max_matchs(da, db):
        return dict((k, none_max(da.get(k), db.get(k))) for k in set(da.keys()).union(db.keys()))

    def inner(comp, patterns):
        if comp in _CACHE:
            del _CACHE[comp]

        if not isinstance(patterns, (six.string_types, list, set)):
            raise TypeError("Filter patterns must be of type string, list, or set.")

        if isinstance(patterns, six.string_types):
            patterns = [patterns]

        for pat in patterns:
            if not pat:
                raise Exception("Filter patterns must not be empty.")

        patterns = dict((pt, max_match) for pt in patterns)
        # here patterns is a dict

        FILTERS[comp].update(max_matchs(FILTERS[comp], patterns))

    if max_match is None or type(max_match) is not int or max_match <= 0:
        raise Exception(
            "Invalid argument: {0}. It can only be a positive integer.".format(max_match)
        )

    if not plugins.is_datasource(component):
        deps = get_dependency_datasources(component)
        if deps:
            filterable_deps = [dep for dep in deps if dr.get_delegate(dep).filterable]
            # At least one dependency datasource be filterable
            if not filterable_deps:
                raise Exception("Filters aren't applicable to %s." % dr.get_name(component))

            for dep in filterable_deps:
                inner(dep, patterns)
    else:
        delegate = dr.get_delegate(component)

        if delegate.raw:
            raise Exception("Filters aren't applicable to raw datasources.")

        if not delegate.filterable:
            raise Exception("Filters aren't applicable to %s." % dr.get_name(component))

        inner(component, patterns)


_add_filter = add_filter


def get_filters(component, with_matches=False):
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
        with_matches (boolean): Needs the max matches being returned? False by
                                default.

    Returns:
        (set or dict): when `with_matches=False`, returns the set of filters
                       defined for the datasource only.
                       when `with_matches=True`, returns filters defined for
                       the datasource with the max match count specified by
                       `add_filter`.
    """

    def inner(c, filters=None):
        filters = filters or dict()

        if hasattr(c, 'filterable') and c.filterable is False:
            return filters

        if not ENABLED:
            return filters

        if not plugins.is_datasource(c):
            return filters

        if c in FILTERS:
            filters.update(FILTERS[c])

        for d in dr.get_dependents(c):
            filters.update(inner(d, filters))

        return filters

    if not component:
        # No filters for nothing
        return dict() if with_matches else set()

    if component not in _CACHE:
        _CACHE[component] = inner(component)

    return _CACHE[component] if with_matches else set(_CACHE[component].keys())


def apply_filters(target, lines):
    """
    Applys filters to the lines of a datasource. This function is used only in
    integration tests. Filters are applied in an equivalent but more performant
    way at run time.
    """
    filters = get_filters(target)
    if filters:
        for l in lines:
            if any(f in l for f in filters):
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
        FILTERS[dr.get_component(k) or k] = v


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
    """Returns a string representation of the sorted FILTERS dictionary."""
    d = {}
    for k, v in FILTERS.items():
        d[dr.get_name(k)] = dict(sorted(v.items()))
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
