from insights.parsers.sys_fs_cgroup_memory import SysFsCgroupUniqMemorySwappiness
from insights.tests import context_wrap

UNIQ_MEMORY_SWAPPINESS = """
10  1
60  66
"""


def test_sys_fs_cgroup_uniq_memory_swappiness():
    items = SysFsCgroupUniqMemorySwappiness(context_wrap(UNIQ_MEMORY_SWAPPINESS))
    assert items is not None
    assert len(items.stats) == 2
    assert items.stats[0] == SysFsCgroupUniqMemorySwappiness.MemorySwappiness(
        count=1,
        value=10)
    assert items.stats[1].value == 60
