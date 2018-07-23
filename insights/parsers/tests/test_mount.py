""""
test mount
==========
"""
from insights.parsers import ParseException
from insights.parsers.mount import Mount
from insights.tests import context_wrap

import pytest

MOUNT_DATA = """
tmpfs on /tmp type tmpfs (rw,seclabel)
hugetlbfs on /dev/hugepages type hugetlbfs (rw,relatime,seclabel)
nfsd on /proc/fs/nfsd type nfsd (rw,relatime)
/dev/sda1 on /boot type ext4 (rw,relatime,seclabel,data=ordered)
/dev/mapper/fedora-home on /home type ext4 (rw,relatime,seclabel,data=ordered)
/dev/mapper/fedora-root on / type ext4 (rw,relatime,seclabel,data=ordered)
sunrpc on /var/lib/nfs/rpc_pipefs type rpc_pipefs (rw,relatime)
tmpfs on /run/user/42 type tmpfs (rw,nosuid,nodev,relatime,seclabel,size=1605428k,mode=700,uid=42,gid=42)
tmpfs on /run/user/1000 type tmpfs (rw,nosuid,nodev,relatime,seclabel,size=1605428k,mode=700,uid=1000,gid=1000)
gvfsd-fuse on /run/user/1000/gvfs type fuse.gvfsd-fuse (rw,nosuid,nodev,relatime,user_id=1000,group_id=1000)
fusectl on /sys/fs/fuse/connections type fusectl (rw,relatime)
/dev/mapper/HostVG-Config on /etc/shadow type ext4 (rw,noatime,seclabel,stripe=256,data=ordered) [CONFIG]
/dev/sr0 on /run/media/root/VMware Tools type iso9660 (ro,nosuid,nodev,relatime,uid=0,gid=0,iocharset=utf8,mode=0400,dmode=0500,uhelper=udisks2) [VMware Tools]
""".strip()

# Missing 'on' in second line
MOUNT_ERR_DATA = """
tmpfs on /tmp type tmpfs (rw,seclabel)
hugetlbfs /dev/hugepages type hugetlbfs (rw,relatime,seclabel)
/dev/mapper/fedora-root on / type ext4 (rw,relatime,seclabel,data=ordered)
""".strip()


def test_mount():
    results = Mount(context_wrap(MOUNT_DATA))
    assert results is not None
    assert len(results) == 13
    sr0 = results.search(filesystem='/dev/sr0')[0]
    sda1 = results.search(filesystem='/dev/sda1')[0]
    assert sr0 is not None
    assert sr0['mount_point'] == '/run/media/root/VMware Tools'
    # test get method
    assert sr0.get('mount_point') == '/run/media/root/VMware Tools'
    assert sr0.get('does not exist', 'failure') == 'failure'
    assert sr0['mount_type'] == 'iso9660'
    assert 'ro' in sr0['mount_options']
    assert sr0.mount_options.ro
    assert 'relatime' in sr0['mount_options']
    assert sr0['mount_options']['uhelper'] == 'udisks2'
    assert sr0['mount_label'] == 'VMware Tools'
    assert sda1 is not None
    assert sda1['mount_point'] == '/boot'
    assert sda1['mount_type'] == 'ext4'
    assert 'rw' in sda1['mount_options']
    assert 'seclabel' in sda1['mount_options']
    assert sda1['mount_options']['data'] == 'ordered'
    assert sda1.mount_options.data == 'ordered'
    assert 'mount_label' not in sda1

    # Test iteration
    for mount in results:
        assert hasattr(mount, 'filesystem')
        assert hasattr(mount, 'mount_point')
        assert hasattr(mount, 'mount_type')
        assert hasattr(mount, 'mount_options')

    # Test getitem
    assert results[12] == sr0
    assert results['/etc/shadow'] == results[11]
    # Index only by string or number
    with pytest.raises(TypeError) as exc:
        assert results[set([1, 2, 3])] is None
    assert "Mounts can only be indexed by mount string or line number" in str(exc)

    # Test mounts dictionary
    assert results.mounts['/run/media/root/VMware Tools'] == sr0

    # Test get_dir
    assert results.get_dir('/run/media/root/VMware Tools') == sr0
    assert results.get_dir('/boot/grub2/grub.cfg') == sda1
    assert results.get_dir('/etc') == results['/']
    assert results.get_dir('relative/paths/fail') is None

    # Test parse failure
    errors = Mount(context_wrap(MOUNT_ERR_DATA))
    assert errors is not None
    assert len(errors) == 3
    assert not hasattr(errors[0], 'parse_error')
    assert errors[0].filesystem == 'tmpfs'
    assert hasattr(errors[1], 'parse_error')
    assert errors[1].parse_error == 'Unable to parse line'

    # Test search
    assert results.search(filesystem='/dev/sr0') == [sr0]
    assert results.search(mount_type='tmpfs') == [
        results.rows[n] for n in (0, 7, 8)
    ]
    assert results.search(mount_options__contains='seclabel') == [
        results.rows[n] for n in (0, 1, 3, 4, 5, 7, 8, 11)
    ]


MOUNT_WITHOUT_ROOT = """
tmpfs on /tmp type tmpfs (rw,seclabel)
hugetlbfs on /dev/hugepages type hugetlbfs (rw,relatime,seclabel)
/dev/sda1 on /boot type ext4 (rw,relatime,seclabel,data=ordered)
""".strip()


def test_mount_get_dir():
    with pytest.raises(ParseException) as exc:
        Mount(context_wrap(MOUNT_WITHOUT_ROOT))
    assert "Input for mount must contain '/' mount point." in str(exc)
