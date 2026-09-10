import pytest

from collections import defaultdict
from unittest.mock import patch

from insights.collect import get_to_persist
from insights.core import filters
from insights.core.exceptions import SkipComponent
from insights.specs import Specs
from insights.specs.datasources.user_group import all_users, group_filters


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


@patch("insights.specs.datasources.user_group.pwd.getpwall")
def test_all_users(getpwall):
    entries = ["root_entry", "alice_entry"]
    getpwall.return_value = entries
    assert all_users({}) == entries


@patch("insights.specs.datasources.user_group.pwd.getpwall")
def test_all_users_skip_when_empty(getpwall):
    getpwall.return_value = []
    with pytest.raises(SkipComponent):
        all_users({})


def test_all_users_is_never_persisted():
    # The default manifest persists only ``insights.specs.Specs`` registry
    # points. ``all_users`` is an internal helper datasource and must never be
    # collected into the archive (it can hold sensitive user data).
    to_persist = get_to_persist([{"name": "insights.specs.Specs", "enabled": True}])
    assert all_users not in to_persist
