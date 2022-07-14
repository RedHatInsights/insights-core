from insights.parsers.sys_fs_cgroup_memory_tasks_number import SysFsCgroupMemoryTasksNumber
from insights.parsers import SkipException
from insights.tests import context_wrap
import pytest

Tasks_Number = """
260
""".strip()

Tasks_Number_INVALID = """
unknow_case
""".strip()

Tasks_Number_EMPTY = """
""".strip()


def test_sys_fs_cgroup_memory_tasks_number():
    sys_fs_cgroup_memory_tasks_number_content = SysFsCgroupMemoryTasksNumber(context_wrap(Tasks_Number))
    assert sys_fs_cgroup_memory_tasks_number_content.number == 260


def test_exception():
    with pytest.raises(SkipException) as e:
        SysFsCgroupMemoryTasksNumber(context_wrap(Tasks_Number_INVALID))
    assert 'Output is invalid' in str(e)

    with pytest.raises(SkipException) as e:
        SysFsCgroupMemoryTasksNumber(context_wrap(Tasks_Number_EMPTY))
    assert "No output" in str(e)
