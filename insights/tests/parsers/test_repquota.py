from insights.core.exceptions import SkipException
from insights.parsers import repquota
from insights.parsers.repquota import RepquotaAGNPUV
from insights.tests import context_wrap
import doctest
import pytest

REPQUOTAAGNPUV_ERR = """
""".strip()

REPQUOTAAGNPUV = """
*** Report for user quotas on device /dev/sdb
Block grace time: 7days; Inode grace time: 7days
                        Block limits                File limits
User            used    soft    hard  grace    used  soft  hard  grace
----------------------------------------------------------------------
#0        --    5120       0       0      0       4     0     0      0
#1009     +-   61440   51200  102400 1679983770       1     0     0      0
#1010     --       0   51200  102400      0       0     0     0      0
#1011     +-  107520   51200  307200 1680640819       2     0     0      0
#1012     --   51200       0       0      0       1     0     0      0
#1013     --       0   51200  102400      0       0     0     0      0

*** Status for user quotas on device /dev/sdb
Accounting: ON; Enforcement: ON
Inode: #131 (2 blocks, 2 extents)

*** Report for group quotas on device /dev/sdb
Block grace time: 7days; Inode grace time: 7days
                        Block limits                File limits
Group           used    soft    hard  grace    used  soft  hard  grace
----------------------------------------------------------------------
#0        --    5120       0       0      0       4     0     0      0
#1004     --   61440       0       0      0       1     0     0      0
#1005     --   51200  972800 1048576      0       1     0     0      0
#1011     --  107520       0       0      0       2     0     0      0

*** Status for group quotas on device /dev/sdb
Accounting: ON; Enforcement: ON
Inode: #132 (2 blocks, 2 extents)
""".strip()


def test_repquota():
    results = RepquotaAGNPUV(context_wrap(REPQUOTAAGNPUV))
    assert len(results.group_quota.keys()) == 1
    assert len(results.group_quota['/dev/sdb']['quota_info']) == 4
    assert results.group_quota['/dev/sdb']['quota_info'][1] == {'group': '1004', 'status': '--', 'block_used': '61440', 'block_soft': '0', 'block_hard': '0', 'block_grace': '0', 'file_used': '1', 'file_soft': '0', 'file_hard': '0', 'file_grace': '0'}
    assert len(results.user_quota['/dev/sdb']['quota_info']) == 6
    assert results.user_quota['/dev/sdb']['enforcement'] is True


def test_repquota_err():
    with pytest.raises(SkipException):
        repquota.RepquotaAGNPUV(context_wrap(REPQUOTAAGNPUV_ERR))


def test_repquota_doc_examples():
    env = {
        'repquota': RepquotaAGNPUV(context_wrap(REPQUOTAAGNPUV))
    }
    failed, total = doctest.testmod(repquota, globs=env)
    assert failed == 0
