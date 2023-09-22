import pytest

from insights.core import filters
from insights.core.exceptions import SkipComponent
from insights.specs import Specs
from insights.specs.datasources.dir_list import du_dir_list


def setup_function(func):
    if Specs.du_dirs in filters._CACHE:
        del filters._CACHE[Specs.du_dirs]
    if Specs.du_dirs in filters.FILTERS:
        del filters.FILTERS[Specs.du_dirs]

    if func is test_du_dirs_list:
        filters.add_filter(Specs.du_dirs, ["/var/lib/pulp", "/etc/httpd"])
    if func is test_du_dirs_list_no_filter:
        filters.add_filter(Specs.du_dirs, [])


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
