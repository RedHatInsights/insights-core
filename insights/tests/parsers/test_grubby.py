import doctest
import pytest

from insights.core.exceptions import ParseException, SkipComponent
from insights.parsers import grubby
from insights.parsers.grubby import GrubbyDefaultIndex, GrubbyDefaultKernel, GrubbyInfoAll
from insights.tests import context_wrap

DEFAULT_INDEX_1 = '0'
DEFAULT_INDEX_2 = '1'
ABDEFAULT_INDEX_EMPTY = ''
DEFAULT_INDEX_AB = '-2'

DEFAULT_KERNEL = "/boot/vmlinuz-2.6.32-573.el6.x86_64"
DEFAULT_KERNEL_EMPTY = ""
DEFAULT_KERNEL_AB = """
/boot/vmlinuz-2.6.32-573.el6.x86_64"
/boot/vmlinuz-2.6.32-573.el6.x86_64"
""".strip()
DEFAULT_KERNEL_INVALID = 'rpm-sort: Invalid input'
DEFAULT_KERNEL_INVALID_2 = 'rpm-sort: Invalid input '
DEFAULT_KERNEL_INVALID_3 = """
/usr/libexec/grubby/grubby-bls: fork: retry: Resource temporarily unavailable
/usr/libexec/grubby/grubby-bls: fork: retry: Resource temporarily unavailable
""".strip()

DEFAULT_KERNEL_WITH_ERRORS_MSGS_1 = """
/usr/libexec/grubby/grubby-bls: fork: retry: Resource temporarily unavailable
/usr/libexec/grubby/grubby-bls: fork: retry: Resource temporarily unavailable
/usr/libexec/grubby/grubby-bls: fork: retry: Resource temporarily unavailable
/usr/libexec/grubby/grubby-bls: fork: retry: Resource temporarily unavailable
/boot/vmlinuz-4.18.0-147.5.1.el8_1.x86_64
""".strip()
DEFAULT_KERNEL_WITH_ERRORS_MSGS_2 = """
grub2-editenv: error: cannot rename the file /boot/grub2/grubenv.new to /boot/grub2/grubenv: No such file or directory.
/boot/vmlinuz-3.10.0-862.el7.x86_64
""".strip()
DEFAULT_KERNEL_WITH_ERRORS_MSGS_3 = """
grep: /boot/grub2/grubenv: No such file or directory
/boot/cm/images/dell-rhel8.2/boot/vmlinuz-4.18.0-348.23.1.el8_5.x86_64
""".strip()
DEFAULT_KERNEL_WITH_ERRORS_MSGS_4 = """
/etc/os-release: line 5: VERSION_ID-Peter=8.7: command not found
/etc/os-release: line 6: PLATFORM_ID-Peter=platform:el8: command not found
/boot/vmlinuz-4.18.0-425.10.1.el8_7.x86_64
""".strip()

GRUBBY_INFO_ALL_1 = """
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
""".strip()

GRUBBY_INFO_ALL_2 = """
index=0
kernel=/boot/vmlinuz-3.10.0-862.el7.x86_64
args="ro console=tty0 console=ttyS0,115200n8 no_timer_check net.ifnames=0 crashkernel=auto LANG=en_US.UTF-8"
root=UUID=6bea2b7b-e6cc-4dba-ac79-be6530d348f5
initrd=/boot/initramfs-3.10.0-862.el7.x86_64.img
title=Red Hat Enterprise Linux Server (3.10.0-862.el7.x86_64) 7.5 (Maipo)
index=1
kernel=/boot/vmlinuz-0-rescue-1b461b2e96854984bc0777c4b4b518a9
args="ro console=tty0 console=ttyS0,115200n8 no_timer_check net.ifnames=0 crashkernel=auto"
root=UUID=6bea2b7b-e6cc-4dba-ac79-be6530d348f5
initrd=/boot/initramfs-0-rescue-1b461b2e96854984bc0777c4b4b518a9.img
title=Red Hat Enterprise Linux Server (0-rescue-1b461b2e96854984bc0777c4b4b518a9) 7.5 (Maipo)
index=2
non linux entry
""".strip()

GRUBBY_INFO_ALL_INVALID_1 = """
some head lines
index=0
non linux entry

some tail lines
""".strip()
GRUBBY_INFO_ALL_INVALID_2 = """
some head lines
kernel=/boot/vmlinuz-3.10.0-862.el7.x86_64
args="ro console=tty0 console=ttyS0,115200n8 no_timer_check net.ifnames=0 crashkernel=auto LANG=en_US.UTF-8"
root=UUID=6bea2b7b-e6cc-4dba-ac79-be6530d348f5
initrd=/boot/initramfs-3.10.0-862.el7.x86_64.img
title=Red Hat Enterprise Linux Server (3.10.0-862.el7.x86_64) 7.5 (Maipo)
some tail lines
""".strip()
GRUBBY_INFO_ALL_INVALID_2 = """
some head lines
index=some-index
kernel=/boot/vmlinuz-3.10.0-862.el7.x86_64
args="ro console=tty0 console=ttyS0,115200n8 no_timer_check net.ifnames=0 crashkernel=auto LANG=en_US.UTF-8"
root=UUID=6bea2b7b-e6cc-4dba-ac79-be6530d348f5
initrd=/boot/initramfs-3.10.0-862.el7.x86_64.img
title=Red Hat Enterprise Linux Server (3.10.0-862.el7.x86_64) 7.5 (Maipo)
some tail lines
""".strip()


