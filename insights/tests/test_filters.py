from collections import defaultdict
from insights.core import filters

from insights.parsers.ps import PsAux, PsAuxcww
from insights.specs import Specs
from insights.specs.default import DefaultSpecs

import pytest


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

    if func is test_add_filter_to_parser:
        del filters.FILTERS[Specs.ps_aux]

    if func is test_add_filter_to_parser_patterns_list:
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


def test_add_filter_to_parser():
    filter_string = "bash"
    filters.add_filter(PsAux, filter_string)

    spec_filters = filters.get_filters(Specs.ps_aux)
    assert filter_string in spec_filters

    parser_filters = filters.get_filters(PsAux)
    assert not parser_filters


def test_add_filter_to_parser_patterns_list():
    filters_list = ["bash", "systemd", "Network"]
    filters.add_filter(PsAux, filters_list)

    spec_filters = filters.get_filters(Specs.ps_aux)
    assert all(f in spec_filters for f in filters_list)

    parser_filters = filters.get_filters(PsAux)
    assert not parser_filters


def test_add_filter_to_parser_non_filterable():
    filter_string = "bash"
    filters.add_filter(PsAuxcww, filter_string)

    spec_filters = filters.get_filters(Specs.ps_auxcww)
    assert not spec_filters

    parser_filters = filters.get_filters(PsAuxcww)
    assert not parser_filters


def test_add_filter_exception_not_filterable():
    with pytest.raises(Exception):
        filters.add_filter(Specs.ps_auxcww, "bash")


def test_add_filter_exception_raw():
    with pytest.raises(Exception):
        filters.add_filter(Specs.metadata_json, "[]")
