from collections import defaultdict
from insights.core import filters

from insights.parsers.ps import PsAux, PsAuxcww
from insights.specs import Specs
from insights.specs.default import DefaultSpecs

import pytest
import sys


def setup_function(func):
    if Specs.ps_aux in filters._CACHE:
        del filters._CACHE[Specs.ps_aux]
    if DefaultSpecs.ps_aux in filters._CACHE:
        del filters._CACHE[DefaultSpecs.ps_aux]
    if Specs.ps_aux in filters.FILTERS:
        del filters.FILTERS[Specs.ps_aux]
    if Specs.ps_aux in filters.DENY_FILTERS:
        del filters.DENY_FILTERS[Specs.ps_aux]
    if DefaultSpecs.ps_aux in filters.FILTERS:
        del filters.FILTERS[DefaultSpecs.ps_aux]
    if DefaultSpecs.ps_aux in filters.DENY_FILTERS:
        del filters.DENY_FILTERS[DefaultSpecs.ps_aux]

    if func is test_get_filter:
        filters.add_filter(Specs.ps_aux, "COMMAND")
        filters.add_deny_filter(Specs.ps_aux, "root")

    if func is test_get_filter_registry_point:
        filters.add_filter(Specs.ps_aux, "COMMAND")
        filters.add_filter(DefaultSpecs.ps_aux, "MEM")
        filters.add_deny_filter(DefaultSpecs.ps_aux, "root")

    if func is test_filter_dumps_loads_with_allow:
        filters.add_filter(Specs.ps_aux, "COMMAND")

    if func is test_filter_dumps_loads_with_both:
        filters.add_filter(Specs.ps_aux, "COMMAND")
        filters.add_deny_filter(Specs.ps_aux, "root")

    if func is test_filter_dumps_loads_with_deny:
        filters.add_deny_filter(Specs.ps_aux, "root")


def teardown_function(func):
    if func is test_get_filter:
        del filters.FILTERS[Specs.ps_aux]
        del filters.DENY_FILTERS[Specs.ps_aux]

    if func is test_get_filter_registry_point:
        del filters.FILTERS[Specs.ps_aux]
        del filters.FILTERS[DefaultSpecs.ps_aux]
        del filters.DENY_FILTERS[DefaultSpecs.ps_aux]

    if func is test_filter_dumps_loads_with_allow:
        del filters.FILTERS[Specs.ps_aux]
        del filters.DENY_FILTERS[Specs.ps_aux]

    if func is test_filter_dumps_loads_with_both:
        del filters.FILTERS[Specs.ps_aux]
        del filters.DENY_FILTERS[Specs.ps_aux]

    if func is test_filter_dumps_loads_with_deny:
        del filters.FILTERS[Specs.ps_aux]
        del filters.DENY_FILTERS[Specs.ps_aux]

    if func is test_add_filter_to_parser:
        del filters.FILTERS[Specs.ps_aux]
        del filters.DENY_FILTERS[Specs.ps_aux]

    if func is test_add_filter_to_parser_patterns_list:
        del filters.FILTERS[Specs.ps_aux]
        del filters.DENY_FILTERS[Specs.ps_aux]


@pytest.mark.skipif(sys.version_info < (2, 7), reason='Playbook verifier code uses oyaml library which is incompatable with this test')
def test_filter_dumps_loads_with_allow():
    r = filters.dumps()
    assert r is not None

    filters.FILTERS = defaultdict(set)
    filters.DENY_FILTERS = defaultdict(set)
    filters.loads(r)

    assert Specs.ps_aux in filters.FILTERS
    assert filters.FILTERS[Specs.ps_aux] == set(["COMMAND"])

    assert Specs.ps_aux in filters.DENY_FILTERS
    assert filters.DENY_FILTERS[Specs.ps_aux] == set()


def test_filter_dumps_loads_with_both():
    r = filters.dumps()
    assert r is not None

    filters.FILTERS = defaultdict(set)
    filters.DENY_FILTERS = defaultdict(set)
    filters.loads(r)

    assert Specs.ps_aux in filters.FILTERS
    assert filters.FILTERS[Specs.ps_aux] == set()

    assert Specs.ps_aux in filters.DENY_FILTERS
    assert filters.DENY_FILTERS[Specs.ps_aux] == set(["root"])


