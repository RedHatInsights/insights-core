from insights.combiners.grubby import Grubby
from insights.core.exceptions import ParseException
from insights.parsers.grubby import GrubbyInfoAll, GrubbyDefaultIndex
from insights.tests import context_wrap
import pytest

DEFAULT_INDEX_1 = '0'
DEFAULT_INDEX_2 = '3'

GRUBBY_INFO_ALL = """
index=0
kernel="/boot/vmlinuz-5.14.0-162.6.1.el9_1.x86_64"
args="ro crashkernel=1G-4G:192M,4G-64G:256M,64G-:512M resume=/dev/mapper/rhel-swap rd.lvm.lv=rhel/root rd.lvm.lv=rhel/swap rhgb quiet retbleed=stuff"
root="/dev/mapper/rhel-root"
initrd="/boot/initramfs-5.14.0-162.6.1.el9_1.x86_64.img"
title="Red Hat Enterprise Linux (5.14.0-162.6.1.el9_1.x86_64) 9.1 (Plow)"
id="4d684a4a6166439a867e701ded4f7e10-5.14.0-162.6.1.el9_1.x86_64"
index=1
kernel="/boot/vmlinuz-5.14.0-70.13.1.el9_0.x86_64"
args="ro crashkernel=1G-4G:192M,4G-64G:256M,64G-:512M resume=/dev/mapper/rhel-swap rd.lvm.lv=rhel/root rd.lvm.lv=rhel/swap rhgb quiet retbleed=stuff"
root="/dev/mapper/rhel-root"
initrd="/boot/initramfs-5.14.0-70.13.1.el9_0.x86_64.img"
title="Red Hat Enterprise Linux (5.14.0-70.13.1.el9_0.x86_64) 9.0 (Plow)"
id="4d684a4a6166439a867e701ded4f7e10-5.14.0-70.13.1.el9_0.x86_64"
index=2
kernel="/boot/vmlinuz-0-rescue-4d684a4a6166439a867e701ded4f7e10"
args="ro crashkernel=1G-4G:192M,4G-64G:256M,64G-:512M resume=/dev/mapper/rhel-swap rd.lvm.lv=rhel/root rd.lvm.lv=rhel/swap rhgb quiet retbleed=stuff"
root="/dev/mapper/rhel-root"
initrd="/boot/initramfs-0-rescue-4d684a4a6166439a867e701ded4f7e10.img"
title="Red Hat Enterprise Linux (0-rescue-4d684a4a6166439a867e701ded4f7e10) 9.0 (Plow)"
id="4d684a4a6166439a867e701ded4f7e10-0-rescue"
""".strip()

GRUBBY_INFO_ALL_AB_1 = """
index=0
title="Red Hat Enterprise Linux (5.14.0-162.6.1.el9_1.x86_64) 9.1 (Plow)"
id="4d684a4a6166439a867e701ded4f7e10-5.14.0-162.6.1.el9_1.x86_64"
""".strip()


def test_grubby():
    grubby_info_all = GrubbyInfoAll(context_wrap(GRUBBY_INFO_ALL))
    grubby_default_index = GrubbyDefaultIndex(context_wrap(DEFAULT_INDEX_1))
    result = Grubby(grubby_info_all, grubby_default_index)

    assert result.default_index == 0
    assert result.default_boot_entry == dict(
        index=0,
        kernel="/boot/vmlinuz-5.14.0-162.6.1.el9_1.x86_64",
        args={
            'ro': [True],
            'crashkernel': ['1G-4G:192M,4G-64G:256M,64G-:512M'],
            'resume': ['/dev/mapper/rhel-swap'],
            'rd.lvm.lv': ['rhel/root', 'rhel/swap'],
            'rhgb': [True],
            'quiet': [True],
            'retbleed': ['stuff'],
        },
        root="/dev/mapper/rhel-root",
        initrd="/boot/initramfs-5.14.0-162.6.1.el9_1.x86_64.img",
        title="Red Hat Enterprise Linux (5.14.0-162.6.1.el9_1.x86_64) 9.1 (Plow)",
        id="4d684a4a6166439a867e701ded4f7e10-5.14.0-162.6.1.el9_1.x86_64",
    )
    assert result.default_kernel == "/boot/vmlinuz-5.14.0-162.6.1.el9_1.x86_64"
    assert len(result.boot_entries) == 3


def test_grubby_ab():
    grubby_info_all = GrubbyInfoAll(context_wrap(GRUBBY_INFO_ALL))
    grubby_default_index = GrubbyDefaultIndex(context_wrap(DEFAULT_INDEX_2))
    with pytest.raises(ParseException) as excinfo:
        Grubby(grubby_info_all, grubby_default_index)
    assert "DEFAULT index 3 not exist in parsed boot_entries: [0, 1, 2]" in str(excinfo.value)

    grubby_info_all = GrubbyInfoAll(context_wrap(GRUBBY_INFO_ALL_AB_1))
    grubby_default_index = GrubbyDefaultIndex(context_wrap(DEFAULT_INDEX_1))
    with pytest.raises(ParseException) as excinfo:
        Grubby(grubby_info_all, grubby_default_index)
    assert "DEFAULT kernel-path not exist in default-index: 0" in str(excinfo.value)
