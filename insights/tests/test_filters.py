from collections import defaultdict
from insights.core import filters

from insights.specs import Specs
from insights.specs.default import DefaultSpecs


def test_filter_dumps_loads():
    key = "test_filter_dump"
    value = key

    filters.add_filter(key, value)
    r = filters.dumps()
    assert r is not None

    filters.FILTERS = defaultdict(set)
    filters.loads(r)

    assert key in filters.FILTERS
    assert filters.FILTERS[key] == set([value])


def test_get_filter():
    filters.add_filter(Specs.fstab, "COMMAND")
    f = filters.get_filters(Specs.fstab)
    assert "COMMAND" in f

    f = filters.get_filters(DefaultSpecs.fstab)
    assert "COMMAND" in f

    lines = ["COMMAND", "DISCARD"]

    lines = filters.apply_filters(DefaultSpecs.fstab, lines)
    assert "COMMAND" in lines
    assert "DISCARD" not in lines
