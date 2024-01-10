import doctest
import pytest

from insights.core.exceptions import ParseException, SkipComponent
from insights.parsers import mount
from insights.parsers.mount import Mount, ProcMounts, MountInfo
from insights.tests import context_wrap

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

MOUNT_WITHOUT_ROOT = """
tmpfs on /tmp type tmpfs (rw,seclabel)
hugetlbfs on /dev/hugepages type hugetlbfs (rw,relatime,seclabel)
/dev/sda1 on /boot type ext4 (rw,relatime,seclabel,data=ordered)
""".strip()


PROC_MOUNT = """
proc /proc proc rw,relatime 0 0
sysfs /sys sysfs rw,relatime 0 0
devtmpfs /dev devtmpfs rw,relatime,size=8155456k,nr_inodes=2038864,mode=755 0 0
devpts /dev/pts devpts rw,relatime,gid=5,mode=620,ptmxmode=000 0 0
tmpfs /dev/shm tmpfs rw,nosuid,nodev,noexec,relatime 0 0
/dev/mapper/rootvg-rootlv / ext4 rw,relatime,barrier=1,data=ordered 0 0
/proc/bus/usb /proc/bus/usb usbfs rw,relatime 0 0
/dev/sda1 /boot ext4 rw,relatime,barrier=1,data=ordered 0 0
/dev/mapper/rootvg-homelv /home ext4 rw,relatime,barrier=1,data=ordered 0 0
/dev/mapper/rootvg-optlv /opt ext4 rw,relatime,barrier=1,data=ordered 0 0
/dev/mapper/rootvg-tmplv /tmp ext4 rw,relatime,barrier=1,data=ordered 0 0
/dev/mapper/rootvg-usrlv /usr ext4 rw,relatime,barrier=1,data=ordered 0 0
/dev/mapper/rootvg-varlv /var ext4 rw,relatime,barrier=1,data=ordered 0 0
/dev/mapper/rootvg-tmplv /var/tmp ext4 rw,relatime,barrier=1,data=ordered 0 0
none /proc/sys/fs/binfmt_misc binfmt_misc rw,relatime 0 0
sunrpc /var/lib/nfs/rpc_pipefs rpc_pipefs rw,relatime 0 0
/vol/vol3/wpsanet /sa/net nfs rw,relatime,vers=3,rsize=8192,wsize=8192,namlen=255,soft,proto=tcp,timeo=14,retrans=2,sec=sys,mountaddr=10.xx.xx.xx,mountvers=3,mountport=4046,mountproto=udp,local_lock=none 0 0
/vol/vol9/home /users nfs rw,relatime,vers=3,rsize=8192,wsize=8192,namlen=255,soft,proto=tcp,timeo=14,retrans=2,sec=sys,mountaddr=10.xx.xx.xx,mountvers=3,mountport=4046,mountproto=udp,local_lock=none,addr=10.xx.xx.xx 0 0
/etc/auto.misc /misc autofs rw,relatime,fd=7,pgrp=1936,timeout=300,minproto=5,maxproto=5,indirect 0 0
""".strip()

PROC_MOUNT_QUOTES = '''
/dev/mapper/rootvg-rootlv / ext4 rw,relatime,barrier=1,data=ordered 0 0
tmpfs /var/lib/containers/storage/overlay-containers/ff7e79fc09c/userdata/shm tmpfs rw,nosuid,nodev,noexec,relatime,context="system_u:object_r:container_file_t:s0:c184,c371",size=64000k 0 0
tmpfs /var/lib/containers/storage/overlay-containers/aa7e79fc09c/userdata/shm tmpfs rw,nosuid,nodev,noexec,relatime,context="system_u:object_r:container_file_t:s0",size=64000k 0 0
tmpfs /var/lib/containers/storage/overlay-containers/bb7e79fc09c/userdata/shm tmpfs rw,nosuid,nodev,noexec,relatime,context="system_u:object_r:container_file_t:s0:c184,c371,c381,c391",size=64000k 0 0
tmpfs /var/lib/containers/storage/overlay-containers/cc7e79fc09c/userdata/shm tmpfs rw,nosuid,nodev,noexec,relatime,context="system_u:object_r:container_file_t:s0:c184,c371,c381,c391" 0 0
'''

PROCMOUNT_ERR_DATA = """
rootfs / rootfs rw 0 0
sysfs /sys sysfs rw,relatime
""".strip()

PROC_EXCEPTION1 = """
""".strip()

PROC_EXCEPTION2 = """
proc /proc proc rw,relatime 0 0
sysfs /sys sysfs rw,relatime 0 0
devtmpfs /dev devtmpfs rw,relatime,size=8155456k,nr_inodes=2038864,mode=755 0 0
""".strip()

