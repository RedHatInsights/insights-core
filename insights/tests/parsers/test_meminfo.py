from insights.parsers import meminfo
from insights.tests import context_wrap

import pytest

"""
The following meminfo comes from a RHEL 7.1 box.  There are three values that
are currently accounted for in MemInfo that aren't in here:

- CmaTotal
- CmaFree
- DirectMap1G
"""

MEMINFO = """
MemTotal:        8009912 kB
MemFree:          538760 kB
MemAvailable:    6820236 kB
Buffers:          157048 kB
Cached:          4893932 kB
SwapCached:          120 kB
Active:          2841500 kB
Inactive:        2565560 kB
Active(anon):     311596 kB
Inactive(anon):   505800 kB
Active(file):    2529904 kB
Inactive(file):  2059760 kB
Unevictable:           0 kB
Mlocked:               0 kB
SwapTotal:       3145724 kB
SwapFree:        3136352 kB
Dirty:               140 kB
Writeback:             0 kB
AnonPages:        355484 kB
Mapped:            51988 kB
Shmem:            461316 kB
Slab:            1982652 kB
SReclaimable:    1945228 kB
SUnreclaim:        37424 kB
KernelStack:        3568 kB
PageTables:         8504 kB
NFS_Unstable:          0 kB
Bounce:                0 kB
WritebackTmp:          0 kB
CommitLimit:     7150680 kB
Committed_AS:    1218948 kB
VmallocTotal:   34359738367 kB
VmallocUsed:      122268 kB
VmallocChunk:   34359607064 kB
HardwareCorrupted:     0 kB
AnonHugePages:    135168 kB
HugePages_Total:       0
HugePages_Free:        0
HugePages_Rsvd:        0
HugePages_Surp:        0
Hugepagesize:       2048 kB
DirectMap4k:       71664 kB
DirectMap2M:     8316928 kB
""".strip()


def test_meminfo():
    values = []
    for l in MEMINFO.splitlines():
        values.append(l.split()[1].strip())
    m = meminfo.MemInfo(context_wrap(MEMINFO))
    actual = [
        m.total, m.free, m.available, m.buffers, m.cached, m.swap.cached,
        m.active, m.inactive, m.anon.active, m.anon.inactive, m.file.active,
        m.file.inactive, m.unevictable, m.mlocked, m.swap.total, m.swap.free,
        m.dirty, m.writeback, m.anon.pages, m.mapped, m.shmem, m.slab.total,
        m.slab.reclaimable, m.slab.unreclaimable, m.kernel_stack, m.page_tables,
        m.nfs_unstable, m.bounce, m.writeback_tmp, m.commit.limit, m.commit.total,
        m.vmalloc.total, m.vmalloc.used, m.vmalloc.chunk, m.corrupted,
        m.huge_pages.anon, m.huge_pages.total, m.huge_pages.free,
        m.huge_pages.reserved, m.huge_pages.surplus, m.huge_pages.size,
        m.direct_map.kb, m.direct_map.mb
    ]
    for i in range(len(actual)):
        assert isinstance(actual[i], int), "Line %d's value is not an int: %s" % (i, type(actual[i]))
        assert actual[i] == int(values[i]) * 1024, "Line %d failed to match" % i

    assert m.swap.used == (int(values[14]) - int(values[15]) - int(values[5])) * 1024
    assert m.used == (8009912 - 538760) * 1024


MEMINFO_SHORT = """
MemTotal:        8009912 kB
MemAvailable:    6820236 kB
"""


def test_meminfo_short():
    # Test the various calculated properties when little or no data is
    # available.
    m = meminfo.MemInfo(context_wrap(MEMINFO_SHORT))
    with pytest.raises(TypeError):
        assert m.swap.used is None
    with pytest.raises(TypeError):
        assert m.used is None


def test_using_huge_pages():
    t = [
        "AnonHugePages:    135168 kB",
        "HugePages_Total:       0"
    ]
    m = meminfo.MemInfo(context_wrap(t))
    assert not m.huge_pages.using
    assert m.huge_pages.using_transparent
    t = [
        "AnonHugePages:    0 kB",
        "HugePages_Total:  123456",
        "HugePages_Rsvd:     4096",
    ]
    m = meminfo.MemInfo(context_wrap(t))
    assert m.huge_pages.using
    assert not m.huge_pages.using_transparent
    assert m.huge_pages.total == 123456
    assert m.huge_pages.reserved == 4096