def test_filter_dumps_loads_with_deny():
    r = filters.dumps()
    assert r is not None

    filters.FILTERS = defaultdict(set)
    filters.DENY_FILTERS = defaultdict(set)
    filters.loads(r)

    assert Specs.ps_aux in filters.FILTERS
    assert filters.FILTERS[Specs.ps_aux] == set()

    assert Specs.ps_aux in filters.DENY_FILTERS
    assert filters.DENY_FILTERS[Specs.ps_aux] == set(["root"])


def test_get_filter():
    allow_filters, deny_filters = filters.get_filters(Specs.ps_aux)
    assert "COMMAND" in allow_filters
    assert "root" in deny_filters

    allow_filters, deny_filters = filters.get_filters(DefaultSpecs.ps_aux)
    assert "COMMAND" in allow_filters
    assert "root" in deny_filters


def test_get_filter_registry_point():
    s = set(["COMMAND", "MEM"])
    allow_filters, deny_filters = filters.get_filters(DefaultSpecs.ps_aux)
    assert allow_filters & s == s
    assert "root" in deny_filters

    allow_filters, deny_filters = filters.get_filters(Specs.ps_aux)
    assert "COMMAND" in allow_filters
    assert "MEM" not in allow_filters
    assert "root" not in deny_filters


def test_add_filter_to_parser():
    filter_string = "bash"
    filters.add_filter(PsAux, filter_string)
    deny_filter_string = "root"
    filters.add_deny_filter(PsAux, deny_filter_string)

    spec_allow_filters, spec_deny_filters = filters.get_filters(Specs.ps_aux)
    assert filter_string in spec_allow_filters
    assert deny_filter_string in spec_deny_filters

    parser_allow_filters, parser_deny_filters = filters.get_filters(PsAux)
    assert not parser_allow_filters
    assert not parser_deny_filters


def test_add_filter_to_parser_patterns_list():
    filters_list = ["bash", "systemd", "Network"]
    filters.add_filter(PsAux, filters_list)
    deny_filters_list = ["root", "nginx", ]
    filters.add_deny_filter(PsAux, deny_filters_list)

    spec_allow_filters, spec_deny_filters = filters.get_filters(Specs.ps_aux)
    assert all(f in spec_allow_filters for f in filters_list)
    assert all(f in spec_deny_filters for f in deny_filters_list)

    parser_allow_filters, parser_deny_filters = filters.get_filters(PsAux)
    assert not parser_allow_filters
    assert not parser_deny_filters


def test_add_filter_to_parser_non_filterable():
    filter_string = "bash"
    filters.add_filter(PsAuxcww, filter_string)
    deny_filter_string = "root"
    filters.add_deny_filter(PsAuxcww, deny_filter_string)

    spec_allow_filters, spec_deny_filters = filters.get_filters(Specs.ps_auxcww)
    assert not spec_allow_filters
    assert not spec_deny_filters

    parser_allow_filters, parser_deny_filters = filters.get_filters(PsAuxcww)
    assert not parser_allow_filters
    assert not parser_deny_filters


def test_add_filter_exception_not_filterable():
    with pytest.raises(Exception):
        filters.add_filter(Specs.ps_auxcww, "bash")

    with pytest.raises(Exception):
        filters.add_deny_filter(Specs.ps_auxcww, "bash")


def test_add_filter_exception_raw():
    with pytest.raises(Exception):
        filters.add_filter(Specs.metadata_json, "[]")

    with pytest.raises(Exception):
        filters.add_deny_filter(Specs.metadata_json, "[]")


def test_add_filter_exception_empty():
    with pytest.raises(Exception):
        filters.add_filter(Specs.ps_aux, "")


if __name__ == "__main__":
    filters.add_filter(Specs.ps_aux, "COMMAND")
    filters.add_deny_filter(Specs.ps_aux, "root")
    test_get_filter()
