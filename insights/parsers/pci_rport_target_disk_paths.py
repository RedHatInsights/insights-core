"""
PCIRportTargetDiskPath
======================

Module for parsing the output of command ``find /sys/devices/pci* -mindepth 8 -maxdepth 8``. 
"""

from insights import parser, CommandParser
from insights.specs import Specs
import os


@parser(Specs.pci_rport_target_disk_paths)
class PCIRportTargetDiskPaths(CommandParser, dict):
    """
    Class for parsing ``find /sys/devices/pci* -mindepth 8 -maxdepth 8`` command output. It supports
    filter of 'block' or '/block/'.

    Typical output of command ``find /sys/devices/pci* -mindepth 8 -maxdepth 8`` with filter looks like::

        /sys/devices/pci0000:00/0000:00:01.0/0000:04:00.6/host1/rport-1:0-1/target1:0:0/1:0:0:0/block/sdb
        /sys/devices/pci0000:00/0000:00:01.0/0000:04:00.7/host2/rport-2:0-2/target2:0:0/2:0:0:0/block/sdc
        /sys/devices/pci0000:00/0000:00:02.2/0000:02:00.0/host0/target0:1:0/0:1:0:0/block/sda/dev
        /sys/devices/pci0000:00/0000:00:02.2/0000:02:00.0/host0/target0:1:0/0:1:0:0/block/sda/sda1
        /sys/devices/pci0000:00/0000:00:02.2/0000:02:00.0/host0/target0:1:0/0:1:0:0/block/sda/sda2

    Examples:
        >>> type(pd)
        <class 'insights.parsers.pci_rport_target_disk_path.PCIRportTargetDiskPaths'>
        >>> pd['pci']
        ['04:00.6', '04:00.7', 02:00.0]
        >>> pd['host']
        ['host0', 'host1', 'host2']
        >>> pd['rport']
        ['rport-1:0-1', 'rport-2:0-2']
        >>> pd['target']
        ['target1:0:0', 'target2:0:0']
        >>> pd['host_channel_id_lun']
        ['1:0:0:0', '2:0:0:0']
        >>> pd['devnode']
        ['sdb', 'sdc']

    Raises:
        ParseException: When input content is not available to parse

    Attributes:
        data (list): The output of command ``find /sys/devices/pci* -mindepth 8 -maxdepth 8``
        pci_id (list): The list the pci_id involved
        devnode (list): The list of devnode
        host (list): The list of host
        rport (list): The list of rport
        target (list): The list of target
        host_channel_id_lun: The list of host_channel_id_lun
    """


    def __init__(self, *args, **kwargs):
        super(PCIRportTargetDiskPaths, self).__init__(*args, **kwargs)
        self.update(self.pdata)

    @property
    def pci_id(self):
        plist = []
        for a in self.pdata:
            if a.pci_id not in plist:
                return plist.append(a.pci_id)

    def parse_content(self, content):
        EMPTY = "Input content is empty"
        BADWD = "No useful data parsed in content: '{0}'".format(content)

        if not content:
            raise SkipException(EMPTY)

        pdata = []
        self.pdata = {'data': pdata}
        self.pci_id = []

        for line in content:
            line = line.strip()

            pci={}
            cnt = 0
            host_pos = None
            pci_id_pos = None
            rport_pos = None
            target_pos = None
            devnode_pos = None

            for l in line.split('/', 11):
                if 'host' in l:
                    host_pos = cnt
                if 'pci' in l:
                    pci_id_pos = cnt + 2
                if 'rport-' in l:
                    rport_pos = cnt
                if 'target' in l:
                    target_pos = cnt
                if 'block' == l:
                    devnode_pos = cnt + 1 
                cnt += 1

            if host_pos and pci_id_pos and target_pos and devnode_pos:     
                pci_id = line.split('/', 11)[pci_id_pos]
                host = line.split('/', 11)[host_pos]
                target = line.split('/', 11)[target_pos]
                devnode = line.split('/', 11)[devnode_pos]

                if rport_pos:
                    rport = line.split('/', 11)[rport_pos]
                else:
                    rport = ''

                if pci_id not in pci:
                    pci['pci_id'] = pci_id
                    pci['host'] = host
                    pci['rport'] = rport
                    pci['target'] = target
                    pci['devnode'] = devnode

                    if pci not in pdata:
                       pdata.append(pci)
            else:
                ParseException(BADWD)

        print(self.pdata)
