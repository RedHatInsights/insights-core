import doctest
import pytest

from insights.parsers import df, ParseException
from insights.tests import context_wrap

DF_LI = """
Filesystem        Inodes  IUsed     IFree IUse% Mounted on
/dev/mapper/vg_lxcrhel6sat56-lv_root

                 6275072 124955   6150117    2% /

devtmpfs         1497120    532   1496588    1% /dev
tmpfs            1499684    331   1499353    1% /dev/shm
tmpfs            1499684    728   1498956    1% /run
tmpfs            1499684     16   1499668    1% /sys/fs/cgroup
tmpfs            1499684     54   1499630    1% /tmp
/dev/sda2      106954752 298662 106656090    1% /home
/dev/sda1         128016    429    127587    1% /boot
/dev/sdb1        1499684      6   1499678    1% /V M T o o l s
/dev/sdb2        1499684     15   1499669    1% /VM Tools
""".strip()


def test_df_li():
    df_list = df.DiskFree_LI(context_wrap(DF_LI))
    assert len(df_list) == 10
    assert len(df_list.mounts) == 10
    assert len(df_list.filesystems) == 7
    assert '/home' in df_list.mounts
    r = df.Record(
        filesystem='/dev/sda2',
        total='106954752',
        used='298662',
        available='106656090',
        capacity='1%',
        mounted_on='/home'
    )

    assert df_list.get_mount('/home') == r
    assert '/dev/sda2' in df_list.filesystems
    assert len(df_list.get_filesystem('/dev/sda2')) == 1
    assert df_list.get_filesystem('/dev/sda2')[0] == r
    assert len(df_list.get_filesystem('tmpfs')) == 4
    assert df_list.get_mount('/dev').filesystem == 'devtmpfs'
    assert df_list.get_mount('/run').total == '1499684'
    assert df_list.get_mount('/tmp').used == '54'
    assert df_list.get_mount('/boot').available == '127587'
    assert df_list.get_filesystem('/dev/sda2')[0].capacity == '1%'
    assert df_list.get_filesystem('/dev/sda2')[0].available == '106656090'
    assert df_list.get_filesystem('devtmpfs')[0].mounted_on == '/dev'
    assert df_list.get_mount('/V M T o o l s').available == '1499678'
    assert df_list.get_filesystem('/dev/mapper/vg_lxcrhel6sat56-lv_root')[0].mounted_on == '/'
    sorted_mount_names = sorted([
        '/', '/dev', '/dev/shm', '/run', '/sys/fs/cgroup', '/tmp', '/home',
        '/boot', '/V M T o o l s', '/VM Tools'
    ])
    assert sorted([d.mounted_on for d in df_list]) == sorted_mount_names
    assert sorted(df_list.mount_names) == sorted_mount_names
    assert sorted(df_list.filesystem_names) == sorted([
        '/dev/mapper/vg_lxcrhel6sat56-lv_root', 'devtmpfs', 'tmpfs',
        '/dev/sda2', '/dev/sda1', '/dev/sdb2', '/dev/sdb1'
    ])

    # Test get_path
    # Root mount point works:
    assert df_list.get_dir('/') == df_list.get_mount('/')
    # Mount point underneath root works:
    assert df_list.get_dir('/dev') == df_list.get_mount('/dev')
    # Directory underneath sub-mount:
    assert df_list.get_dir('/boot/grub2') == df_list.get_mount('/boot')
    # Directory with / suffix:
    assert df_list.get_dir('/boot/grub2/') == df_list.get_mount('/boot')
    # File path also works:
    assert df_list.get_dir('/boot/grub2/grub.cfg') == df_list.get_mount('/boot')
    # Relative path returns None
    assert df_list.get_dir('var/lib') is None
    # Invalid path returns None
    assert df_list.get_dir('"') is None


DF_ALP = """
/bin/df: '/vobs/GEMS': No such file or directory
/bin/df: '/vobs/NT/TFax': No such file or directory
Filesystem                           1024-blocks      Used Available Capacity Mounted on
/dev/mapper/vg_lxcrhel6sat56-lv_root    98571884   4244032  89313940       5% /
sysfs                                          0         0         0        - /sys
proc                                           0         0         0        - /proc
devtmpfs                                 5988480         0   5988480       0% /dev
securityfs                                     0         0         0        - /sys/kernel/security
tmpfs                                    5998736    491660   5507076       9% /dev/shm
devpts                                         0         0         0        - /dev/pts
tmpfs                                    5998736      1380   5997356       1% /run

tmpfs                                    5998736         0   5998736       0% /sys/fs/cgroup
""".strip()


