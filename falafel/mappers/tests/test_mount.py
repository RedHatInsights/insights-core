""""
test mount
==========
"""

from falafel.mappers import mount
from falafel.core.context import Context

MOUNT_DATA = ['tmpfs on /tmp type tmpfs (rw,seclabel)',
              'hugetlbfs on /dev/hugepages type hugetlbfs (rw,relatime,seclabel)',
              'nfsd on /proc/fs/nfsd type nfsd (rw,relatime)',
              '/dev/sda1 on /boot type ext4 (rw,relatime,seclabel,data=ordered)',
              '/dev/mapper/fedora-home on /home type ext4 (rw,relatime,seclabel,data=ordered)',
              'sunrpc on /var/lib/nfs/rpc_pipefs type rpc_pipefs (rw,relatime)',
              'tmpfs on /run/user/42 type tmpfs (rw,nosuid,nodev,relatime,seclabel,size=1605428k,mode=700,uid=42,gid=42)',
              'tmpfs on /run/user/1000 type tmpfs (rw,nosuid,nodev,relatime,seclabel,size=1605428k,mode=700,uid=1000,gid=1000)',
              'gvfsd-fuse on /run/user/1000/gvfs type fuse.gvfsd-fuse (rw,nosuid,nodev,relatime,user_id=1000,group_id=1000)',
              'fusectl on /sys/fs/fuse/connections type fusectl (rw,relatime)',
              '/dev/mapper/HostVG-Config on /etc/shadow type ext4 (rw,noatime,seclabel,stripe=256,data=ordered) [CONFIG]',
              '/dev/sr0 on /run/media/root/VMware Tools type iso9660 (ro,nosuid,nodev,relatime,uid=0,gid=0,iocharset=utf8,mode=0400,dmode=0500,uhelper=udisks2) [VMware Tools]']


def test_mount():
    context = Context(content=MOUNT_DATA)
    results = mount.Mount.parse_context(context)
    assert results is not None
    assert len(results) == 12
    sr0 = None
    sda1 = None
    for result in results:
        if result['filesystem'] == '/dev/sr0':
            sr0 = result
        elif result['filesystem'] == '/dev/sda1':
            sda1 = result
    assert sr0 is not None
    assert sr0['mount_point'] == '/run/media/root/VMware Tools'
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
