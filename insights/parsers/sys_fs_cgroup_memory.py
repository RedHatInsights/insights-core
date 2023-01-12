"""
Memory controller information of cgroup - ``/sys/fs/cgroup/memeory``
====================================================================

Parser included in this module is:

SysFsCgroupUniqMemorySwappiness - Datasource ``sys_fs_cgroup_uniq_memory_swappiness``
-------------------------------------------------------------------------------------
"""
from collections import namedtuple

from insights.core import Parser
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.sys_fs_cgroup_uniq_memory_swappiness)
class SysFsCgroupUniqMemorySwappiness(Parser):
    """
    Class to parse the datasource ``sys_fs_cgroup_uniq_memory_swappiness`` output.

    Sample output of datasource looks like::
        10   1
        60   66

    The two columns that are output are:
    1. value - the value of memory.swappiness
    2. count - how many memory.swappiness files have the same setting

    Examples:
        >>> type(sys_fs_cgroup_uniq_memory_swappiness)
        <class 'insights.parsers.sys_fs_cgroup_memory_swappiness.SysFsCgroupUniqMemorySwappiness'>
        >>> sys_fs_cgroup_uniq_memory_swappiness.stats[0]
        MemorySwappiness(count=1, value=10)
        >>> sys_fs_cgroup_uniq_memory_swappiness.stats[0].count
        1
        >>> sys_fs_cgroup_uniq_memory_swappiness.stats[1].value
        60

    Attributes:
        stats (list): a list of ``MemorySwappiness`` objects
    """

    MemorySwappiness = namedtuple('MemorySwappiness', ['value', 'count'])
    """namedtuple: Structure to hold a line of ``sys_fs_cgroup_uniq_memory_swappiness`` datasource."""

    def parse_content(self, content):
        self.stats = []
        for line in content:
            parts = line.split()
            self.stats.append(self.MemorySwappiness(int(parts[0]), int(parts[1])))
