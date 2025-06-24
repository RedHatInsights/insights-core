import pytest

from collections import defaultdict

from insights import parser
from insights.combiners.hostname import Hostname
from insights.core import filters
from insights.core.spec_factory import RegistryPoint, SpecSet, simple_file
from insights.parsers.ps import PsAux, PsAuxcww
from insights.specs import Specs
from insights.specs.default import DefaultSpecs


class MySpecs(SpecSet):
    no_filters = RegistryPoint(filterable=False)
    has_filters = RegistryPoint(filterable=True)


class LocalSpecs(MySpecs):
    no_filters = simple_file('no_filters')
    has_filters = simple_file('has_filters')


@parser(MySpecs.has_filters)
class MySpecsHasFilters(object):
    pass


@parser(LocalSpecs.has_filters)
class LocalSpecsHasFilters(object):
    pass


@parser(MySpecs.no_filters)
class LocalSpecsNoFilters(object):
    pass


#
# TEST
#


def setup_function(func):
    if func is test_get_filter:
        filters.add_filter(Specs.ps_aux, "COMMAND", 99999)
        filters.add_filter(Specs.ps_aux, ["COMMAND", "PID"], 99)

    if func is test_get_filter_registry_point:
        filters.add_filter(Specs.ps_aux, "COMMAND")
        filters.add_filter(DefaultSpecs.ps_aux, "MEM")

    if func is test_filter_dumps_loads:
        filters.add_filter(Specs.ps_aux, ["PID", "COMMAND"])
        filters.add_filter(Specs.ps_aux, "TEST_10", 10)
        filters.add_filter(Specs.ps_aux, ["PID", "TEST_5"], 5)


def teardown_function(func):
    filters._CACHE = {}
    filters.FILTERS = defaultdict(dict)


def test_filter_dumps_loads():
    r = filters.dumps()
    assert r is not None

    filters.loads(r)

    assert Specs.ps_aux in filters.FILTERS
    assert filters.FILTERS[Specs.ps_aux] == {
        'COMMAND': filters.MAX_MATCH,
        'PID': filters.MAX_MATCH,  # max match
        'TEST_10': 10,
        'TEST_5': 5,
    }

    r2 = filters.dumps()
    assert r2 == r  # 'filters' are in the same order in every dumps()


def test_get_filter():
    f = filters.get_filters(Specs.ps_aux)
    assert "COMMAND" in f

    f = filters.get_filters(DefaultSpecs.ps_aux, True)
    assert "COMMAND" in f
    assert f["COMMAND"] == 99999  # max match
    assert f["PID"] == 99


def test_get_filter_registry_point():
    s = set(["COMMAND", "MEM"])
    f = filters.get_filters(DefaultSpecs.ps_aux)
    assert f & s == s

    f = filters.get_filters(Specs.ps_aux)
    assert "COMMAND" in f
    assert "MEM" not in f


# Local Parser
def test_add_filter_to_MySpecsHasFilters():
    """
    "filters" added to MySpecs.x will also add to LocalSpecs.x
    """
    filter_string = "bash"

    # Local Parser depends on MySpecs (Specs)
    filters.add_filter(MySpecsHasFilters, filter_string)

    myspecs_filters = filters.get_filters(MySpecs.has_filters)
    assert filter_string in myspecs_filters
    assert filter_string in filters.FILTERS[MySpecs.has_filters]

    localspecs_filters = filters.get_filters(LocalSpecs.has_filters)
    assert filter_string in localspecs_filters
    # but there is no key in FILTERS for the LocalSpecs.x
    assert filter_string not in filters.FILTERS[LocalSpecs.has_filters]


def test_add_filter_to_LocalSpecsHasFilters():
    """
    "filters" added to LocalSpecs.x will NOT add to Specs.x
    """
    filter_string = "bash"
    filters.add_filter(LocalSpecsHasFilters, filter_string)

    myspecs_filters = filters.get_filters(MySpecs.has_filters)
    assert filter_string not in myspecs_filters
    assert filter_string not in filters.FILTERS[MySpecs.has_filters]

    localspecs_filters = filters.get_filters(LocalSpecs.has_filters)
    assert filter_string in localspecs_filters
    assert filter_string in filters.FILTERS[LocalSpecs.has_filters]


