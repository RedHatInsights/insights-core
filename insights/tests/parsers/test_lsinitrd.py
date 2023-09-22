import doctest
import pytest
from insights.parsers import lsinitrd
from insights.parsers.lsinitrd import LsinitrdKdumpImage
from insights.tests import context_wrap


LSINITRD_ALL = """
Image: /boot/initramfs-3.10.0-862.el7.x86_64.img: 24M
========================================================================
Early CPIO image
========================================================================
drwxr-xr-x   3 root     root            0 Apr 20 15:58 .
-rw-r--r--   1 root     root            2 Apr 20 15:58 early_cpio
drwxr-xr-x   3 root     root            0 Apr 20 15:58 kernel
drwxr-xr-x   3 root     root            0 Apr 20 15:58 kernel/x86
drwxr-xr-x   2 root     root            0 Apr 20 15:58 kernel/x86/microcode
-rw-r--r--   1 root     root        12684 Apr 20 15:58 kernel/x86/microcode/AuthenticAMD.bin
========================================================================
Version: dracut-033-535.el7

Arguments: -f

dracut modules:
bash
nss-softokn
i18n
network
ifcfg
drm
plymouth
dm
kernel-modules
lvm
resume
rootfs-block
terminfo
udev-rules
biosdevname
systemd
usrmount
base
fs-lib
shutdown
========================================================================
drwxr-xr-x  12 root     root            0 Apr 20 15:58 .
crw-r--r--   1 root     root       5,   1 Apr 20 15:57 dev/console
crw-r--r--   1 root     root       1,  11 Apr 20 15:57 dev/kmsg
crw-r--r--   1 root     root       1,   3 Apr 20 15:57 dev/null
lrwxrwxrwx   1 root     root            7 Apr 20 15:57 bin -> usr/bin
========================================================================
""".strip()

LSINITRD_FILTERED = """
drwxr-xr-x   3 root     root            0 Apr 20 15:58 kernel/x86
Version: dracut-033-535.el7
dracut modules:
kernel-modules
udev-rules
drwxr-xr-x  12 root     root            0 Apr 20 15:58 .
crw-r--r--   1 root     root       5,   1 Apr 20 15:57 dev/console
crw-r--r--   1 root     root       1,  11 Apr 20 15:57 dev/kmsg
crw-r--r--   1 root     root       1,   3 Apr 20 15:57 dev/null
""".strip()

LSINITRD_EMPTY = ""

# This test case
LSINITRD_BROKEN = """
drwxr-xr-x   3 root     root            0 Apr 20 15:58 kernel/x86
Version: dracut-033-535.el7
dracut modules:
kernel-modules
udev-rules
drwxr-xr-x  12 root     root            0 Apr 20 15:58 .
crw-r--r--   1
crw-r-
c
""".strip()

