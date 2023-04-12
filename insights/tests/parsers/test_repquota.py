from insights.core.exceptions import SkipException
from insights.parsers import repquota
from insights.parsers.repquota import RepquotaAGNUV
from insights.tests import context_wrap
import doctest
import pytest

REPQUOTAAGNUV_ERR = """
""".strip()

REPQUOTAAGNUV = """
*** Report for user quotas on device /dev/sdc
Block grace time: 2days; Inode grace time: 2days
                        Block limits                File limits
User            used    soft    hard  grace    used  soft  hard  grace
----------------------------------------------------------------------
#0        --       0       0       0              3     0     0       
#1001     +-  563200  512000 1024000   none       1     0     0       
#1002     +-  579520  512000 1024000  44:58       2     0     0       

*** Status for user quotas on device /dev/sdc
Accounting: ON; Enforcement: ON
Inode: #131 (2 blocks, 2 extents)

*** Report for group quotas on device /dev/sdc
Block grace time: 7days; Inode grace time: 7days
                        Block limits                File limits
Group           used    soft    hard  grace    used  soft  hard  grace
----------------------------------------------------------------------
#0        --       0       0       0              3     0     0       
#1001     --  563200       0       0              1     0     0       
#1002     --  579520       0       0              2     0     0       

*** Status for group quotas on device /dev/sdc
Accounting: ON; Enforcement: ON
Inode: #132 (2 blocks, 2 extents)

""".strip()

REPQUOTAAGNUV_INVALID = """
*** Report for user quotas on device /dev/sdc
Block grace time: 2days; Inode grace time: 2days
                        Block limits                File limits
User            used    soft    hard  grace    used  soft  hard  grace
----------------------------------------------------------------------
#0        --       0       0       0              3     0     0       
#1001     +-    none    none    none   none       1     0     0       
#1002     +-  579520  512000 1024000  44:58       2     0     0       

*** Status for user quotas on device /dev/sdc
Accounting: ON; Enforcement: ON
Inode: #131 (2 blocks, 2 extents)

*** Report for group quotas on device /dev/sdc
Block grace time: 7days; Inode grace time: 7days
                        Block limits                File limits
Group           used    soft    hard  grace    used  soft  hard  grace
----------------------------------------------------------------------
#0        --       0       0       0              3     0     0       
#1001     --  563200       0       0              1     0     0       
#1002     --  579520       0       0              2     0     0       

*** Status for group quotas on device /dev/sdc
Accounting: ON; Enforcement: ON
Inode: #132 (2 blocks, 2 extents)

""".strip()


def test_repquota():
    results = RepquotaAGNUV(context_wrap(REPQUOTAAGNUV))
    assert len(results.group_quota.keys()) == 1
    assert len(results.group_quota['/dev/sdc']['quota_info']) == 3
    assert results.user_quota['/dev/sdc']['quota_info'][2] == {'user': '1002', 'status': '+-', 'block_used': '579520', 'block_soft': '512000', 'block_hard': '1024000', 'block_grace': '44:58', 'file_used': '2', 'file_soft': '0', 'file_hard': '0', 'file_grace': '0'}
    assert len(results.user_quota['/dev/sdc']['quota_info']) == 3
    assert results.group_quota['/dev/sdc']['enforcement'] is True


def test_repquota_err():
    with pytest.raises(SkipException):
        repquota.RepquotaAGNUV(context_wrap(REPQUOTAAGNUV_ERR))


def test_repquota_content_invalid():
    with pytest.raises(SkipException):
        repquota.RepquotaAGNUV(context_wrap(REPQUOTAAGNUV_INVALID))


def test_repquota_doc_examples():
    env = {
        'repquota': RepquotaAGNUV(context_wrap(REPQUOTAAGNUV))
    }
    failed, total = doctest.testmod(repquota, globs=env)
    assert failed == 0
