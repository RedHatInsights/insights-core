from insights.combiners.grubby import Grubby, IsUEFIBoot
from insights.core.exceptions import ParseException
from insights.parsers.grubby import GrubbyInfoAll, GrubbyDefaultIndex
from insights.parsers.grubenv import GrubEnv
from insights.parsers.ls import LSlanFiltered
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

GRUBBY_INFO_ALL_AB_2 = """
index=0
kernel="/boot/vmlinuz-5.14.0-162.6.1.el9_1.x86_64"
args="ro crashkernel=1G-4G:192M,4G-64G:256M,64G-:512M resume=/dev/mapper/rhel-swap rd.lvm.lv=rhel/root rd.lvm.lv=rhel/swap rhgb intel_iommu=on"
root="/dev/mapper/rhel-root"
initrd="/boot/initramfs-5.14.0-162.6.1.el9_1.x86_64.img"
title="Red Hat Enterprise Linux (5.14.0-162.6.1.el9_1.x86_64) 9.1 (Plow)"
id="4d684a4a6166439a867e701ded4f7e10-5.14.0-162.6.1.el9_1.x86_64"
index=1
kernel=""
args="ro crashkernel=1G-4G:192M,4G-64G:256M,64G-:512M resume=/dev/mapper/rhel-swap rd.lvm.lv=rhel/root rd.lvm.lv=rhel/swap rhgb quiet retbleed=stuff"
root="/dev/mapper/rhel-root"
initrd=""
title="Red Hat Enterprise Linux (5.14.0-70.13.1.el9_0.x86_64) 9.0 (Plow)"
id="4d684a4a6166439a867e701ded4f7e10-5.14.0-70.13.1.el9_0.x86_64"
""".strip()

GRUBBY_INFO_ALL_WITH_PARAMS = """
index=0
kernel="/boot/vmlinuz-5.14.0-570.30.1.el9_6.x86_64"
args="ro audit=1 crashkernel=1G-4G:192M,4G-64G:256M,64G-:512M rd.lvm.lv=rhel/root rhgb quiet selinux=0 audit_backlog_limit=8192 $tuned_params"
root="/dev/mapper/rhel-root"
initrd="/boot/initramfs-5.14.0-570.30.1.el9_6.x86_64.img $tuned_initrd"
title="Red Hat Enterprise Linux (5.14.0-570.30.1.el9_6.x86_64) 9.6 (Plow)"
id="1234567890abcdefffffffffffffffff-5.14.0-570.30.1.el9_6.x86_64"
index=1
kernel="/boot/vmlinuz-0-rescue-1234567890abcdefffffffffffffffff"
args="ro audit=1 $kernelopts $tuned_params"
root="/dev/mapper/rhel-root"
initrd="/boot/initramfs-0-rescue-1234567890abcdefffffffffffffffff.img"
title="Red Hat Enterprise Linux (0-rescue-1234567890abcdefffffffffffffffff) 9.6 (Plow)"
id="1234567890abcdefffffffffffffffff-0-rescue"
""".strip()

GRUBENV_WITH_PARAMS = """
saved_entry=1234567890abcdefffffffffffffffff-5.14.0-570.30.1.el9_6.x86_64
menu_auto_hide=1
boot_success=1
boot_indeterminate=0
kernelopts=console=tty0 console=ttyS0,115200 noapic
tuned_params=transparent_hugepages=never
tuned_initrd=foo=bar
""".strip()

GRUBENV_WITHOUT_PARAMS = """
saved_entry=1234567890abcdefffffffffffffffff-5.14.0-570.30.1.el9_6.x86_64
menu_auto_hide=1
boot_success=1
boot_indeterminate=0
""".strip()

LS_SYS_FIRMWARE_NOT_EFI = """
/sys/firmware:
total 0
drwxr-xr-x  6 0 0 0 Aug 19 14:57 dmi
""".strip()

LS_SYS_FIRMWARE_IS_EFI = """
/sys/firmware:
total 0
drwxr-xr-x  6 0 0 0 Aug 19 14:57 efi
""".strip()


