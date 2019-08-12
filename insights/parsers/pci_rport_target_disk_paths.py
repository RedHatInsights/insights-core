"""
PCIRportTargetDiskPath
======================

Module for parsing the output of command ``find /sys/devices/pci0000:00 -mindepth 8 -maxdepth 8``.
"""

from insights.parsers import ParseException, SkipException
from insights import parser, CommandParser
from insights.specs import Specs


@parser(Specs.pci_rport_target_disk_paths)
class PCIRportTargetDiskPaths(CommandParser):
    """
    Class for parsing ``find /sys/devices/pci0000:00 -mindepth 8 -maxdepth 8`` command output.

    Typical output of command ``find /sys/devices/pci0000:00 -mindepth 8 -maxdepth 8`` with
    the filter of 'block' looks like::

        /sys/devices/pci0000:00/0000:00:01.0/0000:04:00.6/host1/rport-1:0-1/target1:0:0/1:0:0:0/block/sdb
        /sys/devices/pci0000:00/0000:00:01.0/0000:04:00.7/host2/rport-2:0-2/target2:0:0/2:0:0:0/block/sdc
        /sys/devices/pci0000:00/0000:00:02.2/0000:02:00.0/host0/target0:1:0/0:1:0:0/block/sda/dev
        /sys/devices/pci0000:00/0000:00:02.2/0000:02:00.0/host0/target0:1:0/0:1:0:0/block/sda/sda1
        /sys/devices/pci0000:00/0000:00:02.2/0000:02:00.0/host0/target0:1:0/0:1:0:0/block/sda/sda2

    The Original data parsed looks like::

        [
               {
                   'target': 'target1:0:0',
                   'devnode': 'sdb',
                   'host_channel_id_lun': '1:0:0:0',
                   'pci_id': '0000:04:00.6',
                   'host': 'host1',
                   'rport': 'rport-1:0-1'
               },
               {
                   'target': 'target2:0:0',
                   'devnode': 'sdc',
                   'host_channel_id_lun': '2:0:0:0',
                   'pci_id': '0000: 04:00.7',
                   'host': 'host2',
                   'rport': 'rport-2:0-2'
               },
               {
                   'target': 'target0:1:0',
                   'devnode': 'sda',
                   'host_channel_id_lun': '0:1:0:0',
                   'pci_id': '0000: 02:00.0',
                   'host': 'host0',
                   'rport': 'rport-2:0-2'
               }
        ]

    Examples:
        >>> type(pd)
        <class 'insights.parsers.pci_rport_target_disk_paths.PCIRportTargetDiskPaths'>
        >>> pd.pci_id()
        ['0000:02:00.0', '0000:04:00.6', '0000:04:00.7']
        >>> pd.host()
        ['host0', 'host1', 'host2']
        >>> pd.target()
        ['target0:1:0', 'target1:0:0', 'target2:0:0']
        >>> pd.host_channel_id_lun()
        ['0:1:0:0', '1:0:0:0', '2:0:0:0']
        >>> pd.devnode()
        ['sda', 'sdb', 'sdc']

    Raises:
        ParseException: Input content is not available to parse
        SkipException: Input content is empty

    Attributes:
        path_list (list): the result parsed

    """

    @property
    def pci_id(self):
        """
        The all pci_id(s) from parsed content.

        Returns:
            list: pci id
        """
        return self.__pci_id_attributes

    @property
    def devnode(self):
        """
        The all devicenode(s) from parsed content.

        Returns:
            list: device nodes
        """
        return self.__devnode_attributes

    @property
    def host(self):
        """
        The all host(s) from parsed content.

        Returns:
            list: hosts
        """
        return self.__host_attributes

    @property
    def rport(self):
        """
        The all rport(s) from parsed content.

        Returns:
            list: rports
        """
        return self.__rport_attributes

    @property
    def target(self):
        """
        The all rport(s) from parsed content.

        Returns:
            list: rports
        """
        return self.__target_attributes

    @property
    def host_channel_id_lun(self):
        """
        The all host_channel_id_lun(s) from parsed content

        Returns:
            list: host_channel_id_lun
        """
        return self.__host_channel_id_lun_attributes

    def parse_content(self, content):
        EMPTY = "Input content is empty"
        BADWD = "No useful data parsed in line: '{0}'"

        if not content:
            raise SkipException(EMPTY)

        pci = []
        self.__host_attributes = []
        self.__rport_attributes = []
        self.__target_attributes = []
        self.__pci_id_attributes = []
        self.__devnode_attributes = []
        self.__host_channel_id_lun_attributes = []

        for line in content:
            line_sp = list(filter(None, line.strip().split('/')))
            temp_pci = {}
            for i, l in enumerate(line_sp):
                rport = None
                if 'host' in l:
                    temp_pci['host'] = l
                elif 'pci' in l:
                    temp_pci['pci_id'] = line_sp[i + 2]
                elif 'rport-' in l:
                    rport = l
                elif 'target' in l:
                    temp_pci['target'] = l
                elif 'block' == l:
                    temp_pci['devnode'] = line_sp[i + 1]
                    temp_pci['host_channel_id_lun'] = line_sp[i - 1]
                temp_pci['rport'] = rport

                if len(temp_pci) == 5:
                    pci.append(temp_pci)
                else:
                    raise ParseException(BADWD.format(line))

                self.__host_attributes.append(temp_pci['host'])
                self.__rport_attributes.append(rport) if rport else None
                self.__target_attributes.append(temp_pci['target'])
                self.__pci_id_attributes.append(temp_pci['pci_id'])
                self.__devnode_attributes.append(temp_pci['devnode'])
                self.__host_channel_id_lun_attributes.append(temp_pci['host_channel_id_lun'])

        self.path_list = pci
