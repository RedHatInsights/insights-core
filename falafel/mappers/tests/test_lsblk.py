from falafel.mappers import lsblk
from falafel.tests import context_wrap

lsblk_content_1 = """
NAME                            MAJ:MIN RM  SIZE RO TYPE  MOUNTPOINT
sdb                               8:16   0   32G  0 disk
sda                               8:0    0   80G  0 disk
|-sda1                            8:1    0  256M  0 part  /boot
`-sda2                            8:2    0 79.8G  0 part
  |-volgrp01-root (dm-0)        253:0    0   15G  0 lvm   /
  |-volgrp01-swap (dm-1)        253:1    0    8G  0 lvm   [SWAP]
  |-volgrp01-var (dm-3)         253:3    0   20G  0 lvm   /var
  |-volgrp01-banktools (dm-4)   253:4    0   10G  0 lvm   /banktools
  |-volgrp01-data (dm-5)        253:5    0  128M  0 lvm   /data
  `-volgrp01-export_home (dm-6) 253:6    0  128M  0 lvm   /export/home
sdc                               8:32   0  8.5G  0 disk
`-mpathb (dm-2)                 253:2    0  8.5G  0 mpath
  |-testVG-LVtest (dm-7)        253:7    0    3G  0 lvm   /test-clus-fs
  |-testVG-LVtest1 (dm-8)       253:8    0    2G  0 lvm   /test-clus-fs1
  `-testVG-LVtest2 (dm-9)       253:9    0    1G  0 lvm   /test-clus-fs2
""".strip()

lsblk_content_2 = """
NAME                                        MAJ:MIN RM  SIZE RO TYPE  MOUNTPOINT
sda                                           8:0    0   50G  0 disk
`-rootdisk                                  253:1    0   50G  0 mpath
  |-rootdisk1                               253:2    0  500M  0 part  /boot
  `-rootdisk2                               253:3    0   38G  0 part
    |-rhel-root                             253:4    0   10G  0 lvm   /
    |-rhel-swap                             253:5    0    8G  0 lvm   [SWAP]
    |-rhel-home                             253:7    0   10G  0 lvm   /home
    `-rhel-var                              253:8    0   10G  0 lvm   /var
sdb                                           8:16   0  300G  0 disk
`-testdbcl                                  253:0    0  300G  0 mpath
sdc                                           8:32   0    1G  0 disk
`-qdisk                                     253:6    0    1G  0 mpath
sdd                                           8:48   0   50G  0 disk
|-rootdisk                                  253:1    0   50G  0 mpath
|  |-rootdisk1                               253:2    0  500M  0 part  /boot
|  |-rootdisk2                               253:3    0   38G  0 part
|  |  |-rhel-root                             253:4    0   10G  0 lvm   /
|  |  |-rhel-swap                             253:5    0    8G  0 lvm   [SWAP]
|  |  |-rhel-home                             253:7    0   10G  0 lvm   /home
|  |  `-rhel-var                              253:8    0   10G  0 lvm   /var
|  |-rootdisk3                               253:3    0   38G  0 part
|-datadisk                                  253:1    0   50G  0 mpath
  |-datadisk1                               253:2    0  500M  0 part  /boot
  |-datadisk2                               253:3    0   38G  0 part
sde                                           8:64   0  300G  0 disk
`-testdbcl                                  253:0    0  300G  0 mpath
sdf                                           8:80   0    1G  0 disk
`-qdisk                                     253:6    0    1G  0 mpath
sdg                                           8:96   0  100G  0 disk
`-testdbcl12                                253:9    0  100G  0 mpath
sdh                                           8:112  0  100G  0 disk
`-testdbcl12                                253:9    0  100G  0 mpath
sdi                                           8:128  0  100G  0 disk
`-testdbcl12_druga                          253:11   0  100G  0 mpath
  `-vg_testdbcl12_druga-lv_testdbcl12_druga 253:10   0  100G  0 lvm   /testdbcl12_druga
sdj                                           8:144  0  100G  0 disk
`-testdbcl12_druga                          253:11   0  100G  0 mpath
  `-vg_testdbcl12_druga-lv_testdbcl12_druga 253:10   0  100G  0 lvm   /testdbcl12_druga
sr0                                          11:0    1 1024M  0 rom
""".strip()

lsblk_output = """
NAME                            MAJ:MIN RM  SIZE RO TYPE  MOUNTPOINT
sdb                               8:16   0   32G  0 disk
sda                               8:0    0   80G  0 disk
|-sda1                            8:1    0  256M  0 part  /boot
`-sda2                            8:2    0 79.8G  0 part
  |-volgrp01-root (dm-0)        253:0    0   15G  0 lvm   /
  |-volgrp01-swap (dm-1)        253:1    0    8G  0 lvm   [SWAP]
  |-volgrp01-var (dm-3)         253:3    0   20G  0 lvm   /var
  |-volgrp01-banktools (dm-4)   253:4    0   10G  0 lvm   /banktools
  |-volgrp01-data (dm-5)        253:5    0  128M  0 lvm   /data
  `-volgrp01-export_home (dm-6) 253:6    0  128M  0 lvm   /export/home
sdc                               8:32   0  8.5G  0 disk
`-mpathb (dm-2)                 253:2    0  8.5G  0 mpath
  |-testVG-LVtest (dm-7)        253:7    0    3G  0 lvm   /test-clus-fs
  |-testVG-LVtest1 (dm-8)       253:8    0    2G  0 lvm   /test-clus-fs1
  `-testVG-LVtest2 (dm-9)       253:9    0    1G  0 lvm   /test-clus-fs2
""".strip()


def test_get_device_info_a():
    context = context_wrap(lsblk_output)
    m_result = lsblk.get_device_info(context)
    lines = lsblk_content_1.splitlines()
    for index, item in enumerate(m_result):
        assert item.get('device') in lines[index + 1]
        assert item.get('type') in lines[index + 1]
        if item.get('device') == "mpathb":
            assert item.get('parent') == "sdc"
            assert item.get('type') == "mpath"


def test_get_device_info_1():
    context = context_wrap(lsblk_content_1)
    m_result = lsblk.get_device_info(context)
    lines = lsblk_content_1.splitlines()
    for index, item in enumerate(m_result):
        assert item.get('device') in lines[index + 1]
        assert item.get('type') in lines[index + 1]
        if item.get('mountpoint'):
            assert item.get('mountpoint') in lines[index + 1]
        if item.get('device') == "testVG-LVtest":
            assert item.get('parent') == "mpathb"
        if item.get('device') == "volgrp01-export_home":
            assert item.get('parent') == "sda2"


def test_get_device_info_2():
    context = context_wrap(lsblk_content_2)
    m_result = lsblk.get_device_info(context)
    lines = lsblk_content_2.splitlines()
    for index, item in enumerate(m_result):
        assert item.get('device') in lines[index + 1]
        assert item.get('type') in lines[index + 1]
        if item.get('mountpoint'):
            assert item.get('mountpoint') in lines[index + 1]
        if item.get('device') == "rhel-home":
            assert item.get('parent') == "rootdisk2"
        if item.get('device') == "vg_testdbcl12_druga-lv_testdbcl12_druga":
            assert item.get('parent') == "testdbcl12_druga"
