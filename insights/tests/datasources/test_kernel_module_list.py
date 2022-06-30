import pytest

from insights.specs import Specs
from insights.core import filters
from insights.specs.datasources.kernel_module_list import kernel_module_filters
from insights.core.dr import SkipComponent


def setup_function(func):
    if Specs.modinfo_modules in filters._CACHE:
        del filters._CACHE[Specs.modinfo_modules]
    if Specs.modinfo_modules in filters.FILTERS:
        del filters.FILTERS[Specs.modinfo_modules]

    if func is test_module_filters:
        filters.add_filter(Specs.modinfo_modules, ["udp_diag", "binfmt_misc"])
    if func is test_module_filters_empty:
        filters.add_filter(Specs.modinfo_modules, [])


def test_module_filters():
    broker = {}
    result = kernel_module_filters(broker)
    assert 'binfmt_misc udp_diag' == result


def test_module_filters_empty():
    broker = {}
    with pytest.raises(SkipComponent):
        kernel_module_filters(broker)
