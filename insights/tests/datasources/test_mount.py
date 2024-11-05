import pytest

from insights.core.exceptions import SkipComponent
from insights.specs.datasources.mount import xfs_mounts, dumpdev_list, fstab_mounted
from insights.parsers.mount import ProcMounts
from insights.tests import context_wrap
from insights.parsers.fstab import FSTab

PROC_MOUNT_XFS = '''
/dev/mapper/rhel_insights--release-root / xfs rw,seclabel,relatime,attr2,inode64,logbufs=8,logbsize=32k,noquota 0 0
/dev/vda1 /boot xfs rw,seclabel,relatime,attr2,inode64,logbufs=8,logbsize=32k,noquota 0 0
'''.strip()

PROC_MOUNT_NO_XFS = '''
/dev/mapper/rhel_insights--release-root / ext4 rw,seclabel,relatime,attr2,inode64,logbufs=8,logbsize=32k,noquota 0 0
fusectl /sys/fs/fuse/connections fusectl rw,relatime 0 0
tmpfs /run/user/1000 tmpfs rw,seclabel,nosuid,nodev,relatime,size=786664k,mode=700,uid=1000,gid=10 0 0
binfmt_misc /proc/sys/fs/binfmt_misc binfmt_misc rw,relatime 0 0
'''.strip()

MOUNT = """
/dev/mapper/root / ext4 rw,relatime,barrier=1,data=ordered 0 0
/dev/mapper/httpd1 /httpd1 nfs4 rw,relatime,vers=4,barrier=1,data=ordered 0 0
/dev/mapper/httpd2 /httpd2 nfs4 rw,relatime,vers=4,barrier=1,data=ordered 0 0
""".strip()


MOUNT_NO_EXT = """
/dev/mapper/root / xfs rw,relatime,barrier=1,data=ordered 0 0
/dev/mapper/httpd1 /httpd1 nfs4 rw,relatime,vers=4,barrier=1,data=ordered 0 0
/dev/mapper/httpd2 /httpd2 nfs4 rw,relatime,vers=4,barrier=1,data=ordered 0 0
""".strip()

FSTAB = """
#
# /etc/fstab
# Created by anaconda on Fri May  6 19:51:54 2016
#
/dev/mapper/rhel_hadoop--test--1-root /                       xfs     defaults        0 0
UUID=2c839365-37c7-4bd5-ac47-040fba761735 /boot               xfs     defaults        0 0
/dev/mapper/rhel_hadoop--test--1-home /home                   xfs     defaults        0 0
/dev/mapper/rhel_hadoop--test--1-swap swap                    swap    defaults        0 0
""".strip()

FSTAB_EMPTY = ""


def test_xfs_mounts():
    pmnt = ProcMounts(context_wrap(PROC_MOUNT_XFS))
    broker = {ProcMounts: pmnt}
    result = xfs_mounts(broker)
    assert result == ['/', '/boot']

    pmnt = ProcMounts(context_wrap(PROC_MOUNT_NO_XFS))
    broker = {ProcMounts: pmnt}
    with pytest.raises(SkipComponent):
        xfs_mounts(broker)


def test_dumpdev_list():
    broker = {ProcMounts: ProcMounts(context_wrap(MOUNT))}
    result = dumpdev_list(broker)
    assert len(result) == 1
    assert '/dev/mapper/root' in result


def test_dumpdev_list_no_ext_filesystem():
    broker = {ProcMounts: ProcMounts(context_wrap(MOUNT_NO_EXT))}
    with pytest.raises(SkipComponent):
        dumpdev_list(broker)


def test_fstab_mount_points():
    fstab_content = FSTab(context_wrap(FSTAB))

    broker = {
        FSTab: fstab_content
    }
    result = fstab_mounted(broker)
    assert result is not None
    assert result == '/ /boot /home swap'


def test_fstab_mount_points_bad():
    fstab_content = FSTab(context_wrap(FSTAB_EMPTY))

    broker = {
        FSTab: fstab_content
    }
    with pytest.raises(SkipComponent):
        fstab_mounted(broker)