def test_df_alP():
    df_list = df.DiskFree_ALP(context_wrap(DF_ALP))
    assert len(df_list) == 9
    assert len(df_list.mounts) == 9
    assert len(df_list.filesystems) == 7
    assert '/' in df_list.mounts
    r = df.Record(
        filesystem='/dev/mapper/vg_lxcrhel6sat56-lv_root',
        total='98571884',
        used='4244032',
        available='89313940',
        capacity='5%',
        mounted_on='/'
    )
    assert df_list.get_mount('/') == r
    assert '/dev/mapper/vg_lxcrhel6sat56-lv_root' in df_list.filesystems
    assert len(df_list.get_filesystem('/dev/mapper/vg_lxcrhel6sat56-lv_root')) == 1
    assert df_list.get_filesystem('/dev/mapper/vg_lxcrhel6sat56-lv_root')[0] == r
    assert len(df_list.get_filesystem('tmpfs')) == 3
    assert df_list.get_mount('/sys').filesystem == 'sysfs'
    assert df_list.get_mount('/proc').total == '0'
    assert df_list.get_mount('/dev').used == '0'
    assert df_list.get_mount('/run').available == '5997356'
    assert df_list.get_mount('/sys/fs/cgroup').capacity == '0%'
    assert df_list.get_mount('/').filesystem == '/dev/mapper/vg_lxcrhel6sat56-lv_root'
    assert df_list.get_mount('/').capacity == '5%'

    # Test get_path
    # Root mount point works:
    assert df_list.get_dir('/') == df_list.get_mount('/')
    # Mount point underneath root works:
    assert df_list.get_dir('/dev') == df_list.get_mount('/dev')
    # Directory underneath sub-mount:
    assert df_list.get_dir('/dev/v4l') == df_list.get_mount('/dev')
    # Directory with / suffix:
    assert df_list.get_dir('/dev/v4l/') == df_list.get_mount('/dev')
    # File path also works:
    assert df_list.get_dir('/dev/v4l/adapter0/control0.cfg') == df_list.get_mount('/dev')
    # Relative path returns None
    assert df_list.get_dir('dev/sys') is None
    # Invalid path returns None
    assert df_list.get_dir('"') is None


DF_AL = """
Filesystem                             1K-blocks      Used Available     Use% Mounted on
/dev/mapper/vg_lxcrhel6sat56-lv_root    98571884   4244032  89313940       5% /
sysfs                                          0         0         0        - /sys
proc                                           0         0         0        - /proc
devtmpfs                                 5988480         0   5988480       0% /dev
securityfs                                     0         0         0        - /sys/kernel/security

tmpfs                                    5998736    491660   5507076       9% /dev/shm
devpts                                         0         0         0        - /dev/pts
tmpfs                                    5998736      1380   5997356       1% /run
tmpfs                                    5998736         0   5998736       0% /sys/fs/cgroup
""".strip()


def test_df_al():
    df_list = df.DiskFree_AL(context_wrap(DF_AL))
    assert len(df_list) == 9
    assert len(df_list.mounts) == 9
    assert len(df_list.filesystems) == 7
    assert '/' in df_list.mounts
    r = df.Record(
        filesystem='/dev/mapper/vg_lxcrhel6sat56-lv_root',
        total='98571884',
        used='4244032',
        available='89313940',
        capacity='5%',
        mounted_on='/'
    )
    assert df_list.get_mount('/') == r
    assert '/dev/mapper/vg_lxcrhel6sat56-lv_root' in df_list.filesystems
    assert len(df_list.get_filesystem('/dev/mapper/vg_lxcrhel6sat56-lv_root')) == 1
    assert df_list.get_filesystem('/dev/mapper/vg_lxcrhel6sat56-lv_root')[0] == r
    assert len(df_list.get_filesystem('tmpfs')) == 3
    assert df_list.get_mount('/sys').filesystem == 'sysfs'
    assert df_list.get_mount('/proc').total == '0'
    assert df_list.get_mount('/dev').used == '0'
    assert df_list.get_mount('/run').available == '5997356'
    assert df_list.get_mount('/sys/fs/cgroup').capacity == '0%'
    assert df_list.get_mount('/').filesystem == '/dev/mapper/vg_lxcrhel6sat56-lv_root'
    assert df_list.get_mount('/').capacity == '5%'

    # Test get_path
    # Root mount point works:
    assert df_list.get_dir('/') == df_list.get_mount('/')
    # Mount point underneath root works:
    assert df_list.get_dir('/dev') == df_list.get_mount('/dev')
    # Directory underneath sub-mount:
    assert df_list.get_dir('/dev/v4l') == df_list.get_mount('/dev')
    # Directory with / suffix:
    assert df_list.get_dir('/dev/v4l/') == df_list.get_mount('/dev')
    # File path also works:
    assert df_list.get_dir('/dev/v4l/adapter0/control0.cfg') == df_list.get_mount('/dev')
    # Relative path returns None
    assert df_list.get_dir('dev/sys') is None
    # Invalid path returns None
    assert df_list.get_dir('"') is None


DF_AL_BAD = """
Filesystem                             1K-blocks      Used Available     Use% Mounted on
/dev/mapper/vg_lxcrhel6sat56-lv_root    98571884   4244032  89313940       5% /
sysfs                                          0
"""

