from insights.parsers import df, ParseException
from insights.tests import context_wrap

import pytest

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
tmpfs            1499684      6   1499678    1% /V M T o o l s
tmpfs            1499684     15   1499669    1% /VM Tools
""".strip()


def test_df_li():
    df_list = df.DiskFree_LI(context_wrap(DF_LI))
    assert len(df_list) == 10
    assert len(df_list.mounts) == 10
    assert len(df_list.filesystems) == 5
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
    assert len(df_list.get_filesystem('tmpfs')) == 6
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
        '/dev/sda2', '/dev/sda1'
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


def test_df_al_bad():
    with pytest.raises(ParseException) as exc:
        df_list = df.DiskFree_AL(context_wrap(DF_AL_BAD))
        assert len(df_list) == 2
    assert 'Could not parse line' in str(exc)
