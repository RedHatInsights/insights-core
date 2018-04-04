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
    for opt, v in dev_vg0.fs_mntops:
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
