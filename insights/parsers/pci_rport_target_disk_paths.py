"""
PCIRportTargetDiskPath
======================

Module for parsing the output of command ``find /sys/devices/pci* -mindepth 8 -maxdepth 8``.
"""

from insights.parsers import ParseException, SkipException
from insights import parser, CommandParser
from insights.specs import Specs


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

    The Original data parsed looks like:
        {
            'PCI': [
                {
                    'target': 'target1: 0: 0',
                    'devnode': 'sdb',
                    'host_channel_id_lun': '1: 0: 0: 0',
                    'pci_id': '0000: 04: 00.6',
                    'host': 'host1',
                    'rport': 'rport-1: 0-1'
                },
                {
                    'target': 'target2: 0: 0',
                    'devnode': 'sdc',
                    'host_channel_id_lun': '2: 0: 0: 0',
                    'pci_id': '0000: 04: 00.7',
                    'host': 'host2',
                    'rport': 'rport-2: 0-2'
                },
                {
                    'target': 'target0: 1: 0',
                    'devnode': 'sda',
                    'host_channel_id_lun': '0: 1: 0: 0',
                    'pci_id': '0000: 02: 00.0',
                    'host': 'host0',
                    'rport': 'rport-2: 0-2'
                }
                    ]
        }


    Examples:
        >>> type(pd)
        <class 'insights.parsers.pci_rport_target_disk_paths.PCIRportTargetDiskPaths'>
        >>> pd.pci_id
        ['0000:02:00.0', '0000:04:00.6', '0000:04:00.7']
        >>> pd.host
        ['host0', 'host1', 'host2']
        >>> pd.target
        ['target0:1:0', 'target1:0:0', 'target2:0:0']
        >>> pd.host_channel_id_lun
        ['0:1:0:0', '1:0:0:0', '2:0:0:0']
        >>> pd.devnode
        ['sda', 'sdb', 'sdc']

    Raises:
        ParseException: When input content is not available to parse
        KeyError: When input key doesn't exists in dict

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

    def __attrs__(self, item):
        plist = []
        for dc in self.pdata['PCI']:
            if dc[item]:
                plist.append(dc[item])
        return sorted(plist)

    @property
    def pci_id(self):
        """
        The all pci_id(s) from parsed content.
        For example:
            ../pci0000:00/0000:00:01.0/0000:04:00.6

        Returns:
            list: pci IDs
        """
        return self.__attrs__('pci_id')

    @property
    def devnode(self):
        """
        The all devicenode(s) from parsed content.
        For example:
            ../0000:04:00.7/host2/rport-2:0-2/target2:0:0/2:0:0:0/block/sdc

        Returns:
            list: device nodes
        """
        return self.__attrs__('devnode')

    @property
    def host(self):
        """
        The all host(s) from parsed content.
        For example:
            ../0000:04:00.6/host1/

        Returns:
            list: hosts
        """
        return self.__attrs__('host')

    @property
    def rport(self):
        """
        The all rport(s) from parsed content.
        For example:
            ../0000:04:00.7/host2/rport-2:0-2

        Returns:
            list: rports
        """
        return self.__attrs__('rport')

    @property
    def target(self):
        """
        The all rport(s) from parsed content.
        For example:
            ../0000:02:00.0/host0/target0:1:0

        Returns:
            list: rports
        """

        return self.__attrs__('target')

    @property
    def host_channel_id_lun(self):
        """
        The all host_channel_id_lun(s) from parsed content
        For example:
            ../0000:04:00.7/host2/rport-2:0-2/target2:0:0/2:0:0:0

        Returns:
            list: host_channel_id_lun
        """
        return self.__attrs__('host_channel_id_lun')

    def parse_content(self, content):
        """
        Parse content of command ``find /sys/devices/pci* -mindepth 8 -maxdepth 8``

        Args:
            content (list): The output of command ``find /sys/devices/pci* -mindepth 8 -maxdepth 8``
        """

        EMPTY = "Input content is empty"
        BADWD = "No useful data parsed in content: '{0}'".format(content)

        if not content:
            raise SkipException(EMPTY)

        pdata_list = []
        self.pdata = {'PCI': pdata_list}

        for line in content:
            line = line.strip()

            pci = {}
            cnt = 0

            host_pos = None
            pci_id_pos = None
            rport_pos = None
            target_pos = None
            devnode_pos = None
            host_channel_id_lun = None

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
                    host_channel_id_lun_pos = cnt - 1
                cnt += 1

            if (host_pos and pci_id_pos and target_pos and devnode_pos and host_channel_id_lun_pos):
                pci_id = line.split('/', 11)[pci_id_pos]
                host = line.split('/', 11)[host_pos]
                target = line.split('/', 11)[target_pos]
                devnode = line.split('/', 11)[devnode_pos]
                host_channel_id_lun = line.split('/', 11)[host_channel_id_lun_pos]
                if rport_pos:
                    rport = line.split('/', 11)[rport_pos]

                if rport_pos:
                    pci['rport'] = rport
                else:
                    pci['rport'] = None

                pci['pci_id'] = pci_id
                pci['host'] = host
                pci['target'] = target
                pci['devnode'] = devnode
                pci['host_channel_id_lun'] = host_channel_id_lun

                if pci not in pdata_list:
                    pdata_list.append(pci)
            else:
                raise ParseException(BADWD)
