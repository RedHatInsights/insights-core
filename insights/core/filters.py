import re
import six
from collections import defaultdict

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
    results = []
    for l in lines:
        for f in FILTERS[target]:
            if re.search(f, l):
                results.append(l)
    return results
