""""
``test fstab``
================
"""
from insights.parsers import fstab
from insights.tests import context_wrap

FS_TAB_DATA = ['#',
               '# /etc/fstab',
               '# Created by anaconda on Fri May  6 19:51:54 2016',
               '#',
               '/dev/mapper/rhel_hadoop--test--1-root /                       xfs     defaults        0 0',
               'UUID=2c839365-37c7-4bd5-ac47-040fba761735 /boot               xfs     defaults        0 0',
               '/dev/mapper/rhel_hadoop--test--1-home /home                   xfs     defaults        0 0',
               '/dev/mapper/rhel_hadoop--test--1-swap swap                    swap    defaults        0 0',
               ' ',
               '/dev/sdb1 /hdfs/data1 xfs rw,relatime,seclabel,attr2,inode64,noquota 0 0',
               '/dev/sdc1 /hdfs/data2 xfs rw,relatime,seclabel,attr2,inode64,noquota 0 0',
               '/dev/sdd1 /hdfs/data3 xfs rw,relatime,seclabel,attr2,inode64,noquota 0 0',
               'localhost:/ /mnt/hdfs nfs rw,vers=3,proto=tcp,nolock,timeo=600 0 0',
               ' ',
               '/dev/mapper/vg0-lv2 /test1             ext4 defaults,data=writeback     1 1',
               'nfs_hostname.example.com:/nfs_share/data     /srv/rdu/data/000  nfs     ro,defaults,hard,intr,bg,noatime,nodev,nosuid,nfsvers=3,tcp,rsize=32768,wsize=32768     0']

content_fstab_without_mntopts = """
#
# /etc/fstab
# Created by anaconda on Mon Dec  5 14:53:47 2016
#
# Accessible filesystems, by reference, are maintained under '/dev/disk'
# See man pages fstab(5), findfs(8), mount(8) and/or blkid(8) for more info
#
/dev/mapper/vg_osbase-lv_root /                       ext4    defaults        1 1
UUID=05ce4fc3-04c3-4111-xxxx /boot                   ext4    defaults        1 2
/dev/mapper/vg_osbase-lv_home /home                   ext4    defaults        1 2
/dev/mapper/vg_osbase-lv_tmp /tmp                    ext4    defaults        1 2

## default mount options##
/dev/foo /foo somefs
###SIMBOX MOUNT###
192.168.48.65:/cellSiteData /ceSiteData nfs
    /dev/vg_data/lv_pg /var/opt/rh/rh-postgresql95/lib/pgsql  xfs rw,noatime        0        0
"""


def test_fstab():
    context = context_wrap(FS_TAB_DATA)
    results = fstab.FSTab(context)
    assert results is not None
    assert len(results) == 10
    sdb1 = None
    nfs_host = None

    for result in results:
        if result.fs_spec == "/dev/sdb1":
            sdb1 = result
        elif result.fs_spec.startswith("nfs_hostname.example.com:"):
            nfs_host = result
        elif result.fs_spec.startswith("/dev/mapper/vg0"):
            dev_vg0 = result
    assert sdb1 is not None
    assert sdb1.fs_file == "/hdfs/data1"
    assert sdb1.fs_vfstype == "xfs"
    assert sdb1.fs_mntops.rw
    assert sdb1.fs_mntops.relatime
    assert 'noquota' in sdb1.fs_mntops
    assert sdb1.fs_freq == 0
    assert sdb1.fs_passno == 0
    assert sdb1.raw == '/dev/sdb1 /hdfs/data1 xfs rw,relatime,seclabel,attr2,inode64,noquota 0 0'
    assert nfs_host is not None
    assert nfs_host.fs_spec == "nfs_hostname.example.com:/nfs_share/data"
    assert nfs_host.fs_file == "/srv/rdu/data/000"
    assert nfs_host.fs_vfstype == "nfs"
    assert nfs_host.fs_mntops.ro
    assert nfs_host.fs_mntops.hard
    assert 'bg' in nfs_host.fs_mntops
    assert nfs_host.fs_mntops.rsize == "32768"
    assert nfs_host.fs_freq == 0
    assert nfs_host.fs_passno == 0
    assert dev_vg0.fs_mntops.data == 'writeback'
    assert dev_vg0.raw == '/dev/mapper/vg0-lv2 /test1             ext4 defaults,data=writeback     1 1'
    for opt, v in dev_vg0.fs_mntops.items():
        if opt.startswith('data'):
            assert v == 'writeback'

    assert results.mounted_on['/hdfs/data1'] == sdb1
    assert results.mounted_on['/srv/rdu/data/000'] == nfs_host

    # Test keyword searches - from examples
    assert results.search(fs_file='/') == [l for l in results if l.fs_file == '/']
    assert results.search(fs_spec__startswith='LABEL=') == [l for l in results if l.fs_spec.startswith('LABEL')]
    assert results.search(fs_mntops__contains='uid') == [l for l in results if 'uid' in l.fs_mntops]
    assert results.search(fs_vfstype='xfs', fs_mntops__contains='relatime') == [l for l in results if l.fs_vfstype == 'xfs' and 'relatime' in l.fs_mntops]

    results = fstab.FSTab(context_wrap(content_fstab_without_mntopts))
    sitedata_mount_list = [result for result in results if result.fs_file == "/ceSiteData"]
    assert len(sitedata_mount_list) == 1
    sitedata_mount = sitedata_mount_list[0]
    assert sitedata_mount.fs_mntops['defaults'] is True
    assert sitedata_mount.fs_vfstype == "nfs"
    assert sitedata_mount.fs_spec == "192.168.48.65:/cellSiteData"


