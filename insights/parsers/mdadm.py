"""
MDAdm - command ``/usr/sbin/mdadm -E {device}``
===============================================
"""

from insights.core import CommandParser
from insights.core.plugins import parser
from insights.parsers import split_kv_pairs
from insights.parsers import SkipException

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
            raise SkipException('Cannot parse device name from path {p}'.format(p=self.file_path))

        for key, val in split_kv_pairs(content, split_on=':').items():
            if val.isdigit():
                val = int(val)

            self[key] = val
