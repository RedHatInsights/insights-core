"""
ZiplConf - configuration file for zipl
======================================

A parser file for parsing and extracting data from ``/etc/zipl.conf`` file.

Sample input::

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

This module contains one parser:

ZiplConf - file ``/etc/zipl.conf``
----------------------------------

Examples:
    >>> zipl_info['linux']['image']
    '/boot/vmlinuz-3.10.0-693.el7.s390x'
    >>> zipl_info.images
    {'linux':'/boot/vmlinuz-3.10.0-693.el7.s390x','linux-0-rescue-a27932c8d57248e390cee3798bbd3709':'/boot/vmlinuz-0-rescue-a27932c8d57248e390cee3798bbd3709'}
    >>> zipl_info.dumptofses
    {'dumpscsi':'/dev/sda2'}
    >>> zipl_info[':menu1']['1']
    'linux'
    >>> 'defaultauto' in zipl_info['global']
    True
    >>> zipl_info['global']['defaultauto']
    None
"""
from insights.core import LegacyItemAccess, Parser
from insights.core.exceptions import ParseException
from insights.core.plugins import parser
from insights.parsers import get_active_lines
from insights.specs import Specs


@parser(Specs.zipl_conf)
class ZiplConf(LegacyItemAccess, Parser):
    """
    The zipl.conf file basically contains key-value pairs or single command based on the line.
    Section name is quoted with '[]' and menu name is started with ':'.

    Raises:
        ParseException: when the first active line is not a section
    """
    def __init__(self, *args, **kwargs):
        self._images = {}
        self._dumptofses = {}
        super(ZiplConf, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        self.data = {}
        lines = get_active_lines(content)
        line0 = lines[0]
        if line0.startswith('[') and line0.endswith(']'):
            current = line0[1:-1]
            self.data[current] = {}
            for line in lines[1:]:
                if line.startswith('[') and line.endswith(']'):
                    current = line[1:-1]
                    self.data[current] = {}
                elif line.startswith(':'):
                    current = line
                    self.data[current] = {}
                else:
                    if '=' in line:
                        k, v = [s.strip() for s in line.split('=', 1)]
                        if k == "image":
                            self._images[current] = v
                        elif k == "dumptofs":
                            self._dumptofses[current] = v
                        self.data[current][k] = v
                    else:
                        self.data[current][line] = True
        else:
            raise ParseException('Invalid zipl configuration file is found.')

    @property
    def images(self):
        """
        Get all `image` items referenced in zipl configuration file

        Returns:
            (dict): Returns a dict of the `section` and `image` names referenced
                    in zipl configuration file
        """
        return self._images

    @property
    def dumptofses(self):
        """
        Get all `dumptofs` items referenced in zipl configuration file

        Returns:
            (dict): Returns a dict of the `section` and `dumptofs` names referenced
                    in zipl configuration file
        """
        return self._dumptofses
