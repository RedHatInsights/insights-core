import pytest
import doctest
from insights.parsers import grubby
from insights.parsers.grubby import GrubbyDefaultIndex, GrubbyDefaultKernel
from insights.parsers.grubby import GrubbyInfoALL
from insights.tests import context_wrap
from insights.parsers import SkipException

DEFAULT_INDEX_1 = '0'
DEFAULT_INDEX_2 = '1'
DEFAULT_INDEX_3 = ''
DEFAULT_INDEX_4 = '-2'

DEFAULT_KERNEL = """
/boot/vmlinuz-2.6.32-573.el6.x86_64
""".strip()

INFO_ALL_RHEL6 = """
boot=/dev/vda
index=0
kernel=/vmlinuz-2.6.32-754.9.1.el6.x86_64
args="ro rd_NO_LUKS rd_NO_LVM LANG=en_US.UTF-8 rd_NO_MD SYSFONT=latarcyrheb-sun16 crashkernel=auto  KEYBOARDTYPE=pc KEYTABLE=us rd_NO_DM rhgb quiet"
root=UUID=1b46779e-4fae-442d-a2ac-dd6d8563ff3e
initrd=/boot/initramfs-2.6.32-754.9.1.el6.x86_64.img
index=1
kernel=/vmlinuz-2.6.32-573.el6.x86_64
args="ro rd_NO_LUKS rd_NO_LVM LANG=en_US.UTF-8 rd_NO_MD SYSFONT=latarcyrheb-sun16 crashkernel=auto  KEYBOARDTYPE=pc KEYTABLE=us rd_NO_DM rhgb quiet"
root=UUID=1b46779e-4fae-442d-a2ac-dd6d8563ff3e
initrd=/boot/initramfs-2.6.32-573.el6.x86_64.img
""".strip()

INFO_ALL_RHEL7 = """
index=0
kernel=/boot/vmlinuz-3.10.0-957.1.3.el7.x86_64
args="ro crashkernel=auto rd.lvm.lv=rhel/root rd.lvm.lv=rhel/swap rhgb quiet LANG=en_US.UTF-8"
root=/dev/mapper/rhel-root
initrd=/boot/initramfs-3.10.0-957.1.3.el7.x86_64.img
title=Red Hat Enterprise Linux Server (3.10.0-957.1.3.el7.x86_64) 7.5 (Maipo)
index=1
kernel=/boot/vmlinuz-3.10.0-862.14.4.el7.x86_64
args="ro crashkernel=auto rd.lvm.lv=rhel/root rd.lvm.lv=rhel/swap rhgb quiet LANG=en_US.UTF-8"
root=/dev/mapper/rhel-root
initrd=/boot/initramfs-3.10.0-862.14.4.el7.x86_64.img
title=Red Hat Enterprise Linux Server (3.10.0-862.14.4.el7.x86_64) 7.5 (Maipo)
index=2
kernel=/boot/vmlinuz-3.10.0-862.el7.x86_64
args="ro crashkernel=auto rd.lvm.lv=rhel/root rd.lvm.lv=rhel/swap rhgb quiet
LANG=en_US.UTF-8"
root=/dev/mapper/rhel-root
initrd=/boot/initramfs-3.10.0-862.el7.x86_64.img
title=Red Hat Enterprise Linux Server (3.10.0-862.el7.x86_64) 7.5 (Maipo)
index=3
kernel=/boot/vmlinuz-0-rescue-40924d06236c45fba188c471ccc6f9ee
args="ro crashkernel=auto rd.lvm.lv=rhel/root rd.lvm.lv=rhel/swap rhgb quiet"
root=/dev/mapper/rhel-root
initrd=/boot/initramfs-0-rescue-40924d06236c45fba188c471ccc6f9ee.img
title=Red Hat Enterprise Linux Server (0-rescue-40924d06236c45fba188c471ccc6f9ee) 7.5 (Maipo)
index=4
non linux entry
""".strip()


def test_grubby_default_index():
    res = GrubbyDefaultIndex(context_wrap(DEFAULT_INDEX_1))
    assert res.default_index == 0

    res = GrubbyDefaultIndex(context_wrap(DEFAULT_INDEX_2))
    assert res.default_index == 1


def test_grubby_default_index_ab():
    with pytest.raises(SkipException) as excinfo:
        GrubbyDefaultIndex(context_wrap(DEFAULT_INDEX_3))
    assert 'Invalid output:' in str(excinfo.value)

    with pytest.raises(SkipException) as excinfo:
        GrubbyDefaultIndex(context_wrap(DEFAULT_INDEX_4))
    assert 'Invalid output:' in str(excinfo.value)


def test_grubby_default_kernel_ab():
    with pytest.raises(SkipException) as excinfo:
        GrubbyDefaultKernel(context_wrap(''))
    assert 'Invalid output:' in str(excinfo.value)


def test_grubby_default_kernel():
    res = GrubbyDefaultKernel(context_wrap(DEFAULT_KERNEL))
    assert res.default_kernel == DEFAULT_KERNEL


def test_grubby_info_all_rhel_6():
    res = GrubbyInfoALL(context_wrap(INFO_ALL_RHEL6))
    assert len(res.kernel_entries) == 2
    assert res.boot == '/dev/vda'
    assert res[0] == res.get('/vmlinuz-2.6.32-754.9.1.el6.x86_64')
    assert res[1]['kernel'] == '/vmlinuz-2.6.32-573.el6.x86_64'


def test_grubby_info_all_rhel_7():
    res = GrubbyInfoALL(context_wrap(INFO_ALL_RHEL7))
    assert len(res.kernel_entries) == 4
    assert res.boot is None
    assert res[0] == res.get('/boot/vmlinuz-3.10.0-957.1.3.el7.x86_64')
    assert res[1]['kernel'] == '/boot/vmlinuz-3.10.0-862.14.4.el7.x86_64'
    assert res[0]['root'] == '/dev/mapper/rhel-root'


def test_grubby_info_all_ab():
    res = GrubbyInfoALL(context_wrap(INFO_ALL_RHEL7))
    with pytest.raises(KeyError) as excinfo:
        res['Just_Test']
    assert 'Just_Test' in str(excinfo)
    with pytest.raises(IndexError) as excinfo:
        res[-1]
    assert 'list index out of range' in str(excinfo)
    with pytest.raises(IndexError) as excinfo:
        res[4]
    assert 'list index out of range' in str(excinfo)


def test_doc_examples():
    env = {
            'grubby_default_index': GrubbyDefaultIndex(context_wrap(DEFAULT_INDEX_1)),
            'grubby_default_kernel': GrubbyDefaultKernel(context_wrap(DEFAULT_KERNEL)),
            'grubby_info_all': GrubbyInfoALL(context_wrap(INFO_ALL_RHEL6)),
          }
    failed, total = doctest.testmod(grubby, globs=env)
    assert failed == 0