def test_grubby():
    grubby_info_all = GrubbyInfoAll(context_wrap(GRUBBY_INFO_ALL))
    grubby_default_index = GrubbyDefaultIndex(context_wrap(DEFAULT_INDEX_1))
    ls_lan = LSlanFiltered(context_wrap(LS_SYS_FIRMWARE_NOT_EFI))
    is_uefi_boot = IsUEFIBoot(ls_lan, None)
    result = Grubby(grubby_info_all, grubby_default_index, None, is_uefi_boot)

    assert result.default_index == 0
    default_boot_entry_data = dict(
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
            'root': ['/dev/mapper/rhel-root'],
            '/boot/vmlinuz-5.14.0-162.6.1.el9_1.x86_64': [True],
        },
        cmdline="/boot/vmlinuz-5.14.0-162.6.1.el9_1.x86_64 root=/dev/mapper/rhel-root ro "
        "crashkernel=1G-4G:192M,4G-64G:256M,64G-:512M "
        "resume=/dev/mapper/rhel-swap rd.lvm.lv=rhel/root rd.lvm.lv=rhel/swap "
        "rhgb quiet retbleed=stuff",
        root="/dev/mapper/rhel-root",
        initrd="/boot/initramfs-5.14.0-162.6.1.el9_1.x86_64.img",
        title="Red Hat Enterprise Linux (5.14.0-162.6.1.el9_1.x86_64) 9.1 (Plow)",
        name="Red Hat Enterprise Linux (5.14.0-162.6.1.el9_1.x86_64) 9.1 (Plow)",
        id="4d684a4a6166439a867e701ded4f7e10-5.14.0-162.6.1.el9_1.x86_64",
    )
    for k, v in result.default_boot_entry.items():
        assert v == default_boot_entry_data[k]
    assert result.default_kernel == "/boot/vmlinuz-5.14.0-162.6.1.el9_1.x86_64"
    assert len(result.boot_entries) == 3
    assert len(result.kernel_initrds['grub_kernels']) == 3
    assert result.is_kdump_iommu_enabled is False
    assert not result.is_efi


def test_grubby_ab():
    grubby_info_all = GrubbyInfoAll(context_wrap(GRUBBY_INFO_ALL))
    grubby_default_index = GrubbyDefaultIndex(context_wrap(DEFAULT_INDEX_2))
    with pytest.raises(ParseException) as excinfo:
        Grubby(grubby_info_all, grubby_default_index, None, None)
    assert "DEFAULT index 3 not exist in parsed boot_entries: [0, 1, 2]" in str(excinfo.value)

    grubby_info_all = GrubbyInfoAll(context_wrap(GRUBBY_INFO_ALL_AB_1))
    grubby_default_index = GrubbyDefaultIndex(context_wrap(DEFAULT_INDEX_1))
    with pytest.raises(ParseException) as excinfo:
        Grubby(grubby_info_all, grubby_default_index, None, None)
    assert "DEFAULT kernel-path not exist in default-index: 0" in str(excinfo.value)

    grubby_info_all = GrubbyInfoAll(context_wrap(GRUBBY_INFO_ALL_AB_2))
    grubby_default_index = GrubbyDefaultIndex(context_wrap(DEFAULT_INDEX_1))
    result = Grubby(grubby_info_all, grubby_default_index, None, None)
    assert len(result.kernel_initrds['grub_kernels']) == 1
    assert len(result.kernel_initrds['grub_initrds']) == 1  # cov test
    assert result.is_kdump_iommu_enabled is True
    assert result.is_kdump_iommu_enabled is True  # cov test


