import doctest
from insights.parsers.mount import Mount, ProcMounts, MountInfo
from insights.parsers.mount import MountOpts, MountAddtlInfo
from insights.combiners.mounts import Mounts
from insights.combiners import mounts as module_mounts
from insights.tests import context_wrap


MOUNT_DATA = """
/dev/mapper/vgsys-root on / type ext4 (rw)
proc on /proc type proc (rw)
sysfs on /sys type sysfs (rw)
devpts on /dev/pts type devpts (rw,gid=5,mode=620)
tmpfs on /dev/shm type tmpfs (rw,noexec,nosuid,nodev)
/dev/sda1 on /boot type ext4 (rw)
/dev/mapper/vgsys-diskdump on /diskdump type ext4 (rw)
/dev/mapper/vgsys-tmp on /tmp type ext4 (rw)
/dev/mapper/vgsys-var on /var type ext4 (rw)
/dev/mapper/vgsys-var_log on /var/log type ext4 (rw) [cluster7:lv_gfs]
/dev/mapper/vgsys-var_tmp on /var/tmp type ext4 (rw) [VMware Tools]
none on /proc/sys/fs/binfmt_misc type binfmt_misc (rw)
sunrpc on /var/lib/nfs/rpc_pipefs type rpc_pipefs (rw)
hostname1:/shared_dir1 on /shared/dir1 type nfs (rw,nosuid,sync,hard,intr,bg,tcp,timeo=600,rsize=32768,nolock,wsize=32768,noacl,vers=4,addr=10.72.36.91,clientaddr=10.72.32.16)
hostname2:/shared/some/dir2 on /shared/dir2 type nfs (rw,nosuid,sync,hard,intr,bg,tcp,timeo=600,rsize=32768,nolock,wsize=32768,noacl,addr=10.73.32.202)
""".strip()

PROCMOUNTS_DATA = """
rootfs / rootfs rw 0 0
proc /proc proc rw,relatime 0 0
sysfs /sys sysfs rw,relatime 0 0
devtmpfs /dev devtmpfs rw,relatime,size=66002212k,nr_inodes=16500553,mode=755 0 0
devpts /dev/pts devpts rw,relatime,gid=5,mode=620,ptmxmode=000 0 0
tmpfs /dev/shm tmpfs rw,nosuid,nodev,noexec,relatime 0 0
/dev/mapper/vgsys-root / ext4 rw,relatime,barrier=1,stripe=64,data=ordered 0 0
/proc/bus/usb /proc/bus/usb usbfs rw,relatime 0 0
/dev/sda1 /boot ext4 rw,relatime,barrier=1,stripe=64,data=ordered 0 0
/dev/mapper/vgsys-diskdump /diskdump ext4 rw,relatime,barrier=1,stripe=64,data=ordered 0 0
/dev/mapper/vgsys-tmp /tmp ext4 rw,relatime,barrier=1,stripe=64,data=ordered 0 0
/dev/mapper/vgsys-var /var ext4 rw,relatime,barrier=1,stripe=64,data=ordered 0 0
/dev/mapper/vgsys-var_log /var/log ext4 rw,relatime,barrier=1,stripe=64,data=ordered 0 0
/dev/mapper/vgsys-var_tmp /var/tmp ext4 rw,relatime,barrier=1,stripe=64,data=ordered 0 0
none /proc/sys/fs/binfmt_misc binfmt_misc rw,relatime 0 0
sunrpc /var/lib/nfs/rpc_pipefs rpc_pipefs rw,relatime 0 0
hostname1:/shared_dir1 /shared/dir1 nfs4 rw,sync,nosuid,relatime,vers=4,rsize=32768,wsize=32768,namlen=255,hard,proto=tcp,port=0,timeo=600,retrans=2,sec=sys,clientaddr=10.72.32.16,minorversion=0,local_lock=none,addr=10.72.36.91 0 0
hostname2:/shared/some/dir2 /shared/dir2 nfs rw,sync,nosuid,relatime,vers=3,rsize=32768,wsize=32768,namlen=255,hard,nolock,noacl,proto=tcp,timeo=600,retrans=2,sec=sys,mountaddr=10.73.32.108,mountvers=3,mountport=300,mountproto=tcp,local_lock=all,addr=10.73.32.202 0 0
/etc/auto.misc /misc autofs rw,relatime,fd=7,pgrp=4826,timeout=300,minproto=5,maxproto=5,indirect 0 0
-hosts /autofsmp autofs rw,relatime,fd=13,pgrp=4826,timeout=300,minproto=5,maxproto=5,indirect 0 0
""".strip()