LSINITRD_KDUMP_IMAGE_VALID = """
Image: initramfs-4.18.0-240.el8.x86_64kdump.img: 19M
========================================================================
Version: dracut-049-95.git20200804.el8

Arguments: --quiet --hostonly --hostonly-cmdline --hostonly-i18n --hostonly-mode 'strict' -o 'plymouth dash resume ifcfg earlykdump' --mount '/dev/mapper/rhel-root /sysroot xfs rw,relatime,seclabel,attr2,inode64,logbufs=8,logbsize=32k,noquota,nofail,x-systemd.before=initrd-fs.target' --no-hostonly-default-device -f

dracut modules:
bash
systemd
systemd-initrd
nss-softokn
rngd
i18n
drm
prefixdevname
dm
kernel-modules
kernel-modules-extra
lvm
qemu
fstab-sys
rootfs-block
terminfo
udev-rules
biosdevname
dracut-systemd
usrmount
base
fs-lib
kdumpbase
memstrack
microcode_ctl-fw_dir_override
shutdown
squash
========================================================================
crw-r--r--   1 root     root       5,   1 Aug  4  2020 dev/console
drwxr-xr-x   2 root     root            0 Aug  4  2020 run
-rw-r--r--   1 root     root          306 Aug  4  2020 usr/lib/dracut/build-parameter.txt
-rw-r--r--   1 root     root           30 Aug  4  2020 usr/lib/dracut/dracut-049-95.git20200804.el8
drwxr-xr-x   2 root     root            0 Aug  4  2020 usr/lib/dracut/hooks
-rw-r--r--   1 root     root          653 Aug  4  2020 usr/lib/dracut/hostonly-files
-rw-r--r--   1 root     root          780 Aug  4  2020 usr/lib/dracut/loaded-kernel-modules.txt
-rw-r--r--   1 root     root          273 Aug  4  2020 usr/lib/dracut/modules.txt
-rw-r--r--   1 root     root            0 Aug  4  2020 usr/lib/dracut/need-initqueue
-rw-r--r--   1 root     root            0 Aug  4  2020 usr/lib/dracut/no-switch-root
-rw-r--r--   1 root     root          221 Aug  4  2020 usr/lib/initrd-release
drwxr-xr-x   3 root     root            0 Aug  4  2020 usr/lib/modules
drwxr-xr-x   3 root     root            0 Aug  4  2020 usr/lib/modules/4.18.0-240.el8.x86_64
drwxr-xr-x   4 root     root            0 Aug  4  2020 usr/lib/modules/4.18.0-240.el8.x86_64/kernel
drwxr-xr-x   3 root     root            0 Aug  4  2020 usr/lib/modules/4.18.0-240.el8.x86_64/kernel/drivers
drwxr-xr-x   2 root     root            0 Aug  4  2020 usr/lib/modules/4.18.0-240.el8.x86_64/kernel/drivers/block
-rw-r--r--   1 root     root        16868 Aug  4  2020 usr/lib/modules/4.18.0-240.el8.x86_64/kernel/drivers/block/loop.ko.xz
drwxr-xr-x   4 root     root            0 Aug  4  2020 usr/lib/modules/4.18.0-240.el8.x86_64/kernel/fs
drwxr-xr-x   2 root     root            0 Aug  4  2020 usr/lib/modules/4.18.0-240.el8.x86_64/kernel/fs/overlayfs
-rw-r--r--   1 root     root        53736 Aug  4  2020 usr/lib/modules/4.18.0-240.el8.x86_64/kernel/fs/overlayfs/overlay.ko.xz
drwxr-xr-x   2 root     root            0 Aug  4  2020 usr/lib/modules/4.18.0-240.el8.x86_64/kernel/fs/squashfs
-rw-r--r--   1 root     root        24412 Aug  4  2020 usr/lib/modules/4.18.0-240.el8.x86_64/kernel/fs/squashfs/squashfs.ko.xz
-rw-r--r--   1 root     root        21985 Aug  4  2020 usr/lib/modules/4.18.0-240.el8.x86_64/modules.alias
-rw-r--r--   1 root     root        20181 Aug  4  2020 usr/lib/modules/4.18.0-240.el8.x86_64/modules.alias.bin
-rw-r--r--   1 root     root         7528 Aug  4  2020 usr/lib/modules/4.18.0-240.el8.x86_64/modules.builtin
-rw-r--r--   1 root     root         9683 Aug  4  2020 usr/lib/modules/4.18.0-240.el8.x86_64/modules.builtin.bin
-rw-r--r--   1 root     root         3632 Aug  4  2020 usr/lib/modules/4.18.0-240.el8.x86_64/modules.dep
-rw-r--r--   1 root     root         5304 Aug  4  2020 usr/lib/modules/4.18.0-240.el8.x86_64/modules.dep.bin
-rw-r--r--   1 root     root          126 Aug  4  2020 usr/lib/modules/4.18.0-240.el8.x86_64/modules.devname
-rw-r--r--   1 root     root       101785 Aug  4  2020 usr/lib/modules/4.18.0-240.el8.x86_64/modules.order
-rw-r--r--   1 root     root           85 Aug  4  2020 usr/lib/modules/4.18.0-240.el8.x86_64/modules.softdep
-rw-r--r--   1 root     root        50083 Aug  4  2020 usr/lib/modules/4.18.0-240.el8.x86_64/modules.symbols
-rw-r--r--   1 root     root        56186 Aug  4  2020 usr/lib/modules/4.18.0-240.el8.x86_64/modules.symbols.bin
drwxr-xr-x   2 root     root            0 Aug  4  2020 usr/lib64
drwxr-xr-x   2 root     root            0 Aug  4  2020 var/tmp
========================================================================
""".strip()

