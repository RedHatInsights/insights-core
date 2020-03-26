import doctest
import pytest

from insights.parsers import sys_kernel
from insights.parsers.sys_kernel import SchedRTRuntime, SchedFeatures
from insights.tests import context_wrap
from insights.core import ParseException

SYS_KERNEL_RUNTIME_CONTENT_1 = """
-1
""".strip()

SYS_KERNEL_RUNTIME_CONTENT_2 = """
950000
""".strip()

SYS_KERNEL_RUNTIME_CONTENT_3 = """
950000
-1
""".strip()

SYS_KERNEL_RUNTIME_CONTENT_4 = """
sss1
""".strip()

SYS_KERNEL_FEATURES = """
GENTLE_FAIR_SLEEPERS START_DEBIT NO_NEXT_BUDDY LAST_BUDDY CACHE_HOT_BUDDY
""".strip()


def test_sys_runtime_docs():
    failed, total = doctest.testmod(
        sys_kernel,
        globs={
            'srt': SchedRTRuntime(context_wrap(SYS_KERNEL_RUNTIME_CONTENT_2)),
            'sfs': SchedFeatures(context_wrap(SYS_KERNEL_FEATURES)),
        }
    )
    assert failed == 0


def test_sys_kernel_1():
    result = SchedRTRuntime(context_wrap(SYS_KERNEL_RUNTIME_CONTENT_1))
    assert result.runtime_us == -1


def test_exception():
    with pytest.raises(ParseException):
        SchedRTRuntime(context_wrap(SYS_KERNEL_RUNTIME_CONTENT_3))
    with pytest.raises(ParseException):
        SchedRTRuntime(context_wrap(SYS_KERNEL_RUNTIME_CONTENT_4))
