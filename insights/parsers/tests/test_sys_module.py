import doctest
import pytest
from insights.parsers import sys_module, SkipException
from insights.parsers.sys_module import DMModUseBlkMq, SCSIModUseBlkMq, VHostNetZeroCopyTx
from insights.tests import context_wrap


SCSI_DM_MOD_USE_BLK_MQ_Y = """
Y
""".strip()
SCSI_DM_MOD_USE_BLK_MQ_N = """
N
""".strip()
SCSI_DM_MOD_USE_BLK_MQ_UNKNOW_CASE = """
unknow_case
""".strip()

SCSI_DM_MOD_USE_BLK_MQ_EMPTY = """

""".strip()

ZERO_COPY = """
0
""".strip()


def test_doc_examples():
    env = {
        'dm_mod_use_blk_mq': DMModUseBlkMq(context_wrap(SCSI_DM_MOD_USE_BLK_MQ_Y)),
        'scsi_mod_use_blk_mq': SCSIModUseBlkMq(context_wrap(SCSI_DM_MOD_USE_BLK_MQ_N)),
        'vhost_net_zero_copy_tx': VHostNetZeroCopyTx(context_wrap(ZERO_COPY)),
    }
    failed, total = doctest.testmod(sys_module, globs=env)
    assert failed == 0


def test_XModUseBlkMq():
    dm_mod_y = DMModUseBlkMq(context_wrap(SCSI_DM_MOD_USE_BLK_MQ_Y))
    assert dm_mod_y.is_on is True
    assert dm_mod_y.val == 'Y'

    scsi_mod_n = SCSIModUseBlkMq(context_wrap(SCSI_DM_MOD_USE_BLK_MQ_N))
    assert scsi_mod_n.is_on is False
    assert scsi_mod_n.val == 'N'

    dm_mod_unknow = DMModUseBlkMq(context_wrap(SCSI_DM_MOD_USE_BLK_MQ_UNKNOW_CASE))
    assert dm_mod_unknow.val == 'unknow_case'

    zero_copy_0 = VHostNetZeroCopyTx(context_wrap(ZERO_COPY))
    assert zero_copy_0.is_on is False
    assert zero_copy_0.val == '0'

    zero_copy_1 = VHostNetZeroCopyTx(context_wrap(ZERO_COPY.replace('0', '1')))
    assert zero_copy_1.is_on is True
    assert zero_copy_1.val == '1'


def test_class_exceptions():
    with pytest.raises(SkipException):
        dm_mod = DMModUseBlkMq(context_wrap(SCSI_DM_MOD_USE_BLK_MQ_EMPTY))
        assert dm_mod is None

    with pytest.raises(ValueError) as e:
        dm_mod_unknow = DMModUseBlkMq(context_wrap(SCSI_DM_MOD_USE_BLK_MQ_UNKNOW_CASE))
        dm_mod_unknow.is_on
    assert "Unexpected value unknow_case, please get raw data from attribute 'val' and tell is_on by yourself." in str(e)
