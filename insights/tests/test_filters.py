from collections import defaultdict
from insights.core import filters


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