MOUNTINFO_DATA = """
16 21 0:3 / /proc rw,relatime - proc proc rw
17 21 0:0 / /sys rw,relatime - sysfs sysfs rw
18 21 0:5 / /dev rw,relatime - devtmpfs devtmpfs rw,size=66002212k,nr_inodes=16500553,mode=755
19 18 0:11 / /dev/pts rw,relatime - devpts devpts rw,gid=5,mode=620,ptmxmode=000
20 18 0:16 / /dev/shm rw,nosuid,nodev,noexec,relatime - tmpfs tmpfs rw
21 1 253:1 / / rw,relatime - ext4 /dev/mapper/vgsys-root rw,barrier=1,stripe=64,data=ordered
22 16 0:15 / /proc/bus/usb rw,relatime - usbfs /proc/bus/usb rw
23 21 8:1 / /boot rw,relatime - ext4 /dev/sda1 rw,barrier=1,stripe=64,data=ordered
25 21 253:32 / /diskdump rw,relatime - ext4 /dev/mapper/vgsys-diskdump rw,barrier=1,stripe=64,data=ordered
33 21 253:33 / /tmp rw,relatime - ext4 /dev/mapper/vgsys-tmp rw,barrier=1,stripe=64,data=ordered
36 21 253:34 / /var rw,relatime - ext4 /dev/mapper/vgsys-var rw,barrier=1,stripe=64,data=ordered
37 36 253:36 / /var/log rw,relatime - ext4 /dev/mapper/vgsys-var_log rw,barrier=1,stripe=64,data=ordered
40 36 253:35 / /var/tmp rw,relatime - ext4 /dev/mapper/vgsys-var_tmp rw,barrier=1,stripe=64,data=ordered
52 16 0:17 / /proc/sys/fs/binfmt_misc rw,relatime - binfmt_misc none rw
53 36 0:18 / /var/lib/nfs/rpc_pipefs rw,relatime - rpc_pipefs sunrpc rw
55 21 0:20 / /shared/dir1 rw,nosuid,relatime - nfs4 hostname1:/shared_dir1 rw,sync,vers=4,rsize=32768,wsize=32768,namlen=255,hard,proto=tcp,port=0,timeo=600,retrans=2,sec=sys,clientaddr=10.72.32.16,minorversion=0,local_lock=none,addr=10.72.36.91
56 21 0:19 / /shared/dir2 rw,nosuid,relatime - nfs hostname2:/shared/some/dir2 rw,sync,vers=3,rsize=32768,wsize=32768,namlen=255,hard,nolock,noacl,proto=tcp,timeo=600,retrans=2,sec=sys,mountaddr=10.73.32.108,mountvers=3,mountport=300,mountproto=tcp,local_lock=all,addr=10.73.32.202
57 21 0:21 / /misc rw,relatime - autofs /etc/auto.misc rw,fd=7,pgrp=4826,timeout=300,minproto=5,maxproto=5,indirect
58 21 0:22 / /autofsmp rw,relatime - autofs -hosts rw,fd=13,pgrp=4826,timeout=300,minproto=5,maxproto=5,indirect
""".strip()


def test_combiner_mounts_all():
    mount = Mount(context_wrap(MOUNT_DATA))
    procmounts = ProcMounts(context_wrap(PROCMOUNTS_DATA))
    mountinfo = MountInfo(context_wrap(MOUNTINFO_DATA))
    mounts = Mounts(mount, procmounts, mountinfo)
    assert len(mounts) == 19

    assert '/' in mounts
    root_entry = mounts['/']
    assert root_entry.mount_type == 'ext4'
    assert len(root_entry.mount_options) == 5
    assert root_entry.mount_options.data == 'ordered'
    root_entry_opts = MountOpts({'rw': True, 'relatime': True, 'barrier': '1', 'stripe': '64', 'data': 'ordered'})
    for k, v in root_entry_opts.items():
        assert root_entry.mount_options[k] == v
    root_entry_addtlinfo = MountAddtlInfo(dict(fs_freq='0', fs_passno='0',
                mount_id='21', parent_id='1', major_minor='253:1', root='/', optional_fields='',
                mount_clause_binmount='/dev/mapper/vgsys-root on / type ext4 (rw)',
                mount_clause_procmounts='/dev/mapper/vgsys-root / ext4 rw,relatime,barrier=1,stripe=64,data=ordered 0 0',
                mount_clause_mountinfo='21 1 253:1 / / rw,relatime - ext4 /dev/mapper/vgsys-root rw,barrier=1,stripe=64,data=ordered'))
    for k, v in root_entry_addtlinfo.items():
        assert root_entry.mount_addtlinfo[k] == v

    assert mounts.search(mount_source="/dev/mapper/vgsys-root")[0]['mount_point'] == '/'

    assert mounts.rows[0] == mounts['/proc']
    assert len([row for row in mounts]) == 19
    assert len(mounts.mount_points) == 19
    assert mounts.get_dir('/var/somedir') == mounts['/var']
    assert mounts.get_dir('not/absolute/path') is None


