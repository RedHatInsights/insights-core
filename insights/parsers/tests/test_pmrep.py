import pytest
import doctest
from insights.tests import context_wrap
from insights.parsers import SkipException
from insights.parsers import pmrep
from insights.parsers.pmrep import PMREPMetrics

PMREPMETRIC_DATA = """
Time,"network.interface.out.packets-lo","network.interface.out.packets-eth0","network.interface.collisions-lo","network.interface.collisions-eth0","swap.pagesout"
2021-04-26 05:42:24,,,,,
2021-04-26 05:42:25,1.000,2.000,3.000,4.000,5.000
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
    assert pmrep_table[0] == {'Time': '2021-04-26 05:42:25'}
    assert pmrep_table[1] == {'network.interface.out.packets-lo': '1.000'}
    assert pmrep_table[2] == {'network.interface.out.packets-eth0': '2.000'}
    assert pmrep_table[3] == {'network.interface.collisions-lo': '3.000'}
    assert pmrep_table[4] == {'network.interface.collisions-eth0': '4.000'}
    assert pmrep_table[5] == {'swap.pagesout': '5.000'}

    pmrep_table = PMREPMetrics(context_wrap(PMREPMETRIC_DATA_2))
    assert pmrep_table[0] == {'Time': '2021-04-26 05:42:25'}
    assert pmrep_table[1] == {'network.interface.out.packets-lo': '1.000'}
    assert pmrep_table[2] == {'network.interface.collisions-lo': '2.000'}
    assert pmrep_table[3] == {'swap.pagesout': '3.000'}


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
    }
    failed, total = doctest.testmod(pmrep, globs=env)
    assert failed == 0
