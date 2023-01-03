from insights.parsers.sys_fs_cgroup_memory import SysFsCgroupUniqMemorySwappiness
from insights.tests import context_wrap

UNIQ_MEMORY_SWAPPINESS = """
10  1
60  66
"""


def test_sys_fs_cgroup_uniq_memory_swappiness():
    items = SysFsCgroupUniqMemorySwappiness(context_wrap(UNIQ_MEMORY_SWAPPINESS))
    assert items is not None
    assert len(items.data) == 2
    assert items.data[0] == SysFsCgroupUniqMemorySwappiness.MemorySwappiness(
        count=1,
        value=10)
    assert items.data[1].value == 60