LSINITRD_KDUMP_IMAGE_VALID_EXAMPLE = """
Image: initramfs-4.18.0-240.el8.x86_64kdump.img: 19M
========================================================================
Version: dracut-049-95.git20200804.el8

Arguments: --quiet --hostonly --hostonly-cmdline --hostonly-i18n --hostonly-mode 'strict' -o 'plymouth dash resume ifcfg earlykdump' --mount '/dev/mapper/rhel-root /sysroot xfs rw,relatime,seclabel,attr2,inode64,logbufs=8,logbsize=32k,noquota,nofail,x-systemd.before=initrd-fs.target' --no-hostonly-default-device -f

dracut modules:
bash
systemd
systemd-initrd
i18n
========================================================================
crw-r--r--   1 root     root       5,   1 Aug  4  2020 dev/console
crw-r--r--   1 root     root       1,  11 Aug  4  2020 dev/kmsg
crw-r--r--   1 root     root       1,   3 Aug  4  2020 dev/null
crw-r--r--   1 root     root       1,   8 Aug  4  2020 dev/random
crw-r--r--   1 root     root       1,   9 Aug  4  2020 dev/urandom
drwxr-xr-x  14 root     root            0 Aug  4  2020 .
lrwxrwxrwx   1 root     root            7 Aug  4  2020 bin -> usr/bin
drwxr-xr-x   2 root     root            0 Aug  4  2020 dev
========================================================================
""".strip()

LSINITRD_LVM_CONF = """
# volume_list = [ "vg1", "vg2/lvol1", "@tag1", "@*" ]
volume_list = [ "vg2", "vg3/lvol3", "@tag2", "@*" ]
""".strip()


def test_lsinitrd_empty():
    d = lsinitrd.Lsinitrd(context_wrap(LSINITRD_EMPTY))
    assert len(d.data) == 0
    assert d.search(name__contains='kernel') == []
    assert d.unparsed_lines == []


def test_lsinitrd_filtered():
    d = lsinitrd.Lsinitrd(context_wrap(LSINITRD_FILTERED))
    assert len(d.data) == 5
    assert d.search(name__contains='kernel') == [{'type': 'd', 'perms': 'rwxr-xr-x', 'links': 3, 'owner': 'root', 'group': 'root', 'size': 0, 'date': 'Apr 20 15:58', 'name': 'kernel/x86', 'raw_entry': 'drwxr-xr-x   3 root     root            0 Apr 20 15:58 kernel/x86', 'dir': ''}]
    assert d.unparsed_lines == ['Version: dracut-033-535.el7', 'dracut modules:', 'kernel-modules', 'udev-rules']


def test_lsinitrd_all():
    d = lsinitrd.Lsinitrd(context_wrap(LSINITRD_ALL))
    lsdev = d.search(name__contains='dev')
    assert len(lsdev) == 3
    dev_console = {
        'type': 'c', 'perms': 'rw-r--r--', 'links': 1, 'owner': 'root', 'group': 'root',
        'major': 5, 'minor': 1, 'date': 'Apr 20 15:57', 'name': 'dev/console', 'dir': '',
        'raw_entry': 'crw-r--r--   1 root     root       5,   1 Apr 20 15:57 dev/console'
    }
    assert dev_console in lsdev
    assert 'dev/kmsg' in [l['name'] for l in lsdev]
    assert 'dev/null' in [l['name'] for l in lsdev]
    assert len(d.data) == 10
    assert len(d.unparsed_lines) == 32
    assert "udev-rules" in d.unparsed_lines


def test_lsinitrd_broken():
    """
    For this testcase, ls_parser.parse() will throw an IndexError.
    Assert with this specific error here.
    """
    with pytest.raises(Exception) as err:
        lsinitrd.Lsinitrd(context_wrap(LSINITRD_BROKEN))
    assert "list index out of range" in str(err)


def test_lsinitrd_kdump_image_valid():
    parser_result = LsinitrdKdumpImage(context_wrap(LSINITRD_KDUMP_IMAGE_VALID))
    assert parser_result is not None
    result_list = parser_result.search(name__contains='devname')
    assert len(result_list) == 1
    assert result_list[0].get('raw_entry') == '-rw-r--r--   1 root     root          126 Aug  4  2020 usr/lib/modules/4.18.0-240.el8.x86_64/modules.devname'


def test_lsinitrd_lvm_conf():
    lvm_conf = lsinitrd.LsinitrdLvmConf(context_wrap(LSINITRD_LVM_CONF))
    assert lvm_conf["volume_list"] == ["vg2", "vg3/lvol3", "@tag2", "@*"]


def test_lsinitrd_docs():
    failed_count, tests = doctest.testmod(
        globs={'ls': lsinitrd.Lsinitrd(context_wrap(LSINITRD_FILTERED)),
               'lsinitrd_kdump_image': LsinitrdKdumpImage(context_wrap(LSINITRD_KDUMP_IMAGE_VALID_EXAMPLE)),
               'lsinitrd_lvm_conf': lsinitrd.LsinitrdLvmConf(context_wrap(LSINITRD_LVM_CONF))}
    )
    assert failed_count == 0
