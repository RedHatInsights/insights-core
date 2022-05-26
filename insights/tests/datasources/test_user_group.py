import pytest

from insights.specs import Specs
from insights.core import filters
from insights.specs.datasources.user_group import groups
from insights.core.dr import SkipComponent


def setup_function(func):
    if Specs.group_info in filters._CACHE:
        del filters._CACHE[Specs.group_info]
    if Specs.group_info in filters.FILTERS:
        del filters.FILTERS[Specs.group_info]

    if func is test_group_info_list:
        filters.add_filter(Specs.group_info, ["wheel", "mem"])
    if func is test_group_info_no_filter:
        filters.add_filter(Specs.group_info, [])


def test_group_info_list():
    broker = {}
    result = groups(broker)
    assert 'mem wheel' == result


def test_group_info_no_filter():
    broker = {}
    with pytest.raises(SkipComponent):
        groups(broker)
