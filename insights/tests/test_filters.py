from collections import defaultdict
from insights.core import filters

from insights.specs import Specs
from insights.specs.default import DefaultSpecs


def setup_function(func):
    if func is test_get_filter:
        filters.add_filter(Specs.ps_aux, "COMMAND")

    if func is test_get_filter_registry_point:
        filters.add_filter(Specs.ps_aux, "COMMAND")
        filters.add_filter(DefaultSpecs.ps_aux, "MEM")

    if func is test_filter_dumps_loads:
        filters.add_filter(Specs.ps_aux, "COMMAND")


def teardown_function(func):
    if func is test_get_filter:
        del filters.FILTERS[Specs.ps_aux]

    if func is test_get_filter_registry_point:
        del filters.FILTERS[Specs.ps_aux]
        del filters.FILTERS[DefaultSpecs.ps_aux]

    if func is test_filter_dumps_loads:
        del filters.FILTERS[Specs.ps_aux]


def test_filter_dumps_loads():
    r = filters.dumps()
    assert r is not None

    filters.FILTERS = defaultdict(set)
    filters.loads(r)

    assert Specs.ps_aux in filters.FILTERS
    assert filters.FILTERS[Specs.ps_aux] == set(["COMMAND"])


def test_get_filter():
    f = filters.get_filters(Specs.ps_aux)
    assert "COMMAND" in f

    f = filters.get_filters(DefaultSpecs.ps_aux)
    assert "COMMAND" in f


def test_get_filter_registry_point():
    s = set(["COMMAND", "MEM"])
    f = filters.get_filters(DefaultSpecs.ps_aux)
    assert f & s == s

    f = filters.get_filters(Specs.ps_aux)
    assert "COMMAND" in f
    assert "MEM" not in f
