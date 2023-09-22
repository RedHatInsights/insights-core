import pytest

from insights.core.exceptions import ParseException
from insights.parsers.proc_limits import HttpdLimits, MysqldLimits, OvsVswitchdLimits
from insights.tests import context_wrap

PROC_LIMITS_ERR = """
cat: /proc/1100/limits: No such file or directory
""".strip()

PROC_LIMITS = """
Limit                     Soft Limit           Hard Limit           Units
Max cpu time              unlimited            unlimited            seconds
Max file size             unlimited            unlimited            bytes
Max data size             unlimited            unlimited            bytes
Max stack size            10485760             unlimited            bytes
Max core file size        0                    unlimited            bytes
Max resident set          unlimited            unlimited            bytes
Max processes             9                    99                   processes
Max open files            1024                 4096                 files
Max locked memory         65536                65536                bytes
Max address space         unlimited            unlimited            bytes
Max file locks            unlimited            unlimited            locks
Max pending signals       15211                15211                signals
Max msgqueue size         819200               819200               bytes
Max nice priority         0                    0
Max realtime priority     0                    0
Max realtime timeout      unlimited            unlimited            us
""".strip()


def test_httpd_limits():
    results = HttpdLimits(context_wrap(PROC_LIMITS))
    assert len(results) == 16
    assert "max_processes" in results
    assert results.max_processes.hard_limit == '99'
    assert results.max_processes.soft_limit == '9'
    assert results.max_processes.units == 'processes'
    assert results.max_nice_priority.hard_limit == '0'
    assert results.max_nice_priority.units == ''
    for r in results:
        if 'Max cpu time' == r['Limit']:
            assert r['Hard_Limit'] == 'unlimited'
            assert r['Soft_Limit'] == 'unlimited'
        if 'Max realtime timeout' == r['Limit']:
            assert r['Units'] == 'us'


def test_proc_limits_err():
    with pytest.raises(ParseException) as pe:
        HttpdLimits(context_wrap(PROC_LIMITS_ERR))
        assert PROC_LIMITS_ERR in str(pe)

    with pytest.raises(ParseException) as pe:
        HttpdLimits(context_wrap(''))
        assert 'empty file' in str(pe)


def test_mysqld_limits():
    results = MysqldLimits(context_wrap(PROC_LIMITS))
    assert results.max_open_files.hard_limit == '4096'
    assert results.max_open_files.soft_limit == '1024'
    assert len(results) == 16


def test_ovs_vswitchd_limits():
    results = OvsVswitchdLimits(context_wrap(PROC_LIMITS))
    assert "max_open_files" in results
    assert results.max_open_files.units == 'files'
    assert results.max_open_files.hard_limit == '4096'