MOUNTINFO_DATA = """
18 21 0:5 / /dev rw,relatime - devtmpfs devtmpfs rw,size=66002212k,nr_inodes=16500553,mode=755
19 18 0:11 / /dev/pts rw,relatime - devpts devpts rw,gid=5,mode=620,ptmxmode=000
20 18 0:16 / /dev/shm rw,nosuid,nodev,noexec,relatime - tmpfs tmpfs rw
21 1 253:1 / / rw,relatime - ext4 /dev/mapper/vgsys-root rw,barrier=1,stripe=64,data=ordered
23 21 8:1 / /boot rw,relatime - ext4 /dev/sda1 rw,barrier=1,stripe=64,data=ordered
25 21 253:32 / /diskdump rw,relatime - ext4 /dev/mapper/vgsys-diskdump rw,barrier=1,stripe=64,data=ordered
26 21 253:17 / /opt/CA rw,relatime - ext4 /dev/mapper/vgcore-opt_CA rw,barrier=1,stripe=64,data=ordered
36 21 253:34 / /var rw,relatime - ext4 /dev/mapper/vgsys-var rw,barrier=1,stripe=64,data=ordered
37 36 253:36 / /var/log rw,relatime - ext4 /dev/mapper/vgsys-var_log rw,barrier=1,stripe=64,data=ordered
38 36 253:22 / /var/opt/OV rw,relatime - ext4 /dev/mapper/vgcore-var_opt_OV rw,barrier=1,stripe=64,data=ordered
52 16 0:17 / /proc/sys/fs/binfmt_misc rw,relatime - binfmt_misc none rw
53 36 0:18 / /var/lib/nfs/rpc_pipefs rw,relatime - rpc_pipefs sunrpc rw
55 21 0:20 / /shared/dir1 rw,nosuid,relatime - nfs4 hostname1:/shared_dir1 rw,sync,vers=4,rsize=32768,wsize=32768,namlen=255,hard,proto=tcp,port=0,timeo=600,ret
56 21 0:19 / /shared/dir2 rw,nosuid,relatime - nfs hostname2:/shared/some/dir2 rw,sync,vers=3,rsize=32768,wsize=32
57 21 0:21 / /misc rw,relatime - autofs /etc/auto.misc rw,fd=7,pgrp=4826,timeout=300,minproto=5,maxproto=5,indirect
58 21 0:22 / /autofshost rw,relatime - autofs -hosts rw,fd=13,pgrp=4826,timeout=300,minproto=5,maxproto=5,indirect
""".strip()

MOUNTINFO_ERR_DATA = """
18 21 0:5 / /dev rw,relatime - devtmpfs devtmpfs rw,size=66002212k,nr_inodes=16500553,mode=755
20 18 0:16 / /dev/shm rw,nosuid,nodev,noexec,relatime - tmpfs tmpfs rw
21 1 253:1 / / rw,relatime  ext4 /dev/mapper/vgsys-root rw,barrier=1,stripe=64,data=ordered
23 21 8:1 / /boot rw,relatime - ext4 /dev/sda1 rw,barrier=1,stripe=64,data=ordered
""".strip()

MOUNTINFO_EXCEPTION = """
""".strip()

MOUNT_DOC = """
/dev/mapper/rootvg-rootlv on / type ext4 (rw,relatime,barrier=1,data=ordered)
proc on /proc type proc (rw,nosuid,nodev,noexec,relatime)
/dev/mapper/HostVG-Config on /etc/shadow type ext4 (rw,noatime,seclabel,stripe=256,data=ordered)
dev/sr0 on /run/media/root/VMware Tools type iso9660 (ro,nosuid,nodev,relatime,uid=0,gid=0,iocharset=utf8,mode=0400,dmode=0500,uhelper=udisks2) [VMware Tools]
""".strip()

PROC_MOUNT_DOC = """
/dev/mapper/rootvg-rootlv / ext4 rw,relatime,barrier=1,data=ordered 0 0
proc /proc proc rw,nosuid,nodev,noexec,relatime 0 0
/dev/mapper/HostVG-Config /etc/shadow ext4 rw,noatime,seclabel,stripe=256,data=ordered 0 0
dev/sr0 /run/media/root/VMware\040Tools iso9660 ro,nosuid,nodev,relatime,uid=0,gid=0,iocharset=utf8,mode=0400,dmode=0500,uhelper=udisks2 0 0
""".strip()

MOUNTINFO_DOC = """
39 0 253:0 / / rw,relatime shared:1 - xfs /dev/mapper/rootvg-lvlocroot rw,attr2,inode64,noquota
47 39 8:1 / /boot rw,relatime shared:30 - xfs /dev/sda1 rw,attr2,inode64,noquota
65 39 253:19 / /data rw,relatime shared:44 - ext4 /dev/mapper/vgdata-lvdata rw,data=ordered
58 39 253:15 / /opt rw,relatime shared:45 - xfs /dev/mapper/rootvg-lvlocopt rw,attr2,inode64,noquota
61 39 253:17 / /home rw,nosuid,relatime shared:46 - xfs /dev/mapper/rootvg-lvlochome rw,attr2,inode64,noquotao
""".strip()

