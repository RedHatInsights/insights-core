"""
LsDisk - Command ``ls -lanR /dev/disk``
=======================================

The ``ls -lanR /dev/disk`` command provides information for the listing of the
directories under ``/dev/disk/`` .

Sample input is shown in the Examples. See ``FileListing`` class for
additional information.

Examples:
    >>> LS_DISK = '''
    ... /dev/disk/by-id:
    ... total 0
    ... drwxr-xr-x. 2 0 0 360 Sep 20 09:36 .
    ... drwxr-xr-x. 5 0 0 100 Sep 20 09:36 ..
    ... lrwxrwxrwx. 1 0 0   9 Sep 20 09:36 ata-VBOX_CD-ROM_VB2-01700376 -> ../../sr0
    ... lrwxrwxrwx. 1 0 0   9 Sep 20 09:36 ata-VBOX_HARDDISK_VB4c56cb04-26932e6a -> ../../sdb
    ... lrwxrwxrwx. 1 0 0  10 Sep 20 09:36 ata-VBOX_HARDDISK_VB4c56cb04-26932e6a-part1 -> ../../sdb1
    ... lrwxrwxrwx. 1 0 0  10 Sep 20 09:36 scsi-SATA_VBOX_HARDDISK_VB4c56cb04-26932e6a-part1 -> ../../sdb1
    ...
    ... /dev/disk/by-path:
    ... total 0
    ... drwxr-xr-x. 2 0 0 160 Sep 20 09:36 .
    ... drwxr-xr-x. 5 0 0 100 Sep 20 09:36 ..
    ... lrwxrwxrwx. 1 0 0   9 Sep 20 09:36 pci-0000:00:0d.0-scsi-1:0:0:0 -> ../../sdb
    ... lrwxrwxrwx. 1 0 0  10 Sep 20 09:36 pci-0000:00:0d.0-scsi-1:0:0:0-part1 -> ../../sdb1
    ...
    ... /dev/disk/by-uuid:
    ... total 0
    ... drwxr-xr-x. 2 0 0 100 Sep 20 09:36 .
    ... drwxr-xr-x. 5 0 0 100 Sep 20 09:36 ..
    ... lrwxrwxrwx. 1 0 0  10 Sep 20 09:36 3ab50b34-d0b9-4518-9f21-05307d895f81 -> ../../dm-1
    ... lrwxrwxrwx. 1 0 0  10 Sep 20 09:36 51c5cf12-a577-441e-89da-bc93a73a1ba3 -> ../../sda1
    ... lrwxrwxrwx. 1 0 0  10 Sep 20 09:36 7b0068d4-1399-4ce7-a54a-3e2fc1232299 -> ../../dm-0
    ... '''
    >>> from insights.tests import context_wrap
    >>> ls_disk = LsDisk(context_wrap(LS_DISK))
     <__main__.LsDisk object at 0x7f674914c690>
    >>> "/dev/disk/by-path" in ls_disk
    True
    >>> ls_disk.files_of("/dev/disk/by-path")
    ['pci-0000:00:0d.0-scsi-1:0:0:0', 'pci-0000:00:0d.0-scsi-1:0:0:0-part1']
    >>> ls_disk.dirs_of("/dev/disk/by-path")
    ['.', '..']
    >>> ls_disk.specials_of("/dev/disk/by-path")
    []
    >>> ls_disk.listing_of("/dev/disk/by-path").keys()
    ['pci-0000:00:0d.0-scsi-1:0:0:0-part1', 'pci-0000:00:0d.0-scsi-1:0:0:0', '..', '.']
    >>> ls_disk.dir_entry("/dev/disk/by-path", "pci-0000:00:0d.0-scsi-1:0:0:0")
    {'group': '0', 'name': 'pci-0000:00:0d.0-scsi-1:0:0:0', 'links': 1, 'perms': 'rwxrwxrwx.',
    'raw_entry': 'lrwxrwxrwx. 1 0 0   9 Sep 20 09:36 pci-0000:00:0d.0-scsi-1:0:0:0 -> ../../sdb', 'owner': '0',
    'link': '../../sdb', 'date': 'Sep 20 09:36', 'type': 'l', 'size': 9}
    >>> ls_disk.listing_of('/dev/disk/by-path')['.']['type'] == 'd'
    True
    >>> ls_disk.listing_of('/dev/disk/by-path')['pci-0000:00:0d.0-scsi-1:0:0:0']['link']
    '../../sdb'
"""

from .. import parser, FileListing, CommandParser
from insights.specs import Specs


@parser(Specs.ls_disk)
class LsDisk(CommandParser, FileListing):
    """Parses output of ``ls -lanR /dev/disk`` command."""
    pass
