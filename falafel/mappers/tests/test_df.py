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


def test_df_li():
    df_list = df.df_li(context_wrap(DF_LI))
    assert len(df_list) == 10
    df_dict = {m['Mounted_on']: m for m in df_list}
    assert df_dict.get('/home') == {
        'Filesystem': '/dev/sda2',
        'Inodes': '106954752',
        'IUsed': '298662',
        'IFree': '106656090',
        'IUse%': '1%',
        'Mounted_on': '/home'
    }
    assert df_dict['/dev'].get('Filesystem') == 'devtmpfs'
    assert df_dict['/run'].get('Inodes') == '1499684'
    assert df_dict['/tmp'].get('IUsed') == '54'
    assert df_dict['/boot'].get('IFree') == '127587'
    assert df_dict['/'].get('IUse%') == '2%'
    assert df_dict['/V M T o o l s'].get('IFree') == '1499678'
    assert df_dict['/VM Tools'].get('IFree') == '1499669'
    assert df_dict['/'].get('Filesystem') == '/dev/mapper/vg_lxcrhel6sat56-lv_root'


def test_df_alP():
    df_list = df.df_alP(context_wrap(DF_ALP))
    assert len(df_list) == 9
    df_dict = {m['Mounted_on']: m for m in df_list}
    assert df_dict.get('/dev/shm') == {
        'Filesystem': 'tmpfs',
        '1024-blocks': '5998736',
        'Used': '491660',
        'Available': '5507076',
        'Capacity': '9%',
        'Mounted_on': '/dev/shm'
    }
    assert df_dict['/sys'].get('Filesystem') == 'sysfs'
    assert df_dict['/proc'].get('1024-blocks') == '0'
    assert df_dict['/dev'].get('Used') == '0'
    assert df_dict['/run'].get('Available') == '5997356'
    assert df_dict['/sys/fs/cgroup'].get('Capacity') == '0%'
    assert df_dict['/'].get('Filesystem') == '/dev/mapper/vg_lxcrhel6sat56-lv_root'
    assert df_dict['/'].get('Capacity') == '5%'
