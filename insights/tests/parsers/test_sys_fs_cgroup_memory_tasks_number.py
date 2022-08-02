from insights.parsers.sys_fs_cgroup_memory_tasks_number import SysFsCgroupMemoryTasksNumber
from insights.tests import context_wrap


TASKS_NUMBER = """
260
""".strip()


def test_sys_fs_cgroup_memory_tasks_number():
    sys_fs_cgroup_memory_tasks_number_content = SysFsCgroupMemoryTasksNumber(context_wrap(TASKS_NUMBER))
    assert sys_fs_cgroup_memory_tasks_number_content.number == 260
