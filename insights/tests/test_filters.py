import pytest
import sys

from collections import defaultdict

from insights import datasource
from insights.combiners.hostname import Hostname
from insights.core import filters
from insights.core.spec_factory import DatasourceProvider, RegistryPoint, SpecSet
from insights.parsers.ps import PsAux, PsAuxcww
from insights.specs import Specs
from insights.specs.default import DefaultSpecs


class MySpecs(SpecSet):
    no_filters = RegistryPoint(filterable=False)
    has_filters = RegistryPoint(filterable=True)


class LocalSpecs(MySpecs):
    # The has_filters depends on no_filters
    @datasource(MySpecs.no_filters)
    def has_filters(broker):
        return DatasourceProvider("", "the_data")


def setup_function(func):
    if func is test_get_filter:
        filters.add_filter(Specs.ps_aux, "COMMAND")

    if func is test_get_filter_registry_point:
        filters.add_filter(Specs.ps_aux, "COMMAND")
        filters.add_filter(DefaultSpecs.ps_aux, "MEM")

    if func is test_filter_dumps_loads:
        filters.add_filter(Specs.ps_aux, ["PID", "COMMAND", "TEST"])


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


@pytest.mark.skipif(sys.version_info < (2, 7), reason='Playbook verifier code uses oyaml library which is incompatable with this test')
def test_filter_dumps_loads():
    r = filters.dumps()
    assert r is not None

    filters.FILTERS = defaultdict(set)
    filters.loads(r)

    assert Specs.ps_aux in filters.FILTERS
    assert filters.FILTERS[Specs.ps_aux] == set(["PID", "COMMAND", "TEST"])

    r2 = filters.dumps()
    assert r2 == r  # 'filters' are in the same order in every dumps()


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


def test_add_filter_exception_not_filterable():
    with pytest.raises(Exception):
        filters.add_filter(Specs.ps_auxcww, "bash")


def test_add_filter_exception_parser_non_filterable():
    with pytest.raises(Exception):
        filters.add_filter(PsAuxcww, 'bash')


def test_add_filter_exception_combiner_non_filterable():
    with pytest.raises(Exception):
        filters.add_filter(Hostname, "bash")


def test_add_filter_exception_raw():
    with pytest.raises(Exception):
        filters.add_filter(Specs.metadata_json, "[]")


def test_add_filter_exception_empty():
    with pytest.raises(Exception):
        filters.add_filter(Specs.ps_aux, "")


def test_get_filters():
    _filter = 'A filter'
    filters.add_filter(MySpecs.has_filters, _filter)

    ret_has = filters.get_filters(MySpecs.has_filters)
    assert _filter in ret_has
    ret_no = filters.get_filters(MySpecs.no_filters)
    assert len(ret_no) == 0
