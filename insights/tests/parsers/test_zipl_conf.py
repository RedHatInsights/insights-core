from insights.parsers.zipl_conf import ZiplConf
from insights.tests import context_wrap
from insights.parsers import ParseException
import pytest

ZIPL_CONF = """
[defaultboot]
defaultauto
prompt=1
timeout=5
default=linux
target=/boot
[linux]
    image=/boot/vmlinuz-3.10.0-693.el7.s390x
    ramdisk=/boot/initramfs-3.10.0-693.el7.s390x.img
    parameters="root=/dev/mapper/rhel_gss5-root crashkernel=auto rd.dasd=0.0.0100 rd.dasd=0.0.0101 rd.dasd=0.0.0102 rd.lvm.lv=rhel_gss5/root rd.lvm.lv=rhel_gss5/swap net.ifnames=0 rd.znet=qeth,0.0.0600,0.0.0601,0.0.0602,layer2=0,portname=gss5,portno=0 LANG=en_US.UTF-8"
[linux-0-rescue-a27932c8d57248e390cee3798bbd3709]
    image=/boot/vmlinuz-0-rescue-a27932c8d57248e390cee3798bbd3709
    ramdisk=/boot/initramfs-0-rescue-a27932c8d57248e390cee3798bbd3709.img
    parameters="root=/dev/mapper/rhel_gss5-root crashkernel=auto rd.dasd=0.0.0100 rd.dasd=0.0.0101 rd.dasd=0.0.0102 rd.lvm.lv=rhel_gss5/root rd.lvm.lv=rhel_gss5/swap net.ifnames=0 rd.znet=qeth,0.0.0600,0.0.0601,0.0.0602,layer2=0,portname=gss5,portno=0"
[other]
    image=/boot/vmlinuz
    ramdisk=/boot/initramfs.img
    parameters="root=/dev/mapper/rhel_gss5-root crashkernel=auto rd.dasd=0.0.0100

# Configuration for dumping to SCSI disk
# Separate IPL and dump partitions
[dumpscsi]
target=/boot
dumptofs=/dev/sda2
parameters="dump_dir=/mydumps dump_compress=none dump_mode=auto"

# Menu containing two DASD boot configurations
:menu1
1=linux
2=linux-0-rescue-a27932c8d57248e390cee3798bbd3709
default=1
prompt=1
timeout=30
""".strip()

ZIPL_CONF_INVALID = """
prompt=1
timeout=5
default=linux
[linux]
    image=/boot/vmlinuz-3.10.0-693.el7.s390x
    ramdisk=/boot/initramfs-3.10.0-693.el7.s390x.img
    parameters="root=/dev/mapper/rhel_gss5-root crashkernel=auto rd.dasd=0.0.0100 rd.dasd=0.0.0101 rd.dasd=0.0.0102 rd.lvm.lv=rhel_gss5/root rd.lvm.lv=rhel_gss5/swap net.ifnames=0 rd.znet=qeth,0.0.0600,0.0.0601,0.0.0602,layer2=0,portname=gss5,portno=0 LANG=en_US.UTF-8"
""".strip()


def test_zipl_conf():
    res = ZiplConf(context_wrap(ZIPL_CONF))
    assert res.get('linux').get('image') == "/boot/vmlinuz-3.10.0-693.el7.s390x"
    assert res['linux']['image'] == "/boot/vmlinuz-3.10.0-693.el7.s390x"
    assert res[':menu1']['1'] == 'linux'
    assert 'defaultauto' in res['defaultboot']
    assert res['defaultboot']['defaultauto'] is True
    assert res['other']['parameters'] == '"root=/dev/mapper/rhel_gss5-root crashkernel=auto rd.dasd=0.0.0100'
    assert res.images == {
                            'linux': '/boot/vmlinuz-3.10.0-693.el7.s390x',
                            'linux-0-rescue-a27932c8d57248e390cee3798bbd3709': '/boot/vmlinuz-0-rescue-a27932c8d57248e390cee3798bbd3709',
                            'other': '/boot/vmlinuz'
                        }
    assert res.dumptofses == {'dumpscsi': '/dev/sda2'}


def test_zipl_conf_invalid():
    with pytest.raises(ParseException) as pe:
        ZiplConf(context_wrap(ZIPL_CONF_INVALID))
    assert "Invalid zipl configuration file is found." in str(pe)
