import pytest
import doctest
from insights.tests import context_wrap
from insights.parsers import SkipException
from insights.parsers import pmrep
from insights.parsers.pmrep import PMREPMetrics

PMREPMETRIC_DATA = """
Time,"network.interface.out.packets-lo","network.interface.out.packets-eth0","network.interface.collisions-lo","network.interface.collisions-eth0","swap.pagesout","mssql.memory_manager.stolen_server_memory","mssql.memory_manager.total_server_memory"
2021-04-26 05:42:24,,,,,
2021-04-26 05:42:25,1.000,2.000,3.000,4.000,5.000,349816,442000
""".strip()

PMREPMETRIC_DATA_2 = """
Time,"network.interface.out.packets-lo","network.interface.collisions-lo","swap.pagesout"
2021-04-26 05:42:24,,,
2021-04-26 05:42:25,1.000,2.000,3.000
""".strip()

PMREPMETRIC_WRONG_DATA = """
Time,"network.interface.out.packets-lo","network.interface.collisions-lo","swap.pagesout"
""".strip()


PMREPMETRIC_EMPTY_DATA = """
""".strip()


def test_pmrep_info():
    pmrep_table = PMREPMetrics(context_wrap(PMREPMETRIC_DATA))
    pmrep_table = sorted(pmrep_table, key=lambda x: x['name'])
    assert pmrep_table[0] == {'name': 'Time', 'value': '2021-04-26 05:42:25'}
    assert pmrep_table[1] == {'name': 'mssql.memory_manager.stolen_server_memory', 'value': '349816'}
    assert pmrep_table[2] == {'name': 'mssql.memory_manager.total_server_memory', 'value': '442000'}
    assert pmrep_table[3] == {'name': 'network.interface.collisions-eth0', 'value': '4.000'}
    assert pmrep_table[4] == {'name': 'network.interface.collisions-lo', 'value': '3.000'}
    assert pmrep_table[5] == {'name': 'network.interface.out.packets-eth0', 'value': '2.000'}
    assert pmrep_table[6] == {'name': 'network.interface.out.packets-lo', 'value': '1.000'}
    assert pmrep_table[7] == {'name': 'swap.pagesout', 'value': '5.000'}

    pmrep_table = PMREPMetrics(context_wrap(PMREPMETRIC_DATA_2))
    pmrep_table = sorted(pmrep_table, key=lambda x: x['name'])
    assert pmrep_table[0] == {'name': 'Time', 'value': '2021-04-26 05:42:25'}
    assert pmrep_table[1] == {'name': 'network.interface.collisions-lo', 'value': '2.000'}
    assert pmrep_table[2] == {'name': 'network.interface.out.packets-lo', 'value': '1.000'}
    assert pmrep_table[3] == {'name': 'swap.pagesout', 'value': '3.000'}

    pmrep_table = PMREPMetrics(context_wrap(PMREPMETRIC_DATA))
    assert sorted(pmrep_table.search(name__endswith='lo'), key=lambda x: x['name']) == [{'name': 'network.interface.collisions-lo', 'value': '3.000'}, {'name': 'network.interface.out.packets-lo', 'value': '1.000'}]
    assert sorted(pmrep_table.search(name__endswith='swap.pagesout'), key=lambda x: x['name']) == [{'name': 'swap.pagesout', 'value': '5.000'}]


def test_empty():
    with pytest.raises(SkipException) as e:
        PMREPMetrics(context_wrap(PMREPMETRIC_EMPTY_DATA))
    assert 'There is no data in the table' in str(e)


def test_wrong_data():
    with pytest.raises(SkipException) as e:
        PMREPMetrics(context_wrap(PMREPMETRIC_WRONG_DATA))
    assert 'There is no data in the table' in str(e)


def test_pmrep_doc_examples():
    env = {
        'pmrep_doc_obj': PMREPMetrics(context_wrap(PMREPMETRIC_DATA)),
        'pmrep_doc_obj_search': PMREPMetrics(context_wrap(PMREPMETRIC_DATA))
    }
    failed, total = doctest.testmod(pmrep, globs=env)
    assert failed == 0
