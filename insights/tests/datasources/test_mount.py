import pytest

from insights.core.exceptions import SkipComponent
from insights.specs.datasources.mount import xfs_mounts
from insights.parsers.mount import ProcMounts
from insights.tests import context_wrap

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


def test_xfs_mounts():
    pmnt = ProcMounts(context_wrap(PROC_MOUNT_XFS))
    broker = {ProcMounts: pmnt}
    result = xfs_mounts(broker)
    assert result == ['/', '/boot']

    pmnt = ProcMounts(context_wrap(PROC_MOUNT_NO_XFS))
    broker = {ProcMounts: pmnt}
    with pytest.raises(SkipComponent):
        xfs_mounts(broker)