# General Parser
def test_add_filter_to_parser_patterns_string():
    """
    "filters" added to Specs.x will add to DefaultSpecs.x
    """
    filter_string = "bash"
    filters.add_filter(PsAux, filter_string)

    spec_filters = filters.get_filters(Specs.ps_aux)
    assert filter_string in spec_filters
    assert filter_string in filters.FILTERS[Specs.ps_aux]

    default_spec_filters = filters.get_filters(DefaultSpecs.ps_aux)
    assert filter_string in default_spec_filters  # get_filters() works
    # but there is no key in FILTERS for the LocalSpecs.x
    assert filter_string not in filters.FILTERS[DefaultSpecs.ps_aux]  # empty in FILTERS

    parser_filters = filters.get_filters(PsAux)
    assert not parser_filters


def test_add_filter_to_parser_patterns_list():
    filters_list = ["bash", "systemd", "Network"]
    filters.add_filter(PsAux, filters_list)

    spec_filters = filters.get_filters(Specs.ps_aux)
    assert all(f in spec_filters for f in filters_list)

    parser_filters = filters.get_filters(PsAux)
    assert not parser_filters


def test_add_filter_to_parser_patterns_set():
    filters_set = set(["bash", "systemd", "Network"])
    filters.add_filter(PsAux, filters_set)

    spec_filters = filters.get_filters(Specs.ps_aux)
    assert all(f in spec_filters for f in filters_set)

    parser_filters = filters.get_filters(PsAux)
    assert not parser_filters


def test_add_filter_to_parser_patterns_tupple():
    filters_tup = ("bash", "systemd", "Network")
    with pytest.raises(TypeError):
        filters.add_filter(PsAux, filters_tup)


def test_add_filter_exception_spec_not_filterable():
    with pytest.raises(Exception):
        filters.add_filter(Specs.ps_auxcww, "bash")


def test_add_filter_exception_parser_non_filterable():
    with pytest.raises(Exception):
        filters.add_filter(PsAuxcww, 'bash')

    with pytest.raises(Exception):
        filters.add_filter(LocalSpecsNoFilters, 'bash')


def test_add_filter_exception_combiner_non_filterable():
    with pytest.raises(Exception):
        filters.add_filter(Hostname, "bash")


def test_add_filter_exception_raw():
    with pytest.raises(Exception):
        filters.add_filter(Specs.metadata_json, "[]")


def test_add_filter_exception_empty():
    with pytest.raises(Exception):
        filters.add_filter(Specs.ps_aux, "")


def test_add_filter_exception_None():
    with pytest.raises(Exception):
        filters.add_filter(Specs.ps_aux, None)


def test_add_filter_exception_with_invalid_max_match():
    with pytest.raises(Exception) as ex:
        filters.add_filter(Specs.ps_aux, 'abctest', 'str')
    assert "Invalid argument: str" in str(ex)

    with pytest.raises(Exception) as ex:
        filters.add_filter(Specs.ps_aux, 'abctest', 0)
    assert "Invalid argument: 0" in str(ex)

    with pytest.raises(Exception) as ex:
        filters.add_filter(Specs.ps_aux, 'abctest', -1)
    assert "Invalid argument: -1" in str(ex)

    with pytest.raises(Exception) as ex:
        filters.add_filter(Specs.ps_aux, 'abctest', None)
    assert "Invalid argument: None" in str(ex)


def test_get_filters():
    _filter = 'A filter'
    filters.add_filter(MySpecs.has_filters, _filter)

    ret_has = filters.get_filters(MySpecs.has_filters)
    assert _filter in ret_has
    ret_no = filters.get_filters(MySpecs.no_filters)
    assert len(ret_no) == 0

    assert filters.get_filters(None) == set()
    assert filters.get_filters(None, True) == dict()
