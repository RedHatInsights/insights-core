import os
import pkgutil
import six
import yaml as ser
from collections import defaultdict

import insights
from insights.core import dr, plugins


# TODO: consider case insensitive and regex
FILTERS = defaultdict(set)


def add_filter(name, patterns):
    if isinstance(patterns, six.string_types):
        FILTERS[name].add(patterns)
    elif isinstance(patterns, list):
        FILTERS[name] |= set(patterns)
    elif isinstance(patterns, set):
        FILTERS[name] |= patterns
    else:
        raise TypeError("patterns must be string, list, or set.")


def get_filters(component, filters=None):
    filters = filters or set()
    if not plugins.is_datasource(component):
        return filters

    if component in FILTERS:
        filters |= FILTERS[component]

    for d in dr.get_dependents(component):
        filters |= get_filters(d, filters)
    return filters


def apply_filters(target, lines):
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
        FILTERS[dr.get_component(k) or k] = set(v)


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
        d[dr.get_name(k)] = list(v)
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
        with open(path, "wu") as f:
            f.write(dumps())
