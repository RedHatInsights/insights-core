import doctest
import pytest
from insights.parsers import sys_bus, ParseException, SkipException
from insights.parsers.sys_bus import CdcWDM 
from insights.tests import context_wrap


SYS_DEVICE_USAGE = """
1
""".strip()


def test_netstat_doc_examples():
    env = {
        'device_usage': CdcWDM(context_wrap(SYS_DEVICE_USAGE)),
    }
    failed, total = doctest.testmod(sys_bus, globs=env)
    assert failed == 0


def test_bond_dynamic_lb_class():
    device_usage = CdcWDM(context_wrap(SYS_DEVICE_USAGE))
    assert device_usage.device_usage_cnt == 1
    assert device_usage.device_in_use == True
