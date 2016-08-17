from falafel.mappers import df
from falafel.tests import context_wrap

DF_ALP = """
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


def test_df_li():
    df_list = df.DiskFree_LI.parse_context(context_wrap(DF_LI))
    assert len(df_list) == 10
    assert len(df_list.mounts) == 10
    assert len(df_list.filesystems) == 5
    assert '/home' in df_list.mount_names
    assert df_list.get_mount('/home') == {
        'Filesystem': '/dev/sda2',
        'Inodes': '106954752',
        'IUsed': '298662',
        'IFree': '106656090',
        'IUse%': '1%',
        'Mounted_on': '/home'
    }
    assert '/dev/sda2' in df_list.filesystem_names
    assert len(df_list.get_filesystem('/dev/sda2')) == 1
    assert df_list.get_filesystem('/dev/sda2')[0] == {
        'Filesystem': '/dev/sda2',
        'Inodes': '106954752',
        'IUsed': '298662',
        'IFree': '106656090',
        'IUse%': '1%',
        'Mounted_on': '/home'
    }
    assert len(df_list.get_filesystem('tmpfs')) == 6
    assert df_list.get_mount('/dev').Filesystem == 'devtmpfs'
    assert df_list.get_mount('/run').Inodes == '1499684'
    assert df_list.get_mount('/tmp').IUsed == '54'
    assert df_list.get_mount('/boot').IFree == '127587'
    assert df_list.get_filesystem('/dev/sda2')[0].get('IUse%') == '1%'
    assert df_list.get_filesystem('/dev/sda2')[0].IFree == '106656090'
    assert df_list.get_filesystem('devtmpfs')[0].Mounted_on == '/dev'
    assert df_list.get_mount('/V M T o o l s').IFree == '1499678'
    assert df_list.get_filesystem('/dev/mapper/vg_lxcrhel6sat56-lv_root')[0].Mounted_on == '/'


def test_df_alP():
    df_list = df.DiskFree_ALP.parse_context(context_wrap(DF_ALP))
    assert len(df_list) == 9
    assert len(df_list.mounts) == 9
    assert len(df_list.filesystems) == 7
    assert '/' in df_list.mount_names
    assert df_list.get_mount('/') == {
        'Filesystem': '/dev/mapper/vg_lxcrhel6sat56-lv_root',
        '1024-blocks': '98571884',
        'Used': '4244032',
        'Available': '89313940',
        'Capacity': '5%',
        'Mounted_on': '/'
    }
    assert '/dev/mapper/vg_lxcrhel6sat56-lv_root' in df_list.filesystem_names
    assert len(df_list.get_filesystem('/dev/mapper/vg_lxcrhel6sat56-lv_root')) == 1
    assert df_list.get_filesystem('/dev/mapper/vg_lxcrhel6sat56-lv_root')[0] == {
        'Filesystem': '/dev/mapper/vg_lxcrhel6sat56-lv_root',
        '1024-blocks': '98571884',
        'Used': '4244032',
        'Available': '89313940',
        'Capacity': '5%',
        'Mounted_on': '/'
    }
    assert len(df_list.get_filesystem('tmpfs')) == 3
    assert df_list.get_mount('/sys').Filesystem == 'sysfs'
    assert df_list.get_mount('/proc').get('1024-blocks') == '0'
    assert df_list.get_mount('/dev').Used == '0'
    assert df_list.get_mount('/run').Available == '5997356'
    assert df_list.get_mount('/sys/fs/cgroup').Capacity == '0%'
    assert df_list.get_mount('/').Filesystem == '/dev/mapper/vg_lxcrhel6sat56-lv_root'
    assert df_list.get_mount('/').Capacity == '5%'


def test_df_al():
    df_list = df.DiskFree_AL.parse_context(context_wrap(DF_AL))
    assert len(df_list) == 9
    assert len(df_list.mounts) == 9
    assert len(df_list.filesystems) == 7
    assert '/' in df_list.mount_names
    assert df_list.get_mount('/') == {
        'Filesystem': '/dev/mapper/vg_lxcrhel6sat56-lv_root',
        '1K-blocks': '98571884',
        'Used': '4244032',
        'Available': '89313940',
        'Use%': '5%',
        'Mounted_on': '/'
    }
    assert '/dev/mapper/vg_lxcrhel6sat56-lv_root' in df_list.filesystem_names
    assert len(df_list.get_filesystem('/dev/mapper/vg_lxcrhel6sat56-lv_root')) == 1
    assert df_list.get_filesystem('/dev/mapper/vg_lxcrhel6sat56-lv_root')[0] == {
        'Filesystem': '/dev/mapper/vg_lxcrhel6sat56-lv_root',
        '1K-blocks': '98571884',
        'Used': '4244032',
        'Available': '89313940',
        'Use%': '5%',
        'Mounted_on': '/'
    }
    assert len(df_list.get_filesystem('tmpfs')) == 3
    assert df_list.get_mount('/sys').Filesystem == 'sysfs'
    assert df_list.get_mount('/proc').get('1K-blocks') == '0'
    assert df_list.get_mount('/dev').Used == '0'
    assert df_list.get_mount('/run').Available == '5997356'
    assert df_list.get_mount('/sys/fs/cgroup').get('Use%') == '0%'
    assert df_list.get_mount('/').Filesystem == '/dev/mapper/vg_lxcrhel6sat56-lv_root'
    assert df_list.get_mount('/').get('Use%') == '5%'
