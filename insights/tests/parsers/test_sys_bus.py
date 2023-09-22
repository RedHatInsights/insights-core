import doctest
import pytest

from insights.core.exceptions import ParseException
from insights.parsers import sys_bus
from insights.parsers.sys_bus import CdcWDM
from insights.tests import context_wrap


SYS_DEVICE_USAGE = """
1
""".strip()

SYS_DEVICE_USAGE_EMPTY = """

""".strip()

SYS_DEVICE_USAGE_INVALID = """
not valid content
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
    assert device_usage.device_in_use is True


def test_class_exceptions():
    with pytest.raises(ParseException) as exc:
        device_usage = CdcWDM(context_wrap(SYS_DEVICE_USAGE_EMPTY))
        assert device_usage is None
    assert 'Invalid Content!' in str(exc)
    with pytest.raises(ParseException) as exc:
        device_usage = CdcWDM(context_wrap(SYS_DEVICE_USAGE_INVALID))
        assert device_usage is None
    assert 'Invalid Content!' in str(exc)
