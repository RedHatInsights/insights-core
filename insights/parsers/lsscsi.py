"""
LsSCSI - command ``/usr/bin/lsscsi``
====================================

This module provides processing for the output of the ``/usr/bin/lsscsi`` command.
"""

from . import ParseException
from .. import parser, CommandParser
from insights.specs import Specs


@parser(Specs.lsscsi)
class LsSCSI(CommandParser):
    """
    This parser reads the output of ``/usr/bin/lsscsi`` into a list of dictionarys.
    Each item is a dictionary with six keys:

    * ``HCTL`` - the scsi_host,channel,target_number,LUN tuple
    * ``Peripheral-Type`` - the SCSI peripheral type
    * ``Vendor`` - the vendor name
    * ``Model`` - the model name
    * ``Revision`` - the revision string
    * ``Primary-Device-Node`` - the primary device node name

    Attributes:
        data (list of dict): List of the input lines, where each line is a dictionary having the keys identified above.

    Parsing refers to http://sg.danny.cz/scsi/lsscsi.html.

    Sample input::

        [1:0:0:0]    storage IET      Controller       0001  -
        [1:0:0:1]    cd/dvd  QEMU     QEMU DVD-ROM     2.5+  /dev/sr0
        [1:0:0:2]    disk    IET      VIRTUAL-DISK     0001  /dev/sdb
        [3:0:5:0]    tape    HP       C5713A           H910  /dev/st0

    Examples:

        >>> lsscsi[0] == {'Model': 'Controller', 'Vendor': 'IET', 'HCTL': '[1:0:0:0]', 'Peripheral-Type': 'storage', 'Primary-Device-Node': '-', 'Revision': '0001'}
        True
        >>> lsscsi.device_nodes
        ['-', '/dev/sr0', '/dev/sdb', '/dev/st0']
        >>> len(lsscsi.data)
        4
        >>> lsscsi[1]['Peripheral-Type']
        'cd/dvd'

    """
    def parse_content(self, content):
        if len(content) == 0:
            raise ParseException("Empty content of command output.")

        LSSCSI_TABLE_HEADER_ITEMS = ['HCTL', 'Peripheral-Type', 'Vendor', 'Model', 'Revision', 'Primary-Device-Node']
        LEN = len(LSSCSI_TABLE_HEADER_ITEMS)

        col_index = []
        pre_col_index = []
        # Try to find the index of a proper six column line.
        # If col_index can't be found in the above proper way,
        # set it by squeezing redundant items to 'Model' column as a workaround.
        for l in content:
            col_split = l.strip().split()
            if len(col_split) < LEN:
                break
            elif len(col_split) == LEN:
                col_index = [l.index(c) for c in col_split]
                break
            elif not pre_col_index and len(col_split) > LEN:
                unfixed_index = [l.index(c) for c in col_split]
                forth_str = l.split(col_split[2], 1)[-1].strip()
                pre_col_index = unfixed_index[:3] + [l.index(forth_str)] + unfixed_index[-2:]

        if not col_index and pre_col_index:
            col_index = pre_col_index

        if len(col_index) != LEN:
            raise ParseException("Invalid format of content, unparsable.")

        self.data = []
        for line in content:
            col_data = dict((LSSCSI_TABLE_HEADER_ITEMS[i],
                             line[col_index[i]:col_index[i + 1]].strip())
                            for i in range(LEN - 1))
            col_data[LSSCSI_TABLE_HEADER_ITEMS[-1]] = line[col_index[-1]:].strip()
            self.data.append(col_data)

    def __getitem__(self, idx):
        return self.data[idx]

    @property
    def device_nodes(self):
        """
        list: All lines' Primary-Device-Node values.
        """
        return [v['Primary-Device-Node'] for v in self.data]

    @property
    def device_vendors(self):
        """
        list: All lines' Vendor values
        """
        return [v['Vendor'] for v in self.data]
