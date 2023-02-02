import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import sys_module
from insights.parsers.sys_module import (DMModUseBlkMq, KernelCrashKexecPostNotifiers, LpfcMaxLUNs, MaxLUNs, Ql2xMaxLUN,
                                         Ql2xmqSupport, SCSIModMaxReportLUNs, SCSIModUseBlkMq, VHostNetZeroCopyTx)
from insights.tests import context_wrap


SCSI_DM_MOD_USE_BLK_MQ_Y = """
Y
""".strip()
SCSI_DM_MOD_USE_BLK_MQ_N = """
N
""".strip()
QLA2XXX_QL2XMQSUPPORT = """
1
""".strip()

SCSI_DM_MOD_USE_BLK_MQ_UNKNOW_CASE = """
unknow_case
""".strip()

SCSI_DM_MOD_USE_BLK_MQ_EMPTY = """

""".strip()

ZERO_COPY = """
0
""".strip()


MAX_LUNS = """
512
""".strip()


def test_doc_examples():
    env = {
        'dm_mod_use_blk_mq': DMModUseBlkMq(context_wrap(SCSI_DM_MOD_USE_BLK_MQ_Y)),
        'scsi_mod_use_blk_mq': SCSIModUseBlkMq(context_wrap(SCSI_DM_MOD_USE_BLK_MQ_N)),
        'vhost_net_zero_copy_tx': VHostNetZeroCopyTx(context_wrap(ZERO_COPY)),
        'lpfc_max_luns': LpfcMaxLUNs(context_wrap(MAX_LUNS)),
        'ql2xmaxlun': Ql2xMaxLUN(context_wrap(MAX_LUNS)),
        'scsi_mod_max_report_luns': SCSIModMaxReportLUNs(context_wrap(MAX_LUNS)),
        'qla2xxx_ql2xmqsupport': Ql2xmqSupport(context_wrap(QLA2XXX_QL2XMQSUPPORT)),
        'crash_kexec_post_notifiers': KernelCrashKexecPostNotifiers(context_wrap(SCSI_DM_MOD_USE_BLK_MQ_Y))
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

    ql2xmqsuppor_copy_0 = Ql2xmqSupport(context_wrap(ZERO_COPY))
    assert ql2xmqsuppor_copy_0.is_on is False
    assert ql2xmqsuppor_copy_0.val == '0'

    ql2xmqsuppor_copy_1 = Ql2xmqSupport(context_wrap(QLA2XXX_QL2XMQSUPPORT))
    assert ql2xmqsuppor_copy_1.is_on is True
    assert ql2xmqsuppor_copy_1.val == '1'

    crash_kexec_post_notifiers_0 = KernelCrashKexecPostNotifiers(context_wrap(SCSI_DM_MOD_USE_BLK_MQ_N))
    assert crash_kexec_post_notifiers_0.is_on is False
    assert crash_kexec_post_notifiers_0.val == 'N'

    crash_kexec_post_notifiers_1 = KernelCrashKexecPostNotifiers(context_wrap(SCSI_DM_MOD_USE_BLK_MQ_Y))
    assert crash_kexec_post_notifiers_1.is_on is True
    assert crash_kexec_post_notifiers_1.val == 'Y'


def test_MaxLUNs():
    max_luns = MaxLUNs(context_wrap(MAX_LUNS))
    assert max_luns.val == 512

    lpfc_max_luns = LpfcMaxLUNs(context_wrap(MAX_LUNS))
    assert lpfc_max_luns.val == 512

    ql2xmaxlun = Ql2xMaxLUN(context_wrap(MAX_LUNS))
    assert ql2xmaxlun.val == 512

    scsi_mod_max_luns = SCSIModMaxReportLUNs(context_wrap(MAX_LUNS))
    assert scsi_mod_max_luns.val == 512


def test_class_exceptions():
    with pytest.raises(SkipComponent):
        dm_mod = DMModUseBlkMq(context_wrap(SCSI_DM_MOD_USE_BLK_MQ_EMPTY))
        assert dm_mod is None

    with pytest.raises(ValueError) as e:
        dm_mod_unknow = DMModUseBlkMq(context_wrap(SCSI_DM_MOD_USE_BLK_MQ_UNKNOW_CASE))
        dm_mod_unknow.is_on
    assert "Unexpected value unknow_case, please get raw data from attribute 'val' and tell is_on by yourself." in str(e)

    with pytest.raises(SkipComponent):
        max_luns = MaxLUNs(context_wrap(SCSI_DM_MOD_USE_BLK_MQ_EMPTY))
        assert max_luns is None

    with pytest.raises(ValueError) as e:
        max_luns_not_digit = MaxLUNs(context_wrap(SCSI_DM_MOD_USE_BLK_MQ_UNKNOW_CASE))
        max_luns_not_digit.val
    assert "Unexpected content: unknow_case" in str(e)

    with pytest.raises(SkipComponent):
        ql2xmqsuppor_empty = Ql2xmqSupport(context_wrap(SCSI_DM_MOD_USE_BLK_MQ_EMPTY))
        assert ql2xmqsuppor_empty is None

    with pytest.raises(ValueError) as e:
        ql2xmqsuppor_unknow = Ql2xmqSupport(context_wrap(SCSI_DM_MOD_USE_BLK_MQ_UNKNOW_CASE))
        ql2xmqsuppor_unknow.is_on
    assert "Unexpected value unknow_case, please get raw data from attribute 'val' and tell is_on by yourself." in str(e)

    with pytest.raises(ValueError) as e:
        crash_kexec_post_notifiers_unknow = KernelCrashKexecPostNotifiers(context_wrap(SCSI_DM_MOD_USE_BLK_MQ_UNKNOW_CASE))
        crash_kexec_post_notifiers_unknow.is_on
    assert "Unexpected value unknow_case, please get raw data from attribute 'val' and tell is_on by yourself." in str(e)