MOUNT_DATA_WITH_SPECIAL_MNT_POINT = """
hugetlbfs on /dev/hugepages type hugetlbfs (rw,relatime,seclabel)
/dev/sda1 on /boot type ext4 (rw,relatime,seclabel,data=ordered)
/dev/mapper/fedora-root on / type ext4 (rw,relatime,seclabel,data=ordered)
/dev/mapper/HostVG-Config on /etc/shadow type ext4 (rw,noatime,seclabel,stripe=256,data=ordered) [CONFIG]
/dev/sr0 on /run/media/root/VMware Tools type iso9660 (ro,nosuid,nodev,relatime,uid=0,gid=0,iocharset=utf8,mode=0400,dmode=0500,uhelper=udisks2) [VMware Tools]
/dev/sr1 on /run/media/Disk on C type NFS type iso9660 (ro,uid=0,gid=0,iocharset=utf8,uhelper=udisks2) [C type Disk]
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
    assert sr0['mount_label'] == '[VMware Tools]'
    assert sda1 is not None
    assert sda1['mount_point'] == '/boot'
    assert sda1['mount_type'] == 'ext4'
    assert 'rw' in sda1['mount_options']
    assert 'seclabel' in sda1['mount_options']
    assert sda1['mount_options']['data'] == 'ordered'
    assert sda1.mount_options.data == 'ordered'
    assert 'mount_label' not in sda1

    # Test iteration
    for mnt in results:
        assert hasattr(mnt, 'filesystem')
        assert hasattr(mnt, 'mount_point')
        assert hasattr(mnt, 'mount_type')
        assert hasattr(mnt, 'mount_options')

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

    # Test search
    assert results.search(filesystem='/dev/sr0') == [sr0]
    assert results.search(mount_type='tmpfs') == [
        results.rows[n] for n in (0, 7, 8)
    ]
    assert results.search(mount_options__contains='seclabel') == [
        results.rows[n] for n in (0, 1, 3, 4, 5, 7, 8, 11)
    ]


def test_mount_with_special_mnt_point():
    results = Mount(context_wrap(MOUNT_DATA_WITH_SPECIAL_MNT_POINT))
    assert len(results) == 6
    sr0 = results.search(filesystem='/dev/sr0')[0]
    sr1 = results.search(filesystem='/dev/sr1')[0]
    assert sr0['mount_point'] == '/run/media/root/VMware Tools'
    assert sr1['mount_point'] == '/run/media/Disk on C type NFS'
    assert sr0.get('mount_label') == '[VMware Tools]'
    assert sr1.get('mount_label') == '[C type Disk]'
    assert results['/run/media/Disk on C type NFS'].get('mount_label') == '[C type Disk]'


def test_mount_exception1():
    # Test parse failure
    with pytest.raises(ParseException) as pe:
        Mount(context_wrap(MOUNT_ERR_DATA))
    assert 'Unable to parse' in str(pe.value)


def test_mount_exception2():
    with pytest.raises(ParseException) as exc:
        Mount(context_wrap(MOUNT_WITHOUT_ROOT))
    assert "Input for mount must contain '/' mount point." in str(exc)


def test_proc_mount():
    results = ProcMounts(context_wrap(PROC_MOUNT))
    assert results is not None
    assert len(results) == 19
    sda1 = results.search(filesystem='/dev/sda1')[0]

    # Test get method
    assert sda1 is not None
    assert sda1['mount_point'] == '/boot'
    assert sda1['mount_type'] == 'ext4'
    assert 'rw' in sda1['mount_options']
    assert 'relatime' in sda1['mount_options']
    assert sda1['mount_options']['data'] == 'ordered'
    assert sda1.mount_options.data == 'ordered'
    assert sda1['mount_label'] == ['0', '0']

    # Test iteration
    for mnt in results:
        assert hasattr(mnt, 'filesystem')
        assert hasattr(mnt, 'mount_point')
        assert hasattr(mnt, 'mount_type')
        assert hasattr(mnt, 'mount_options')

    # Test getitem
    assert results[7] == sda1
    assert results['/misc'] == results[-1]
    # Index only by string or number
    with pytest.raises(TypeError) as exc:
        assert results[set([1, 2, 3])] is None
    assert 'Mounts can only be indexed by mount string or line number' in str(exc)

    # Test mounts dictionary
    assert results.mounts['/boot'] == sda1

    # Test get_dir
    assert results.get_dir('/var/lib/nfs/rpc_pipefs') == results.search(filesystem='sunrpc')[0]
    assert results.get_dir('/etc') == results['/']

    # Test search
    assert results.search(filesystem='/dev/sda1') == [sda1]
    assert results.search(mount_type='nfs') == [
        results.rows[n] for n in (16, 17)
    ]
    assert results.search(mount_options__contains='mode') == [
        results.rows[n] for n in (2, 3)
    ]


def test_proc_mount_quotes():
    results = ProcMounts(context_wrap(PROC_MOUNT_QUOTES))
    assert results is not None
    assert len(results) == 5
    device = results['/var/lib/containers/storage/overlay-containers/ff7e79fc09c/userdata/shm']
    assert device.mount_options.context == "system_u:object_r:container_file_t:s0:c184,c371"
    device = results['/var/lib/containers/storage/overlay-containers/aa7e79fc09c/userdata/shm']
    assert device.mount_options.context == "system_u:object_r:container_file_t:s0"
    device = results['/var/lib/containers/storage/overlay-containers/bb7e79fc09c/userdata/shm']
    assert device.mount_options.context == "system_u:object_r:container_file_t:s0:c184,c371,c381,c391"
    assert not hasattr(device.mount_options, "c391")
    assert not hasattr(device.mount_options, "c381")
    assert not hasattr(device.mount_options, "c371")
    assert device.mount_options.relatime
    assert device.mount_options.size == "64000k"
    device = results['/var/lib/containers/storage/overlay-containers/cc7e79fc09c/userdata/shm']
    assert device.mount_options.context == "system_u:object_r:container_file_t:s0:c184,c371,c381,c391"


def test_proc_mount_exception1():
    with pytest.raises(SkipComponent) as e:
        ProcMounts(context_wrap(PROC_EXCEPTION1))
    assert 'Empty content' in str(e)


def test_proc_mount_exception2():
    with pytest.raises(ParseException) as e:
        ProcMounts(context_wrap(PROC_EXCEPTION2))
    assert "Input for mount must contain '/' mount point." in str(e)


def test_proc_mount_exception3():
    with pytest.raises(ParseException) as pe:
        ProcMounts(context_wrap(PROCMOUNT_ERR_DATA))
    assert 'Unable to parse' in str(pe.value)


def test_mountinfo():
    results = MountInfo(context_wrap(MOUNTINFO_DATA))
    assert results is not None
    assert len(results) == 16

    sda1 = results.search(mount_source='/dev/sda1')[0]
    assert sda1 is not None
    assert sda1['mount_point'] == '/boot'
    # test get method
    assert sda1.get('mount_point') == '/boot'
    assert sda1.get('does_not_exist', 'failure') == 'failure'
    assert sda1['mount_type'] == 'ext4'
    assert 'rw' in sda1['mount_options']
    assert sda1.mount_options.rw
    assert 'data' in sda1['mount_options']
    assert sda1['mount_options']['data'] == 'ordered'
    assert 'mount_label' not in sda1
    assert sda1 is not None

    dir1 = results.search(mount_point='/shared/dir1')[0]
    assert dir1['mount_source'] == 'hostname1:/shared_dir1'
    assert dir1['mount_type'] == 'nfs4'
    assert 'vers' in dir1['mount_options']
    assert dir1['mount_options']['vers'] == '4'
    assert dir1['mount_addtlinfo'].major_minor == '0:20'
    assert dir1.mount_addtlinfo.mount_id == '55'

    # Test iteration
    for mnt in results:
        assert hasattr(mnt, 'mount_source')
        assert hasattr(mnt, 'mount_point')
        assert hasattr(mnt, 'mount_type')
        assert hasattr(mnt, 'mount_options')

    # Test getitem
    assert results[4] == sda1
    assert results['/shared/dir1'] == results[12]
    # Index only by string or number
    with pytest.raises(TypeError) as exc:
        assert results[set([1, 2, 3])] is None
    assert "Mounts can only be indexed by mount string or line number" in str(exc)

    # Test mounts dictionary
    assert results.mounts['/boot'] == sda1

    # Test get_dir
    assert results.get_dir('/var/log/some_dir') == results.search(mount_point='/var/log')[0]
    assert results.get_dir('/etc') == results['/']

    # Test search
    assert results.search(mount_type='nfs') == [results.rows[13]]
    assert results.search(mount_options__contains='mode') == [
        results.rows[n] for n in (0, 1)
    ]


def test_doc_examples():
    env = {
            'mnt_info': Mount(context_wrap(MOUNT_DOC)),
            'proc_mnt_info': ProcMounts(context_wrap(PROC_MOUNT_DOC)),
            'proc_mountinfo': MountInfo(context_wrap(MOUNTINFO_DOC)),
            'mounts': Mount(context_wrap(MOUNT_DOC))

          }
    failed, total = doctest.testmod(mount, globs=env)
    assert failed == 0
