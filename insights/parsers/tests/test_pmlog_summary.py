import pytest
import doctest

from insights.tests import context_wrap
from insights.parsers import SkipComponent
from insights.parsers import pmlog_summary
from insights.parsers.pmlog_summary import PmLogSummary

PMLOG = """
mem.util.used  3133919.812 Kbyte
mem.physmem  3997600.000 Kbyte
kernel.all.cpu.user  0.003 none
kernel.all.cpu.sys  0.004 none
kernel.all.cpu.nice  0.000 none
kernel.all.cpu.steal  0.000 none
kernel.all.cpu.idle  3.986 none
disk.all.total  0.252 count / sec
"""

PMLOG_EMPTY = """
"""


def test_pmlog_summary():
    pmlog_summary = PmLogSummary(context_wrap(PMLOG))
    assert len(pmlog_summary) == 8
    assert pmlog_summary['mem.util.used'] == '3133919.812 Kbyte'
    assert pmlog_summary['disk.all.total'] == '0.252 count / sec'
    assert 'not.present' not in pmlog_summary
    assert 'kernel.all.cpu.sys' in pmlog_summary


def test_pmlog_summmary():
    with pytest.raises(SkipComponent):
        PmLogSummary(context_wrap(PMLOG_EMPTY))


def test_doc_examples():
    env = {
        'pmlog_summary': PmLogSummary(context_wrap(PMLOG))
    }
    failed, _ = doctest.testmod(pmlog_summary, globs=env)
    assert failed == 0
