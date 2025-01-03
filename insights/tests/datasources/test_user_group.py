import pytest

from collections import defaultdict

from insights.core import filters
from insights.core.exceptions import SkipComponent
from insights.specs import Specs
from insights.specs.datasources.user_group import group_filters


def setup_function(func):
    if func is test_group_filters:
        filters.add_filter(Specs.group_info, ["wheel", "mem"])
    if func is test_group_filters_empty:
        filters.add_filter(Specs.group_info, [])


def teardown_function(func):
    filters._CACHE = {}
    filters.FILTERS = defaultdict(dict)


def test_group_filters():
    broker = {}
    result = group_filters(broker)
    assert 'mem wheel' == result


def test_group_filters_empty():
    broker = {}
    with pytest.raises(SkipComponent):
        group_filters(broker)
