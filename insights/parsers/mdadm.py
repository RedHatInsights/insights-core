"""
MDAdm parsers
=============

Classes to parse ``mdadm`` commands information.

Parsers provided by this module include:

MDAdm - command ``/usr/sbin/mdadm -E {device}``
-----------------------------------------------

MDAdmDetail - command ``/usr/sbin/mdadm -D /dev/md*``
-----------------------------------------------------

"""
from insights.core import CommandParser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.plugins import parser
from insights.parsers import split_kv_pairs, parse_fixed_table
from insights.specs import Specs


@parser(Specs.mdadm_E)
class MDAdmMetadata(CommandParser, dict):
    """
    Parser for output of ``mdadm -E`` for each MD device in system.

    This stores the information from the output in the following properties:
    * ``device`` - the name of the device after /dev/ - e.g. loop0

    Sample output::

        /dev/loop0:
        Magic : a92b4efc
        Version : 1.0
        Feature Map : 0x0
        Array UUID : 98e098ef:c8662ce2:2ed2aa5f:7f0416a9
        Name : 0
        Creation Time : Mon Jun 29 02:16:52 2020
        Raid Level : raid1
        Raid Devices : 2

        Avail Dev Size : 16383968 sectors (7.81 GiB 8.39 GB)
        Array Size : 1048576 KiB (1024.00 MiB 1073.74 MB)
        Used Dev Size : 2097152 sectors (1024.00 MiB 1073.74 MB)
        Super Offset : 16383984 sectors
        Unused Space : before=0 sectors, after=14286824 sectors
        State : clean
        Device UUID : 5e249ed9:a9ee800a:c09c963f:363a18d2

        Update Time : Mon Jun 29 02:19:56 2020
        Bad Block Log : 512 entries available at offset -8 sectors
        Checksum : 395066e8 - correct
        Events : 60

        Device Role : Active device 0
        Array State : AA ('A' == active, '.' == missing, 'R' == replacing)

    Examples:
        >>> mdadm.device
        '/dev/loop0'
        >>> mdadm["Device UUID"]
        '5e249ed9:a9ee800a:c09c963f:363a18d2'
        >>> mdadm["Events"]
        60
    """
    def parse_content(self, content):
        mdadm_dev = "/mdadm_-E_.dev."
        if mdadm_dev in self.file_path:
            self.device = '/dev/' + self.file_path.split(mdadm_dev)[1].strip()
        else:
            raise SkipComponent('Cannot parse device name from path {p}'.format(p=self.file_path))

        for key, val in split_kv_pairs(content, split_on=':').items():
            if val.isdigit():
                val = int(val)

            self[key] = val


class MDAdmDetailDevice(dict):
    """
    Parser for single MD device data from ``mdadm -D /dev/md*`` output.

    MD arrry device's full path name will be reside in /dev/ and start with "md",
    or reside in /dev/md/. For examples: /dev/md0, /dev/md/home .

    The md device's properties in <property name> : <property value> format
    will be stored seprately, and are accessable via <property name>.
    """
    def parse_device(self, content, device_start_index, table_start_index, index):

        self['device_name'] = content[device_start_index].split(':')[0]

        has_device_table = bool(table_start_index > device_start_index)

        kv_pairs_end_index = table_start_index if has_device_table else index
        # Parse the key value pairs part in content
        if kv_pairs_end_index - device_start_index > 1:
            self.update(split_kv_pairs(content[device_start_index + 1:kv_pairs_end_index], split_on=':'))

        # Parse the devices info table part in content
        self['device_table'] = parse_fixed_table(content[table_start_index:index]) if has_device_table else []

        # Empty prased data
        if not (len(self) > 2 or self['device_table']):
            raise ParseException('Empty parsed data')

    @property
    def is_internal_bitmap(self):
        """ bool: True if using "Internal" for Intent Bitmap """
        return self.get("Intent Bitmap") == "Internal"

    @property
    def device_name(self):
        """ str: the name of the device, e.g. /dev/md0 """
        return self.get("device_name")

    @property
    def device_table(self):
        """ list: the devices info table """
        return self.get("device_table")


@parser(Specs.mdadm_D)
class MDAdmDetail(CommandParser, list):
    """
    Parser for output of command ``mdadm -D /dev/md*``.

    Each MD arrry device will be wrapped in :class:``MDAdmDetailDevice``.

    The md device's properties in <property name> : <property value> format
    will be stored seprately, and are accessable via <property name>.

    Attributes:
        unparsable_device_list (list):  the name of unparsable devices

    Sample output::

        /dev/md2:
                   Version : 1.2
             Creation Time : Sun Sep  5 23:19:18 2021
                Raid Level : raid1
                Array Size : 7501333824 (7153.83 GiB 7681.37 GB)
             Used Dev Size : 7501333824 (7153.83 GiB 7681.37 GB)
              Raid Devices : 2
             Total Devices : 2
               Persistence : Superblock is persistent

             Intent Bitmap : Internal

               Update Time : Sun Sep 26 22:18:13 2021
                     State : clean
            Active Devices : 2
           Working Devices : 2
            Failed Devices : 0
             Spare Devices : 0

        Consistency Policy : bitmap

                      Name : hostname:2  (local to host hostname)
                      UUID : 245e1231:245e1231:245e1231:245e1231
                    Events : 1821

            Number   Major   Minor   RaidDevice State
               0     259        1        0      active sync   /dev/nvme2n1
               1     259        0        1      active sync   /dev/nvme3n1
        /dev/md3:
                   Version : 1.2
             Creation Time : Sun Sep  5 23:19:18 2021
                    ...

    Examples:
        >>> len(mdadm_d)
        2
        >>> mdadm_d[0].device_name
        '/dev/md2'
        >>> mdadm_d[0]["UUID"]
        '245e1231:245e1231:245e1231:245e1231'
        >>> mdadm_d[0].is_internal_bitmap
        True
        >>> len(mdadm_d[0].device_table)
        2
        >>> mdadm_d[1].get("Version")
        '1.2'
    """

    MDADM_ERROR_MSG_PREFIX = "mdadm: "

    def parse_content(self, content):

        if len(content) == 0:
            raise SkipComponent("Empty content of command output")

        self.unparsable_device_list = []
        self.error_messages = []

        def _handle_device(device_start_index, table_start_index, index):

            if content[device_start_index].startswith(self.MDADM_ERROR_MSG_PREFIX):
                self.error_messages.append(content[device_start_index])
                return

            try:
                device_detail = MDAdmDetailDevice()
                device_detail.parse_device(content, device_start_index, table_start_index, index)
                self.append(device_detail)
            except ParseException:
                self.unparsable_device_list.append(content[device_start_index].split(':')[0])

        # Split the devices content
        device_start_index = 0
        table_start_index = 0
        for index, _line in enumerate(content):
            line = _line.strip()
            if not line:
                continue

            # Start line of a new device
            if (line.startswith("/dev/md") and line.endswith(":") or
                    line.startswith(self.MDADM_ERROR_MSG_PREFIX)):

                # Handle the last recongnized device
                if index > device_start_index:
                    _handle_device(device_start_index, table_start_index, index)

                device_start_index = index

            elif "Number   Major   Minor" in line:
                table_start_index = index

        # Handle the final device
        _handle_device(device_start_index, table_start_index, index + 1)

        # Empty prased data
        if len(self) < 1:
            raise SkipComponent('Empty parsed device')