FSTAB_WITH_BLANK_IN_PATH = [
    r'/dev/sda2                    /                          ext4    1 1  # work',
    r'/dev/sdb3                    /var/crash                 ext4    defaults        1 1',
    r'/dev/sdb5                    /l\040ok/at                ext4    defaults        1 1',
    r'/dev/sdb7                    /sdb7ok/at                 ext4    defaults',
    r'/dev/sdba                    /sdbal\040ok/ab\040ta      ext4,a,b    defaults,c,d        1 1',
]


def test_fstab_with_blank_in_path():
    fstab_info = fstab.FSTab(context_wrap(FSTAB_WITH_BLANK_IN_PATH))
    assert ([l.fs_file for l in fstab_info.search(fs_file__contains='ok')] ==
            ['/l ok/at', '/sdb7ok/at', '/sdbal ok/ab ta'])


FSTAB_DEVICE_PATH_TEST_INFO = [
    r'/dev/sda2                    /                          ext4    defaults        1 1',
    r'/dev/sdb2                    /var                       ext4    defaults        1 1',
    r'/dev/sdb3                    /var/crash                 ext4    defaults        1 1',
    r'/dev/sdb4                    /abc/def                   ext4    defaults        1 1',
    r'/dev/mapper/VolGroup-lv_usr  /usr                       ext4    defaults        1 1',
    r'UUID=qX0bSg-p8CN-cWER-i8qY-cETN-jiZL-LDt93V /kdump                   ext4    defaults        1 2',
    r'/dev/mapper/VolGroup-lv_swap swap                    swap    defaults        0 0',
    r'proc                    /proc                   proc    defaults        0 0',
    r'/dev/mapper/vgext-lv--test      /lv_test        ext3    defaults        0       0',
    r'/dev/sdb5                    /l\040ok/at                ext4    defaults        1 1',
]


def test_fsspec_of_path():
    fstab_info = fstab.FSTab(context_wrap(FSTAB_DEVICE_PATH_TEST_INFO))
    path_device_map = {'/var/crash': '/dev/sdb3',
                       '/var/some/path': '/dev/sdb2',
                       '/var/crash_xxx': '/dev/sdb2',
                       '/kdump/crash': 'UUID=qX0bSg-p8CN-cWER-i8qY-cETN-jiZL-LDt93V',
                       '/some/path': '/dev/sda2',
                       '/lv_test': '/dev/mapper/vgext-lv--test',
                       '/lv': '/dev/sda2',
                       '/': '/dev/sda2',
                       'error': None,
                       '/abc': '/dev/sda2',
                       '/abc/xxx': '/dev/sda2',
                       '/tmp/vm tools': '/dev/sda2',
                       '/l ok/at/you': '/dev/sdb5',
                       '/l ok': '/dev/sda2',  # dict treat '/l\040ok' same as '/l ok'
                       r'/l\040ok': '/dev/sda2',
                       }
    for path, dev in path_device_map.items():
        assert dev == fstab_info.fsspec_of_path(path)
