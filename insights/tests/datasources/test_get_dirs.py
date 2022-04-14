from insights.specs import Specs
from insights.core import filters
from insights.specs.datasources.get_dirs import du_dirs_list


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
    result = du_dirs_list(broker)
    assert len(result) == 2
    assert '/var/lib/pulp' in result
    assert '/etc/httpd' in result


def test_du_dirs_list_no_filter():
    broker = {}
    result = du_dirs_list(broker)
    assert not result