def test_grubby_default_index():
    res = GrubbyDefaultIndex(context_wrap(DEFAULT_INDEX_1))
    assert res.default_index == 0

    res = GrubbyDefaultIndex(context_wrap(DEFAULT_INDEX_2))
    assert res.default_index == 1


def test_grubby_default_index_ab():
    with pytest.raises(SkipComponent) as excinfo:
        GrubbyDefaultIndex(context_wrap(ABDEFAULT_INDEX_EMPTY))
    assert 'Empty output' in str(excinfo.value)

    with pytest.raises(ParseException) as excinfo:
        GrubbyDefaultIndex(context_wrap(DEFAULT_INDEX_AB))
    assert 'Invalid output:' in str(excinfo.value)


def test_grubby_default_kernel():
    res = GrubbyDefaultKernel(context_wrap(DEFAULT_KERNEL))
    assert res.default_kernel == DEFAULT_KERNEL

    content_with_error_msgs = [
        DEFAULT_KERNEL_WITH_ERRORS_MSGS_1,
        DEFAULT_KERNEL_WITH_ERRORS_MSGS_2,
        DEFAULT_KERNEL_WITH_ERRORS_MSGS_3,
        DEFAULT_KERNEL_WITH_ERRORS_MSGS_4,
    ]
    for content in content_with_error_msgs:
        this_res = GrubbyDefaultKernel(context_wrap(content))
        assert this_res.default_kernel == content.split()[-1].strip()


def test_grubby_default_kernel_ab():
    with pytest.raises(SkipComponent) as excinfo:
        GrubbyDefaultKernel(context_wrap(DEFAULT_KERNEL_EMPTY))
    assert 'Empty output' in str(excinfo.value)

    with pytest.raises(ParseException) as excinfo:
        GrubbyDefaultKernel(context_wrap(DEFAULT_KERNEL_AB))
    assert 'Invalid output:' in str(excinfo.value)

    with pytest.raises(ParseException) as excinfo:
        GrubbyDefaultKernel(context_wrap(DEFAULT_KERNEL_INVALID))
    assert 'Invalid output:' in str(excinfo.value)

    with pytest.raises(ParseException) as excinfo:
        GrubbyDefaultKernel(context_wrap(DEFAULT_KERNEL_INVALID_2))
    assert 'Invalid output:' in str(excinfo.value)

    with pytest.raises(ParseException) as excinfo:
        GrubbyDefaultKernel(context_wrap(DEFAULT_KERNEL_INVALID_3))
    assert 'Invalid output:' in str(excinfo.value)


def test_grubby_info_all():
    res = GrubbyInfoAll(context_wrap(GRUBBY_INFO_ALL_1))

    assert res.unparsed_lines == []
    assert len(res.boot_entries) == 2
    assert res.boot_entries[0] == dict(
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

    assert "kernel" in res.boot_entries[1]
    assert res.boot_entries[1]["kernel"] == "/boot/vmlinuz-5.14.0-70.13.1.el9_0.x86_64"
    assert res.boot_entries[1].get("root") == "/dev/mapper/rhel-root"

    entry_args = res.boot_entries[1].get("args")
    assert entry_args.get("ro") == [True]
    assert entry_args.get("rd.lvm.lv") == ['rhel/root', 'rhel/swap']

    res = GrubbyInfoAll(context_wrap(GRUBBY_INFO_ALL_2))
    assert len(res.boot_entries) == 2
    assert res.unparsed_lines == ["non linux entry"]


def test_grubby_info_all_ab():
    with pytest.raises(SkipComponent) as excinfo:
        GrubbyInfoAll(context_wrap(""))
    assert 'Empty output' in str(excinfo.value)

    with pytest.raises(SkipComponent) as excinfo:
        GrubbyInfoAll(context_wrap(GRUBBY_INFO_ALL_INVALID_1))
    assert 'No valid entry parsed' in str(excinfo.value)

    with pytest.raises(ParseException) as excinfo:
        GrubbyInfoAll(context_wrap(GRUBBY_INFO_ALL_INVALID_2))
    assert 'Invalid index value:' in str(excinfo.value)


def test_doc_examples():
    env = {
        'grubby_default_index': GrubbyDefaultIndex(context_wrap(DEFAULT_INDEX_1)),
        'grubby_default_kernel': GrubbyDefaultKernel(context_wrap(DEFAULT_KERNEL)),
        'grubby_info_all': GrubbyInfoAll(context_wrap(GRUBBY_INFO_ALL_1)),
    }
    failed, total = doctest.testmod(grubby, globs=env)
    assert failed == 0
