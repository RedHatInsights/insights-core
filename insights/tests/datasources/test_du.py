import pytest

from collections import defaultdict

from insights.core import filters
from insights.core.exceptions import SkipComponent
from insights.specs import Specs
from insights.specs.datasources.du import du_dir_list


def setup_function(func):
    if func is test_du_dirs_list:
        filters.add_filter(Specs.du_dirs, ["/var/lib/pulp", "/etc/httpd"])
    if func is test_du_dirs_list_no_filter:
        filters.add_filter(Specs.du_dirs, [])


def teardown_function(func):
    filters._CACHE = {}
    filters.FILTERS = defaultdict(dict)


def test_du_dirs_list():
    broker = {}
    result = du_dir_list(broker)
    assert len(result) == 2
    assert '/var/lib/pulp' in result
    assert '/etc/httpd' in result


def test_du_dirs_list_no_filter():
    broker = {}
    with pytest.raises(SkipComponent):
        du_dir_list(broker)
