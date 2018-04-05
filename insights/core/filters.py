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
    """Add a pattern(s) to Specs.

    Example:

        >>> from insights.core.filters import FILTERS, add_filter
        >>> from insights.specs import Specs
        >>> FILTERS.values()
        []
        >>> add_filter(Specs.messages, 'enp0s25')
        >>> FILTERS.values()
        [set(['enp0s25'])]
        >>> FILTERS.viewitems()
        dict_items([(<function messages at 0x7f922c96f758>, set(['enp0s25']))])
        >>>
        >>> add_filter(Specs, 'wlp3s0')
        >>> FILTERS.values()
        [set(['wlp3s0']), set(['enp0s25'])]
        >>> FILTERS.viewitems()
        dict_items([(<class 'insights.specs.Specs'>, set(['wlp3s0'])), (<function messages at 0x7f922c96f758>, set(['enp0s25']))])


    Args:

        name (SpecSetMeta): A ``SpecSetMeta`` or a function. Ex: ``Specs.messages``.

        pattern (str): A matching string.
    """
    if isinstance(patterns, six.string_types):
        FILTERS[name].add(patterns)
    elif isinstance(patterns, list):
        FILTERS[name] |= set(patterns)
    elif isinstance(patterns, set):
        FILTERS[name] |= patterns
    else:
        raise TypeError("patterns must be string, list, or set.")


def get_filters(component, filters=None):
    """Get pattern from Spec

    Example:

        >>> from insights.core.filters import FILTERS, add_filter, get_filters
        >>> from insights.specs import Specs
        >>> from insights.specs.default import DefaultSpecs
        >>> FILTERS.values()
        []
        >>> FILTERS.viewitems()
        dict_items([])
        >>> add_filter(Specs.messages, ['enp0s25', 'wlp3s0'])
        >>> FILTERS.viewitems()
        dict_items([(<function messages at 0x7f5e287515f0>, set(['wlp3s0', 'enp0s25']))])
        >>> get_filters(Specs.messages)
        set(['wlp3s0', 'enp0s25'])
        >>> get_filters(DefaultSpecs.messages)
        set(['wlp3s0', 'enp0s25'])
        >>> get_filters(DefaultSpecs.messages, set(['eth0']))
        set(['wlp3s0', 'enp0s25', 'eth0'])


    Args:

        component (SpecSetMeta): A ``SpecSetMeta`` or a function. Ex: ``Specs.messages``.

        filters (set): A ``set()`` of new filters.
    """
    filters = filters or set()
    if not plugins.is_datasource(component):
        return filters

    if component in FILTERS:
        filters |= FILTERS[component]

    for d in dr.get_dependents(component):
        filters |= get_filters(d, filters)
    return filters


def apply_filters(target, lines):
    """Apply filters on lines.

    Example:

        >>> from insights.core.filters import add_filter, get_filters, apply_filters
        >>> from insights.specs import Specs
        >>> from insights.specs.default import DefaultSpecs
        >>> LOGS = '''
        ... [582980.770142] PM: resume devices took 0.606 seconds
        ... [582980.770157] acpi LNXPOWER:02: Turning OFF
        ... [582980.770352] OOM killer enabled.
        ... [582980.770353] Restarting tasks ... done.
        ... [582980.810019] PM: suspend exit
        ... [582980.819860] IPv6: ADDRCONF(NETDEV_UP): enp0s25: link is not ready
        ... [582981.027104] IPv6: ADDRCONF(NETDEV_UP): enp0s25: link is not ready
        ... [582981.028062] IPv6: ADDRCONF(NETDEV_UP): wlp3s0: link is not ready
        ... '''.split()
        >>> add_filter(Specs.messages, set(['IPv6', 'OOM']))
        >>> get_filters(DefaultSpecs.messages)
        set(['OOM', 'IPv6'])
        >>> get_filters(DefaultSpecs.messages, set(['acpi']))
        set(['OOM', 'acpi', 'IPv6'])
        >>> matched_lines = apply_filters(DefaultSpecs.messages, LOGS)
        >>> 'OOM' in matched_lines
        True
        >>> 'suspend' not in matched_lines
        True
        >>> 'acpi' not in matched_lines
        True


    Args:

        target (func): A function. Ex: ``DefaultSpecs.messages``.

        lines (list): Content with each line as an item in a list.
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
