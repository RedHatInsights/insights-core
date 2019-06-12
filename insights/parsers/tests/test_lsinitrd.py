import doctest
from insights.parsers import lsinitrd
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


def test_lsinitrd_filtered():
    d = lsinitrd.LSINITRD(context_wrap(LSINITRD_FILTERED))
    assert len(d.data) == 5
    assert d.search(name__contains='kernel') == [{'type': 'd', 'perms': 'rwxr-xr-x', 'links': 3, 'owner': 'root', 'group': 'root', 'size': 0, 'date': 'Apr 20 15:58', 'name': 'kernel/x86', 'raw_entry': 'drwxr-xr-x   3 root     root            0 Apr 20 15:58 kernel/x86', 'dir': ''}]
    assert d.unparsed_lines == ['Version: dracut-033-535.el7', 'dracut modules:', 'kernel-modules', 'udev-rules']


def test_lsinitrd_all():
    d = lsinitrd.LSINITRD(context_wrap(LSINITRD_ALL))
    assert d.search(name__contains='dev') == [{'type': 'c', 'perms': 'rw-r--r--', 'links': 1, 'owner': 'root', 'group': 'root', 'major': 5, 'minor': 1, 'date': 'Apr 20 15:57', 'name': 'dev/console', 'raw_entry': 'crw-r--r--   1 root     root       5,   1 Apr 20 15:57 dev/console', 'dir': ''}, {'type': 'c', 'perms': 'rw-r--r--', 'links': 1, 'owner': 'root', 'group': 'root', 'major': 1, 'minor': 11, 'date': 'Apr 20 15:57', 'name': 'dev/kmsg', 'raw_entry': 'crw-r--r--   1 root     root       1,  11 Apr 20 15:57 dev/kmsg', 'dir': ''}, {'type': 'c', 'perms': 'rw-r--r--', 'links': 1, 'owner': 'root', 'group': 'root', 'major': 1, 'minor': 3, 'date': 'Apr 20 15:57', 'name': 'dev/null', 'raw_entry': 'crw-r--r--   1 root     root       1,   3 Apr 20 15:57 dev/null', 'dir': ''}]
    assert len(d.data) == 10
    assert len(d.unparsed_lines) == 32
    assert "udev-rules" in d.unparsed_lines


def test_lsinitrd_docs():
    failed_count, tests = doctest.testmod(
        lsinitrd,
        globs={'ls': lsinitrd.LSINITRD(context_wrap(LSINITRD_FILTERED))}
    )
    assert failed_count == 0