def test_grubby_extend_with_grubenv():
    grubby_info_all = GrubbyInfoAll(context_wrap(GRUBBY_INFO_ALL_WITH_PARAMS))
    grubby_default_index = GrubbyDefaultIndex(context_wrap(DEFAULT_INDEX_1))
    grubenv = GrubEnv(context_wrap(GRUBENV_WITH_PARAMS))
    ls_lan = LSlanFiltered(context_wrap(LS_SYS_FIRMWARE_IS_EFI))
    is_uefi_boot = IsUEFIBoot(ls_lan, None)

    result = Grubby(grubby_info_all, grubby_default_index, grubenv, is_uefi_boot)
    assert result.default_index == 0
    default_boot_entry_data = dict(
        index=0,
        kernel="/boot/vmlinuz-5.14.0-570.30.1.el9_6.x86_64",
        args={
            'audit': ['1'],
            'audit_backlog_limit': ['8192'],
            'crashkernel': ['1G-4G:192M,4G-64G:256M,64G-:512M'],
            'quiet': [True],
            'rd.lvm.lv': ['rhel/root'],
            'rhgb': [True],
            'ro': [True],
            'root': ['/dev/mapper/rhel-root'],
            'selinux': ['0'],
            'transparent_hugepages': ['never'],
            '/boot/vmlinuz-5.14.0-570.30.1.el9_6.x86_64': [True],
        },
        cmdline='/boot/vmlinuz-5.14.0-570.30.1.el9_6.x86_64 root=/dev/mapper/rhel-root ro audit=1 '
        'crashkernel=1G-4G:192M,4G-64G:256M,64G-:512M rd.lvm.lv=rhel/root '
        'rhgb quiet selinux=0 audit_backlog_limit=8192 '
        'transparent_hugepages=never',
        root="/dev/mapper/rhel-root",
        initrd="/boot/initramfs-5.14.0-570.30.1.el9_6.x86_64.img foo=bar",
        title="Red Hat Enterprise Linux (5.14.0-570.30.1.el9_6.x86_64) 9.6 (Plow)",
        name="Red Hat Enterprise Linux (5.14.0-570.30.1.el9_6.x86_64) 9.6 (Plow)",
        id='1234567890abcdefffffffffffffffff-5.14.0-570.30.1.el9_6.x86_64',
    )
    for k, v in result.default_boot_entry.items():
        assert v == default_boot_entry_data[k]
    assert result.default_kernel == "/boot/vmlinuz-5.14.0-570.30.1.el9_6.x86_64"
    assert result.is_efi
    assert len(result.boot_entries) == 2
    assert (
        result.boot_entries[1]['initrd']
        == "/boot/initramfs-0-rescue-1234567890abcdefffffffffffffffff.img"
    )
    assert result.boot_entries[1]['args'] == {
        'root': ['/dev/mapper/rhel-root'],
        'ro': [True],
        'audit': ['1'],
        'console': ['tty0', 'ttyS0,115200'],
        'noapic': [True],
        'transparent_hugepages': ['never'],
        '/boot/vmlinuz-0-rescue-1234567890abcdefffffffffffffffff': [True],
    }
    assert result.boot_entries[1]['cmdline'] == (
        "/boot/vmlinuz-0-rescue-1234567890abcdefffffffffffffffff "
        "root=/dev/mapper/rhel-root ro audit=1 console=tty0 "
        "console=ttyS0,115200 noapic transparent_hugepages=never"
    )

    # without grubenv
    result = Grubby(grubby_info_all, grubby_default_index, None, None)
    assert result.default_index == 0
    assert (
        result.default_boot_entry["initrd"]
        == "/boot/initramfs-5.14.0-570.30.1.el9_6.x86_64.img $tuned_initrd"
    )
    assert result.default_boot_entry["args"]["$tuned_params"] == [True]
    assert result.default_boot_entry["cmdline"].endswith("audit_backlog_limit=8192 $tuned_params")
    assert len(result.boot_entries) == 2
    assert not result.is_efi

    # with grubenv w/o params setting
    grubenv_wo_params = GrubEnv(context_wrap(GRUBENV_WITHOUT_PARAMS))
    result = Grubby(grubby_info_all, grubby_default_index, grubenv_wo_params, None)
    assert result.default_index == 0
    assert result.default_boot_entry["initrd"] == "/boot/initramfs-5.14.0-570.30.1.el9_6.x86_64.img"
    assert "$tuned_params" not in result.default_boot_entry["args"]
    assert "$tuned_params" not in result.default_boot_entry["cmdline"]
    assert result.default_boot_entry["cmdline"].endswith(" audit_backlog_limit=8192")
    assert len(result.boot_entries) == 2
    assert not result.is_efi
