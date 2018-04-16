"""
LsSCSI - command ``/usr/bin/lsscsi``
====================================

This parser reads the output of ``/usr/bin/lsscsi`` into a list of dictionarys.
Each item is a dictionary with six keys:

* ``HCTL`` - the scsi_host,channel,target_number,LUN tuple
* ``Peripheral-Type`` - the SCSI peripheral type
* ``Vendor`` - the vendor name
* ``Model`` - the model name
* ``Revision`` - the revision string
* ``Primary-Device-Node`` - the primary device node name

This dictionary is available in the ``data`` attribute.

Parsing refers to http://sg.danny.cz/scsi/lsscsi.html.

Sample input::

    [1:0:0:0]    storage IET      Controller       0001  -
    [1:0:0:1]    cd/dvd  QEMU     QEMU DVD-ROM     2.5+  /dev/sr0
    [1:0:0:2]    disk    IET      VIRTUAL-DISK     0001  /dev/sdb
    [3:0:5:0]    tape    HP       C5713A           H910  /dev/st0

Examples:

    >>> lsscsi = LsSCSI(context_wrap(LSSCSI_1))
    >>> lsscsi[0]
    {'Model': 'Controller', 'Vendor': 'IET', 'HCTL': '[1:0:0:0]', 'Peripheral-Type': 'storage', 'Primary-Device-Node': '-', 'Revision': '0001'}
    >>> lsscsi.device_nodes
        ['-', '/dev/sdb', '/dev/st0']
    >>> len(lsscsi)
    4
    >>> lsscsi[1]['Peripheral-Type']
    'cd/dvd'
"""

from . import parse_delimited_table
from .. import Parser, parser, LegacyItemAccess
from insights.specs import Specs


@parser(Specs.lsscsi)
class LsSCSI(LegacyItemAccess, Parser):
    """
    Parse the output of ``/usr/bin/lsscsi``.
    """
    def parse_content(self, content):
        LSSCSI_TABLE_HEADER = ["HCTL  Peripheral-Type  Vendor  Model  Revision Primary-Device-Node"]
        self.data = parse_delimited_table(LSSCSI_TABLE_HEADER + content)

    @property
    def device_nodes(self):
        return [v['Primary-Device-Node'] for v in self.data]
