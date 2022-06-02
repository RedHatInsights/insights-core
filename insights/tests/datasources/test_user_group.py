import pytest

from insights.specs import Specs
from insights.core import filters
from insights.specs.datasources.user_group import group_filters
from insights.core.dr import SkipComponent


def setup_function(func):
    if Specs.group_info in filters._CACHE:
        del filters._CACHE[Specs.group_info]
    if Specs.group_info in filters.FILTERS:
        del filters.FILTERS[Specs.group_info]

    if func is test_group_filters:
        filters.add_filter(Specs.group_info, ["wheel", "mem"])
    if func is test_group_filters_empty:
        filters.add_filter(Specs.group_info, [])


def test_group_filters():
    broker = {}
    result = group_filters(broker)
    assert 'mem wheel' == result


def test_group_filters_empty():
    broker = {}
    with pytest.raises(SkipComponent):
        group_filters(broker)
