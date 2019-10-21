"""
PciRportTargetDiskPath
======================

Module for parsing the output of command ``find /sys/devices/ -maxdepth 10 -mindepth 9 -name stat -type f``.
"""

from insights.parsers import ParseException, SkipException
from insights import parser, CommandParser
from insights.specs import Specs


@parser(Specs.pci_rport_target_disk_paths)
class PciRportTargetDiskPaths(CommandParser):
    """
    Class for parsing ``find /sys/devices/ -maxdepth 10 -mindepth 9 -name stat -type f`` command output.

    Typical output of command ``find /sys/devices/ -maxdepth 10 -mindepth 9 -name stat -type f`` with
    the filter of 'block' looks like::

        /sys/devices/pci0000:00/0000:00:01.0/0000:04:00.6/host1/rport-1:0-1/target1:0:0/1:0:0:0/block/sdb/stat
        /sys/devices/pci0000:00/0000:00:01.0/0000:04:00.7/host2/rport-2:0-2/target2:0:0/2:0:0:0/block/sdc/stat
        /sys/devices/pci0000:00/0000:00:02.2/0000:02:00.0/host0/target0:1:0/0:1:0:0/block/sda/stat

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
                   'pci_id': '0000:04:00.7',
                   'host': 'host2',
                   'rport': 'rport-2:0-2'
               },
               {
                   'target': 'target0:1:0',
                   'devnode': 'sda',
                   'host_channel_id_lun': '0:1:0:0',
                   'pci_id': '0000:02:00.0',
                   'host': 'host0',
               }
        ]

    Examples:
        >>> type(pd)
        <class 'insights.parsers.pci_rport_target_disk_paths.PciRportTargetDiskPaths'>
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
        return sorted(self.__pci_id_attributes)

    @property
    def devnode(self):
        """
        The all devicenode(s) from parsed content.

        Returns:
            list: device nodes
        """
        return sorted(self.__devnode_attributes)

    @property
    def host(self):
        """
        The all host(s) from parsed content.

        Returns:
            list: hosts
        """
        return sorted(self.__host_attributes)

    @property
    def rport(self):
        """
        The all rport(s) from parsed content.

        Returns:
            list: rports
        """
        return sorted(self.__rport_attributes)

    @property
    def target(self):
        """
        The all target(s) from parsed content.

        Returns:
            list: targets
        """
        return sorted(self.__target_attributes)

    @property
    def host_channel_id_lun(self):
        """
        The all host_channel_id_lun(s) from parsed content

        Returns:
            list: host_channel_id_lun
        """
        return sorted(self.__host_channel_id_lun_attributes)

    def parse_content(self, content):
        EMPTY = "Input content is empty"
        BADWD = "No useful data parsed in line: '{0}'"
        KEY_MAP = [
                # key,          required chars,   relative index
                {'key': 'host', 'chars': 'host', 'idx': 0},
                {'key': 'pci_id', 'chars': 'pci', 'idx': 2},
                {'key': 'rport', 'chars': 'rport-', 'idx': 0},
                {'key': 'target', 'chars': 'target', 'idx': 0},
                {'key': 'devnode', 'chars': 'block', 'idx': 1},
                {'key': 'host_channel_id_lun', 'chars': 'block', 'idx': -1},
        ]

        if not content:
            raise SkipException(EMPTY)

        pci = []
        self.__host_attributes = set()
        self.__rport_attributes = set()
        self.__target_attributes = set()
        self.__pci_id_attributes = set()
        self.__devnode_attributes = set()
        self.__host_channel_id_lun_attributes = set()

        for line in content:
            line_sp = list(filter(None, line.strip().split('/')))
            temp_pci = {}
            for i, l in enumerate(line_sp):
                for km in KEY_MAP:
                    if l.startswith(km['chars']):
                        temp_pci[km['key']] = line_sp[i + km['idx']]

            len_of_tp = len(temp_pci)
            if len_of_tp == 6 or (len_of_tp == 5 and 'rport' not in temp_pci):
                pci.append(temp_pci)
                self.__host_attributes.add(temp_pci['host'])
                if temp_pci.get('rport'):
                    self.__rport_attributes.add(temp_pci['rport'])
                self.__target_attributes.add(temp_pci['target'])
                self.__pci_id_attributes.add(temp_pci['pci_id'])
                self.__devnode_attributes.add(temp_pci['devnode'])
                self.__host_channel_id_lun_attributes.add(temp_pci['host_channel_id_lun'])
            else:
                raise ParseException(BADWD.format(line))
        self.path_list = pci