DF_AL_BAD_BS = """
Filesystem                             1a-blocks      Used Available     Use% Mounted on
/dev/mapper/vg_lxcrhel6sat56-lv_root    98571884   4244032  89313940       5% /
"""


def test_df_al_bad():
    with pytest.raises(ParseException) as exc:
        df_list = df.DiskFree_AL(context_wrap(DF_AL_BAD))
        assert len(df_list) == 2
    assert 'Could not parse line' in str(exc)

    with pytest.raises(ParseException) as exc:
        df.DiskFree_AL(context_wrap(DF_AL_BAD_BS))
    assert 'Unknown block size' in str(exc)


DF_AL_BS_2MB = """
Filesystem     2MB-blocks  Used Available Use% Mounted on
/dev/vda3           62031 49197      9680  84% /
"""


def test_df_al_2MB():
    df_list = df.DiskFree_LI(context_wrap(DF_AL_BS_2MB))
    root = df_list.get_mount('/')
    assert root.filesystem == '/dev/vda3'
    assert root.total == '62031'
    assert df_list.raw_block_size == '2MB'
    assert df_list.block_size == 2000000
    assert int(root.total) * df_list.block_size == 124062000000  # To Bytes


DF_LI_DOC = """
Filesystem       Inodes IUsed    IFree IUse% Mounted on
devtmpfs         242224   359   241865    1% /dev
tmpfs            246028     1   246027    1% /dev/shm
tmpfs            246028   491   245537    1% /run
tmpfs            246028    17   246011    1% /sys/fs/cgroup
/dev/sda2       8911872 58130  8853742    1% /
/dev/sdb1      26213888 19662 26194226    1% /opt/data
/dev/sda1        524288   306   523982    1% /boot
tmpfs            246028     5   246023    1% /run/user/0
""".strip()

DF_ALP_DOC = """
Filesystem     1024-blocks    Used Available Capacity Mounted on
sysfs                    0       0         0        - /sys
proc                     0       0         0        - /proc
devtmpfs            968896       0    968896       0% /dev
securityfs               0       0         0        - /sys/kernel/security
tmpfs               984112       0    984112       0% /dev/shm
devpts                   0       0         0        - /dev/pts
tmpfs               984112    8660    975452       1% /run
tmpfs               984112       0    984112       0% /sys/fs/cgroup
cgroup                   0       0         0        - /sys/fs/cgroup/systemd
cgroup                   0       0         0        - /sys/fs/cgroup/pids
cgroup                   0       0         0        - /sys/fs/cgroup/rdma
configfs                 0       0         0        - /sys/kernel/config
/dev/sda2         17813504 2127172  15686332      12% /
selinuxfs                0       0         0        - /sys/fs/selinux
systemd-1                -       -         -        - /proc/sys/fs/binfmt_misc
debugfs                  0       0         0        - /sys/kernel/debug
mqueue                   0       0         0        - /dev/mqueue
hugetlbfs                0       0         0        - /dev/hugepages
/dev/sdb1         52402180 1088148  51314032       3% /V M T o o l s
/dev/sda1          1038336  185676    852660      18% /boot
""".strip()

DF_AL_DOC = """
Filesystem     1K-blocks    Used Available Use% Mounted on
sysfs                  0       0         0    - /sys
proc                   0       0         0    - /proc
devtmpfs          968896       0    968896   0% /dev
securityfs             0       0         0    - /sys/kernel/security
tmpfs             984112       0    984112   0% /dev/shm
devpts                 0       0         0    - /dev/pts
tmpfs             984112    8660    975452   1% /run
tmpfs             984112       0    984112   0% /sys/fs/cgroup
cgroup                 0       0         0    - /sys/fs/cgroup/systemd
cgroup                 0       0         0    - /sys/fs/cgroup/pids
cgroup                 0       0         0    - /sys/fs/cgroup/rdma
configfs               0       0         0    - /sys/kernel/config
/dev/sda2       17813504 2127172  15686332  12% /
selinuxfs              0       0         0    - /sys/fs/selinux
systemd-1              -       -         -    - /proc/sys/fs/binfmt_misc
debugfs                0       0         0    - /sys/kernel/debug
mqueue                 0       0         0    - /dev/mqueue
hugetlbfs              0       0         0    - /dev/hugepages
/dev/sdb1       52402180 1088148  51314032   3% /V M T o o l s
/dev/sda1        1038336  185676    852660  18% /boot
""".strip()


def test_doc_examples():
    env = {
            'df_li': df.DiskFree_LI(context_wrap(DF_LI_DOC)),
            'df_al': df.DiskFree_AL(context_wrap(DF_AL_DOC)),
            'df_alP': df.DiskFree_ALP(context_wrap(DF_ALP_DOC)),
          }
    failed, total = doctest.testmod(df, globs=env)
    assert failed == 0
