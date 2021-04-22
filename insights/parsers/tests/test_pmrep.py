import pytest
import doctest
from insights.tests import context_wrap
from insights.parsers import SkipException
from insights.parsers import pmrep
from insights.parsers.pmrep import PMREPMetrics

PMREPMETRIC_DATA = """
  n.i.o.packets  n.i.o.packets  n.i.collisions  n.i.collisions  s.pagesout
           eth0             lo            eth0              lo
        count/s        count/s         count/s         count/s     count/s
            N/A            N/A             N/A             N/A         N/A
          1.000          2.000           3.000           4.000       5.000
"""

PMREPMETRIC_DATA_2 = """
  n.i.o.packets  n.i.collisions  s.pagesout
             lo              lo
        count/s         count/s     count/s
            N/A             N/A         N/A
          1.000           2.000       5.000
"""

PMREPMETRIC_DATA_3 = """
  n.i.o.packets  n.i.o.packets  n.i.o.packets  n.i.collisions  n.i.collisions  n.i.collisions  s.pagesout
           eth0             lo           eth1            eth0              lo            eth1
        count/s        count/s        count/s         count/s         count/s         count/s     count/s
            N/A            N/A            N/A             N/A             N/A             N/A         N/A
          1.000          2.000          3.000           4.000           5.000           6.000       5.000
"""

PMREPMETRIC_EMPTY_DATA = """
""".strip()


def test_pmrep_info():
    pmrep = PMREPMetrics(context_wrap(PMREPMETRIC_DATA))
    assert pmrep.data['n.i.o.packets'] == [{'eth0': '1.000'}, {'lo': '2.000'}]
    assert pmrep.data['n.i.collisions'] == [{'eth0': '3.000'}, {'lo': '4.000'}]
    assert pmrep.data['s.pagesout'] == ['5.000']

    pmrep = PMREPMetrics(context_wrap(PMREPMETRIC_DATA_2))
    assert pmrep.data['n.i.o.packets'] == [{'lo': '1.000'}]
    assert pmrep.data['n.i.collisions'] == [{'lo': '2.000'}]
    assert pmrep.data['s.pagesout'] == ['5.000']

    pmrep = PMREPMetrics(context_wrap(PMREPMETRIC_DATA_3))
    assert pmrep.data['n.i.o.packets'] == [{'eth0': '1.000'}, {'lo': '2.000'}, {'eth1': '3.000'}]
    assert pmrep.data['n.i.collisions'] == [{'eth0': '4.000'}, {'lo': '5.000'}, {'eth1': '6.000'}]
    assert pmrep.data['s.pagesout'] == ['5.000']


def test_empty():
    with pytest.raises(SkipException) as e:
        PMREPMetrics(context_wrap(PMREPMETRIC_EMPTY_DATA))
    assert 'Empty content' in str(e)


def test_pmrep_doc_examples():
    env = {
        'pmrep_doc_obj': PMREPMetrics(context_wrap(PMREPMETRIC_DATA)),
    }
    failed, total = doctest.testmod(pmrep, globs=env)
    assert failed == 0
