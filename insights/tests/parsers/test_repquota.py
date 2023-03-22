import pytest
import doctest
from insights.core.exceptions import ParseException
from insights.parsers.repquota import Repquota
from insights.parsers import repquota
from insights.tests import context_wrap

REPQUOTA_ERR = """
""".strip()

REPQUOTA = """
*** Report for user quotas on device /dev/sdb
Block grace time: 7days; Inode grace time: 7days
                        Block limits                File limits
User            used    soft    hard  grace    used  soft  hard  grace
----------------------------------------------------------------------
root      --       0       0       0              3     0     0
user1     +-   61440   51200  102400  6days       1     0     0

*** Status for user quotas on device /dev/sdb
Accounting: ON; Enforcement: ON
Inode: #131 (2 blocks, 2 extents)

*** Report for user quotas on device /dev/sdc
Block grace time: 7days; Inode grace time: 7days
                        Block limits                File limits
User            used    soft    hard  grace    used  soft  hard  grace
----------------------------------------------------------------------
root      --      20       0       0              2     0     0
user2     +-  100000   50000  100000  7days       1     0     0

Statistics:
Total blocks: 7
Data blocks: 1
Entries: 2
Used average: 2.000000

*** Report for group quotas on device /dev/sdb
Block grace time: 7days; Inode grace time: 7days
                        Block limits                File limits
Group           used    soft    hard  grace    used  soft  hard  grace
----------------------------------------------------------------------
root      --       0       0       0              3     0     0
group1    --   61440       0       0              1     0     0

*** Status for group quotas on device /dev/sdb
Accounting: ON; Enforcement: OFF
Inode: #132 (2 blocks, 2 extents)

*** Report for group quotas on device /dev/sdc
Block grace time: 7days; Inode grace time: 7days
                        Block limits                File limits
Group           used    soft    hard  grace    used  soft  hard  grace
----------------------------------------------------------------------
root      --      20       0       0              2     0     0
group1    --  100000       0       0              3     2     4  6days

Statistics:
Total blocks: 7
Data blocks: 1
Entries: 2
Used average: 2.000000
""".strip()


def test_repquota():
    results = Repquota(context_wrap(REPQUOTA))
    assert len(results.group_quota.keys()) == 2
    assert len(results.group_quota['/dev/sdb']['quota_info']) == 2
    assert results.group_quota['/dev/sdb']['quota_info'][0] == {'group': 'root', 'flag': '--', 'block_used': '0', 'block_soft': '0', 'block_hard': '0', 'block_grace': '-', 'file_used': '3', 'file_soft': '0', 'file_hard': '0', 'file_grace': '-'}
    assert len(results.user_quota['/dev/sdc']['quota_info']) == 2
    assert 'enforcement' not in results.user_quota['/dev/sdc']
    assert results.user_quota['/dev/sdb']['enforcement'] is True


def test_repquota_err():
    with pytest.raises(ParseException) as pe:
        Repquota(context_wrap(REPQUOTA_ERR))
        assert 'empty file' in str(pe)


def test_repquota_doc_examples():
    env = {
        'repquota': Repquota(context_wrap(REPQUOTA))
    }
    failed, total = doctest.testmod(repquota, globs=env)
    assert failed == 0
