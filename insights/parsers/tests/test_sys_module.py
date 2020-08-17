import doctest
import pytest
from insights.parsers import sys_module, ParseException, SkipException
from insights.parsers.sys_module import DMModUseBlkMq, SCSIModUseBlkMq
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


def test_doc_examples():
    env = {
        'dm_mod_use_blk_mq': DMModUseBlkMq(context_wrap(SCSI_DM_MOD_USE_BLK_MQ_Y)),
        'scsi_mod_use_blk_mq': SCSIModUseBlkMq(context_wrap(SCSI_DM_MOD_USE_BLK_MQ_N)),
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


def test_class_exceptions():
    with pytest.raises(SkipException):
        dm_mod = DMModUseBlkMq(context_wrap(SCSI_DM_MOD_USE_BLK_MQ_EMPTY))
        assert dm_mod is None

    with pytest.raises(ParseException) as e:
        dm_mod_unknow = DMModUseBlkMq(context_wrap(SCSI_DM_MOD_USE_BLK_MQ_UNKNOW_CASE))
        dm_mod_unknow.is_on
    assert "Unknown value: unknow_case" in str(e)
