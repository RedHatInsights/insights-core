from falafel.mappers import mount
from falafel.tests import context_wrap

MOUNT = """
tmpfs on /tmp type tmpfs (rw,seclabel)
hugetlbfs on /dev/hugepages type hugetlbfs (rw,relatime,seclabel)
nfsd on /proc/fs/nfsd type nfsd (rw,relatime)
/dev/sda1 on /boot type ext4 (rw,relatime,seclabel,data=ordered)
/dev/mapper/fedora-home on /home type ext4 (rw,relatime,seclabel,data=ordered)
sunrpc on /var/lib/nfs/rpc_pipefs type rpc_pipefs (rw,relatime)
tmpfs on /run/user/42 type tmpfs (rw,nosuid,nodev,relatime,seclabel,size=1605428k,mode=700,uid=42,gid=42)
tmpfs on /run/user/1000 type tmpfs (rw,nosuid,nodev,relatime,seclabel,size=1605428k,mode=700,uid=1000,gid=1000)
gvfsd-fuse on /run/user/1000/gvfs type fuse.gvfsd-fuse (rw,nosuid,nodev,relatime,user_id=1000,group_id=1000)
fusectl on /sys/fs/fuse/connections type fusectl (rw,relatime)
/dev/mapper/HostVG-Config on /etc/shadow type ext4 (rw,noatime,seclabel,stripe=256,data=ordered) [CONFIG]
dev/sr0 on /run/media/root/VMware Tools type iso9660 (ro,nosuid,nodev,relatime,uid=0,gid=0,iocharset=utf8,mode=0400,dmode=0500,uhelper=udisks2) [VMware Tools]
""".strip()


class TestMount():
    def test_mount(self):
        mount_list = mount.get_mount(context_wrap(MOUNT))
        assert len(mount_list) == 12
        assert mount_list == [{'mount_type': 'tmpfs', 'mount_point': '/tmp', 'mount_clause': 'tmpfs on /tmp type tmpfs (rw,seclabel)', 'mount_options': ['rw', 'seclabel'], 'filesystem': 'tmpfs'}, {'mount_type': 'hugetlbfs', 'mount_point': '/dev/hugepages', 'mount_clause': 'hugetlbfs on /dev/hugepages type hugetlbfs (rw,relatime,seclabel)', 'mount_options': ['rw', 'relatime', 'seclabel'], 'filesystem': 'hugetlbfs'}, {'mount_type': 'nfsd', 'mount_point': '/proc/fs/nfsd', 'mount_clause': 'nfsd on /proc/fs/nfsd type nfsd (rw,relatime)', 'mount_options': ['rw', 'relatime'], 'filesystem': 'nfsd'}, {'mount_type': 'ext4', 'mount_point': '/boot', 'mount_clause': '/dev/sda1 on /boot type ext4 (rw,relatime,seclabel,data=ordered)', 'mount_options': ['rw', 'relatime', 'seclabel', 'data=ordered'], 'filesystem': '/dev/sda1'}, {'mount_type': 'ext4', 'mount_point': '/home', 'mount_clause': '/dev/mapper/fedora-home on /home type ext4 (rw,relatime,seclabel,data=ordered)', 'mount_options': ['rw', 'relatime', 'seclabel', 'data=ordered'], 'filesystem': '/dev/mapper/fedora-home'}, {'mount_type': 'rpc_pipefs', 'mount_point': '/var/lib/nfs/rpc_pipefs', 'mount_clause': 'sunrpc on /var/lib/nfs/rpc_pipefs type rpc_pipefs (rw,relatime)', 'mount_options': ['rw', 'relatime'], 'filesystem': 'sunrpc'}, {'mount_type': 'tmpfs', 'mount_point': '/run/user/42', 'mount_clause': 'tmpfs on /run/user/42 type tmpfs (rw,nosuid,nodev,relatime,seclabel,size=1605428k,mode=700,uid=42,gid=42)', 'mount_options': ['rw', 'nosuid', 'nodev', 'relatime', 'seclabel', 'size=1605428k', 'mode=700', 'uid=42', 'gid=42'], 'filesystem': 'tmpfs'}, {'mount_type': 'tmpfs', 'mount_point': '/run/user/1000', 'mount_clause': 'tmpfs on /run/user/1000 type tmpfs (rw,nosuid,nodev,relatime,seclabel,size=1605428k,mode=700,uid=1000,gid=1000)', 'mount_options': ['rw', 'nosuid', 'nodev', 'relatime', 'seclabel', 'size=1605428k', 'mode=700', 'uid=1000', 'gid=1000'], 'filesystem': 'tmpfs'}, {'mount_type': 'fuse.gvfsd-fuse', 'mount_point': '/run/user/1000/gvfs', 'mount_clause': 'gvfsd-fuse on /run/user/1000/gvfs type fuse.gvfsd-fuse (rw,nosuid,nodev,relatime,user_id=1000,group_id=1000)', 'mount_options': ['rw', 'nosuid', 'nodev', 'relatime', 'user_id=1000', 'group_id=1000'], 'filesystem': 'gvfsd-fuse'}, {'mount_type': 'fusectl', 'mount_point': '/sys/fs/fuse/connections', 'mount_clause': 'fusectl on /sys/fs/fuse/connections type fusectl (rw,relatime)', 'mount_options': ['rw', 'relatime'], 'filesystem': 'fusectl'}, {'mount_type': 'ext4', 'mount_point': '/etc/shadow', 'mount_clause': '/dev/mapper/HostVG-Config on /etc/shadow type ext4 (rw,noatime,seclabel,stripe=256,data=ordered) [CONFIG]', 'mount_options': ['rw', 'noatime', 'seclabel', 'stripe=256', 'data=ordered'], 'filesystem': '/dev/mapper/HostVG-Config'}, {'mount_type': 'iso9660', 'mount_point': '/run/media/root/VMware Tools', 'mount_clause': 'dev/sr0 on /run/media/root/VMware Tools type iso9660 (ro,nosuid,nodev,relatime,uid=0,gid=0,iocharset=utf8,mode=0400,dmode=0500,uhelper=udisks2) [VMware Tools]', 'mount_options': ['ro', 'nosuid', 'nodev', 'relatime', 'uid=0', 'gid=0', 'iocharset=utf8', 'mode=0400', 'dmode=0500', 'uhelper=udisks2'], 'filesystem': 'dev/sr0'}]
        assert mount_list[11].get("mount_point") == "/run/media/root/VMware Tools"
        assert mount_list[10].get("mount_options") == ['rw', 'noatime', 'seclabel', 'stripe=256', 'data=ordered']


