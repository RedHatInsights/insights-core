from insights.core.exceptions import SkipComponent
from insights.parsers import xfs_quota
from insights.parsers.xfs_quota import XFSQuotaState
from insights.tests import context_wrap
import doctest
import pytest

XFSQUOTASTATE_ERR = """
""".strip()

XFSQUOTASTATE = """
User quota state on /sdd (/dev/sdd)
  Accounting: ON
  Enforcement: ON
  Inode: #131 (1 blocks, 1 extents)
Blocks grace time: [7 days]
Blocks max warnings: 5
Inodes grace time: [7 days]
Inodes max warnings: 5
Realtime Blocks grace time: [7 days]
Group quota state on /sdd (/dev/sdd)
  Accounting: OFF
  Enforcement: OFF
  Inode: N/A
Blocks grace time: [--------]
Blocks max warnings: 0
Inodes grace time: [--------]
Inodes max warnings: 0
Realtime Blocks grace time: [--------]
User quota state on /sdb (/dev/sdb)
  Accounting: ON
  Enforcement: ON
  Inode: #131 (2 blocks, 2 extents)
Blocks grace time: [6 days]
Blocks max warnings: 10
Inodes grace time: [6 days]
Inodes max warnings: 5
Realtime Blocks grace time: [6 days]
Group quota state on /sdb (/dev/sdb)
  Accounting: ON
  Enforcement: ON
  Inode: #137 (2 blocks, 2 extents)
Blocks grace time: [7 days]
Blocks max warnings: 5
Inodes grace time: [7 days]
Inodes max warnings: 5
Realtime Blocks grace time: [7 days]
User quota state on /sdc (/dev/sdc)
  Accounting: ON
  Enforcement: ON
  Inode: #131 (2 blocks, 2 extents)
Blocks grace time: [7 days]
Blocks max warnings: 20
Inodes grace time: [7 days]
Inodes max warnings: 5
Realtime Blocks grace time: [7 days]
Group quota state on /sdc (/dev/sdc)
  Accounting: ON
  Enforcement: ON
  Inode: #132 (2 blocks, 2 extents)
Blocks grace time: [7 days]
Blocks max warnings: 5
Inodes grace time: [7 days]
Inodes max warnings: 5
Realtime Blocks grace time: [7 days]
""".strip()


def test_repquota():
    results = XFSQuotaState(context_wrap(XFSQUOTASTATE))
    assert len(results.group_quota) == 3
    assert results.group_quota['/dev/sdd']['device'] == '/dev/sdd'
    assert results.group_quota['/dev/sdd']['accounting'] == 'OFF'
    assert results.group_quota['/dev/sdd']['blocks_grace_time'] is None
    assert len(results.user_quota) == 3
    assert results.group_quota['/dev/sdc']['accounting'] == 'ON'
    assert results.user_quota['/dev/sdc'] == {'device': '/dev/sdc', 'accounting': 'ON', 'enforcement': 'ON', 'inode': '#131 (2 blocks, 2 extents)', 'blocks_grace_time': '7 days', 'blocks_max_warnings': '20', 'inodes_grace_time': '7 days', 'inodes_max_warnings': '5', 'realtime_blocks_grace_time': '7 days'}


def test_repquota_err():
    with pytest.raises(SkipComponent):
        XFSQuotaState(context_wrap(XFSQUOTASTATE_ERR))


def test_repquota_doc_examples():
    env = {
        'quota_state': XFSQuotaState(context_wrap(XFSQUOTASTATE))
    }
    failed, total = doctest.testmod(xfs_quota, globs=env)
    assert failed == 0
