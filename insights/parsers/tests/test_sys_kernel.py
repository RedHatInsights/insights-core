import doctest
import pytest

from insights.parsers import sys_kernel
from insights.parsers.sys_kernel import SchedRTRuntime
from insights.tests import context_wrap
from insights.core import ParseException

sys_kernel_content_1 = """
-1
""".strip()

sys_kernel_content_2 = """
950000
""".strip()

sys_kernel_content_3 = """
950000
-1
""".strip()

sys_kernel_content_4 = """
sss1
""".strip()


def test_sys_runtime_docs():
    failed, total = doctest.testmod(
        sys_kernel,
        globs={
            'srt': SchedRTRuntime(context_wrap(sys_kernel_content_2)),
        }
    )
    assert failed == 0


def test_sys_kernel_1():
    result = SchedRTRuntime(context_wrap(sys_kernel_content_1))
    assert result.runtime_us == -1


def test_exception():
    with pytest.raises(ParseException) as ex:
        SchedRTRuntime(context_wrap(sys_kernel_content_3))
    with pytest.raises(ParseException) as ex:
        SchedRTRuntime(context_wrap(sys_kernel_content_4))