def test_combiner_wo_mountinfo():
    mount = Mount(context_wrap(MOUNT_DATA))
    procmounts = ProcMounts(context_wrap(PROCMOUNTS_DATA))
    mounts = Mounts(mount, procmounts, None)
    assert len(mounts) == 19

    assert '/' in mounts
    root_entry = mounts['/']
    assert root_entry.mount_type == 'ext4'
    root_entry_opts = MountOpts({'rw': True, 'relatime': True, 'barrier': '1', 'stripe': '64', 'data': 'ordered'})
    for k, v in root_entry_opts.items():
        assert root_entry.mount_options[k] == v
    root_entry_addtlinfo = MountAddtlInfo(dict(fs_freq='0', fs_passno='0',
                mount_clause_binmount='/dev/mapper/vgsys-root on / type ext4 (rw)',
                mount_clause_procmounts='/dev/mapper/vgsys-root / ext4 rw,relatime,barrier=1,stripe=64,data=ordered 0 0'))
    for k, v in root_entry_addtlinfo.items():
        assert root_entry.mount_addtlinfo[k] == v

    assert mounts.search(mount_source="/dev/mapper/vgsys-root")[0]['mount_point'] == '/'
    assert mounts.rows[0] == mounts['/']


def test_combiner_wo_binmount():
    procmounts = ProcMounts(context_wrap(PROCMOUNTS_DATA))
    mountinfo = MountInfo(context_wrap(MOUNTINFO_DATA))
    mounts = Mounts(None, procmounts, mountinfo)
    assert len(mounts) == 19

    assert '/' in mounts
    root_entry = mounts['/']
    assert root_entry.mount_type == 'ext4'
    root_entry_opts = MountOpts({'rw': True, 'relatime': True, 'barrier': '1', 'stripe': '64', 'data': 'ordered'})
    for k, v in root_entry_opts.items():
        assert root_entry.mount_options[k] == v
    root_entry_addtlinfo = MountAddtlInfo(dict(fs_freq='0', fs_passno='0',
                mount_id='21', parent_id='1', major_minor='253:1', root='/', optional_fields='',
                mount_clause_procmounts='/dev/mapper/vgsys-root / ext4 rw,relatime,barrier=1,stripe=64,data=ordered 0 0',
                mount_clause_mountinfo='21 1 253:1 / / rw,relatime - ext4 /dev/mapper/vgsys-root rw,barrier=1,stripe=64,data=ordered'))
    for k, v in root_entry_addtlinfo.items():
        assert root_entry.mount_addtlinfo[k] == v

    assert mounts.search(mount_source="/dev/mapper/vgsys-root")[0]['mount_point'] == '/'
    assert mounts.rows[0] == mounts['/proc']


def test_combiner_wo_procmount():
    mount = Mount(context_wrap(MOUNT_DATA))
    mountinfo = MountInfo(context_wrap(MOUNTINFO_DATA))
    mounts = Mounts(mount, None, mountinfo)
    assert len(mounts) == 19

    assert '/' in mounts
    root_entry = mounts['/']
    assert root_entry.mount_type == 'ext4'
    root_entry_opts = MountOpts({'rw': True, 'relatime': True, 'barrier': '1', 'stripe': '64', 'data': 'ordered'})
    for k, v in root_entry_opts.items():
        assert root_entry.mount_options[k] == v
    root_entry_addtlinfo = MountAddtlInfo(dict(
                mount_id='21', parent_id='1', major_minor='253:1', root='/', optional_fields='',
                mount_clause_binmount='/dev/mapper/vgsys-root on / type ext4 (rw)',
                mount_clause_mountinfo='21 1 253:1 / / rw,relatime - ext4 /dev/mapper/vgsys-root rw,barrier=1,stripe=64,data=ordered'))
    for k, v in root_entry_addtlinfo.items():
        assert root_entry.mount_addtlinfo[k] == v

    assert mounts.search(mount_source="/dev/mapper/vgsys-root")[0]['mount_point'] == '/'
    assert mounts.rows[0] == mounts['/proc']


def test_combiner_only_binmount():
    mount = Mount(context_wrap(MOUNT_DATA))
    mounts = Mounts(mount, None, None)
    assert len(mounts) == 15

    assert '/' in mounts
    root_entry = mounts['/']
    assert root_entry.mount_type == 'ext4'
    root_entry_opts = MountOpts({'rw': True})
    for k, v in root_entry_opts.items():
        assert root_entry.mount_options[k] == v
    root_entry_addtlinfo = MountAddtlInfo(dict(
                mount_clause_binmount='/dev/mapper/vgsys-root on / type ext4 (rw)'))
    for k, v in root_entry_addtlinfo.items():
        assert root_entry.mount_addtlinfo[k] == v

    assert mounts.search(mount_source="/dev/mapper/vgsys-root")[0]['mount_point'] == '/'
    assert mounts.rows[0] == mounts['/']


def test_docs():
    mount = Mount(context_wrap(MOUNT_DATA))
    procmounts = ProcMounts(context_wrap(PROCMOUNTS_DATA))
    mountinfo = MountInfo(context_wrap(MOUNTINFO_DATA))
    mounts = Mounts(mount, procmounts, mountinfo)
    env = {
        'mounts': mounts
    }
    failed, total = doctest.testmod(module_mounts, globs=env)
    assert failed == 0
