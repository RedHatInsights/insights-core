import re
import six
from collections import defaultdict

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


def apply_filters(target, lines):
    results = []
    for l in lines:
        for f in FILTERS[target]:
            if re.search(f, l):
                results.append(l)
    return results


def _make_factory_func():

    from insights.config import static as s_factory
    from insights.config import db as d_factory

    s_config = s_factory.get_config()
    d_config = d_factory.get_config()

    s_config.compose(d_config)

    def inner():
        return s_config
    return inner


get_config = _make_factory_func()
