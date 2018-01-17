import os
import pkgutil
import re
import six
import yaml as ser
from collections import defaultdict

import insights
from insights.core import dr


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


def get_filters(component):
    filters = set()
    if component in FILTERS:
        filters |= FILTERS[component]

    alias = dr.get_alias(component)
    if alias and alias in FILTERS:
        filters |= FILTERS[alias]
    return filters


def apply_filters(target, lines):
    if target not in FILTERS:
        return lines

    results = []
    for l in lines:
        for f in FILTERS[target]:
            if re.search(f, l):
                results.append(l)
    return results


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
