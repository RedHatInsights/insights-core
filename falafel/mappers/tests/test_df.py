""""
``test df``
================
"""

from falafel.mappers import df
from falafel.core.context import Context

DF_LI_DATA = ['Filesystem        Inodes  IUsed     IFree IUse% Mounted on',
              '/dev/mapper/vg_lxcrhel6sat56-lv_root',
              '                 6275072 124955   6150117    2% /',
              'devtmpfs         1497120    532   1496588    1% /dev',
              'tmpfs            1499684    331   1499353    1% /dev/shm',
              'tmpfs            1499684    728   1498956    1% /run',
              'tmpfs            1499684     16   1499668    1% /sys/fs/cgroup',
              '/dev/sda3       15728640 180293  15548347    2% /',
              'tmpfs            1499684     54   1499630    1% /tmp',
              '/dev/sda2      106954752 298662 106656090    1% /home',
              '/dev/sda1         128016    429    127587    1% /boot',
              'tmpfs            1499684      6   1499678    1% /run/user/988',
              'tmpfs            1499684     15   1499669    1% /run/user/100']


def test_df_li():
    context = Context(content=DF_LI_DATA)
    results = df.df_li(context)
    assert results is not None
    assert len(results) == 11
    lv_root = None
    sda2 = None
    for result in results:
        if result['Filesystem'] == '/dev/mapper/vg_lxcrhel6sat56-lv_root':
            lv_root = result
        elif result['Filesystem'] == '/dev/sda2':
            sda2 = result
    assert lv_root is not None
    assert len(lv_root) == 6
    assert lv_root['Inodes'] == "6275072"
    assert lv_root['IUsed'] == "124955"
    assert lv_root['IFree'] == "6150117"
    assert lv_root['IUse%'] == "2%"
    assert lv_root['Mounted_on'] == "/"
    assert sda2 is not None
    assert len(sda2) == 6
    assert sda2['Inodes'] == "106954752"
    assert sda2['IUsed'] == "298662"
    assert sda2['IFree'] == "106656090"
    assert sda2['IUse%'] == "1%"
    assert sda2['Mounted_on'] == "/home"


DF_ALP_DATA = ['Filesystem                           1024-blocks      Used Available Capacity Mounted on',
               '/dev/mapper/vg_lxcrhel6sat56-lv_root    98571884   4244032  89313940       5% /',
               'sysfs                                          0         0         0        - /sys',
               'proc                                           0         0         0        - /proc',
               'devtmpfs                                 5988480         0   5988480       0% /dev',
               'securityfs                                     0         0         0        - /sys/kernel/security',
               'tmpfs                                    5998736    491660   5507076       9% /dev/shm',
               'devpts                                         0         0         0        - /dev/pts',
               'tmpfs                                    5998736      1380   5997356       1% /run',
               'tmpfs                                    5998736         0   5998736       0% /sys/fs/cgroup',
               'cgroup                                         0         0         0        - /sys/fs/cgroup/systemd']


def test_df_alp():
    context = Context(content=DF_ALP_DATA)
    results = df.df_alP(context)
    assert results is not None
    assert len(results) == 10
    lv_root = None
    devtmpfs = None
    for result in results:
        if result['Filesystem'] == '/dev/mapper/vg_lxcrhel6sat56-lv_root':
            lv_root = result
        elif result['Filesystem'] == 'devtmpfs':
            devtmpfs = result
    assert lv_root is not None
    assert len(lv_root) == 6
    assert lv_root['1024-blocks'] == "98571884"
    assert lv_root['Used'] == "4244032"
    assert lv_root['Available'] == "89313940"
    assert lv_root['Capacity'] == "5%"
    assert lv_root['Mounted_on'] == "/"
    assert devtmpfs is not None
    assert len(devtmpfs) == 6
    assert devtmpfs['1024-blocks'] == "5988480"
    assert devtmpfs['Used'] == "0"
    assert devtmpfs['Available'] == "5988480"
    assert devtmpfs['Capacity'] == "0%"
    assert devtmpfs['Mounted_on'] == "/dev"
