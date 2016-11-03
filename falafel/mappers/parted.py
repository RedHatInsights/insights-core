"""
parted - Command
================

This module provides processing for the ``parted`` command.  The output is parsed
by the ``PartedL`` class.  Attributes are provided for each field for the disk,
and a list of ``Partition`` class objects, one for each partition in the output.

Typical content of the ``parted -l`` command output
looks like::

    Model: ATA TOSHIBA MG04ACA4 (scsi)
    Disk /dev/sda: 4001GB
    Sector size (logical/physical): 512B/512B
    Partition Table: gpt
    Disk Flags: pmbr_boot

    Number  Start   End     Size    File system  Name  Flags
     1      1049kB  2097kB  1049kB                     bios_grub
     2      2097kB  526MB   524MB   xfs
     3      526MB   4001GB  4000GB                     lvm

The columns may vary depending upon the type of device.

Note:
    The examples in this module may be executed with the following command:

    ``python -m falafel.mappers.parted``

Examples:
    >>> parted_data = '''
    ... Model: ATA TOSHIBA MG04ACA4 (scsi)
    ... Disk /dev/sda: 4001GB
    ... Sector size (logical/physical): 512B/512B
    ... Partition Table: gpt
    ... Disk Flags: pmbr_boot
    ...
    ... Number  Start   End     Size    File system  Name  Flags
    ...  1      1049kB  2097kB  1049kB                     bios_grub
    ...  2      2097kB  526MB   524MB   xfs
    ...  3      526MB   4001GB  4000GB                     lvm
    ... '''.strip()
    >>> from falafel.tests import context_wrap
    >>> shared = {PartedL: PartedL(context_wrap(parted_data))}
    >>> parted_info = shared[PartedL]
    >>> parted_info.data
    {'partition_table': 'gpt', 'sector_size': '512B/512B', 'disk_flags': 'pmbr_boot', 'partitions': [{'end': '2097kB', 'name': 'bios_grub', 'number': '1', 'start': '1049kB', 'flags': 'bios_grub', 'file_system': 'bios_grub', 'size': '1049kB'}, {'start': '2097kB', 'size': '524MB', 'end': '526MB', 'number': '2', 'file_system': 'xfs'}, {'end': '4001GB', 'name': 'lvm', 'number': '3', 'start': '526MB', 'flags': 'lvm', 'file_system': 'lvm', 'size': '4000GB'}], 'model': 'ATA TOSHIBA MG04ACA4 (scsi)', 'disk': '/dev/sda', 'size': '4001GB'}
    >>> parted_info.data['model']
    'ATA TOSHIBA MG04ACA4 (scsi)'
    >>> parted_info.disk
    '/dev/sda'
    >>> parted_info.logical_sector_size
    '512B'
    >>> parted_info.physical_sector_size
    '512B'
    >>> parted_info.boot_partition
    >>> parted_info.data['disk_flags']
    'pmbr_boot'
    >>> len(parted_info.partitions)
    3
    >>> parted_info.partitions[0].data
    {'end': '2097kB', 'name': 'bios_grub', 'number': '1', 'start': '1049kB', 'flags': 'bios_grub', 'file_system': 'bios_grub', 'size': '1049kB'}
    >>> parted_info.partitions[0].number
    '1'
    >>> parted_info.partitions[0].start
    '1049kB'
    >>> parted_info.partitions[0].end
    '2097kB'
    >>> parted_info.partitions[0].size
    '1049kB'
    >>> parted_info.partitions[0].file_system
    'bios_grub'
    >>> parted_info.partitions[0].type
    >>> parted_info.partitions[0].flags
    'bios_grub'
"""
from .. import Mapper, mapper
from ..mappers import ParseException


class Partition(object):
    """Class to contain information for one partition.

    Represents the values from one row of the partition information from the
    ``parted`` command.  Column names have been converted to lowercase and are
    provided as attributes.  Column names may vary so the ``get`` method may
    be used to check for the presence of a column.

    Attributes:
        data (dict): Dictionary of partition information keyed by column names
            in lowercase.
    """
    def __init__(self, data):
        self.data = data

    @property
    def number(self):
        """str: Partition number."""
        return self.data.get('number')

    @property
    def start(self):
        """str: Starting location for the partition."""
        return self.data.get('start')

    @property
    def end(self):
        """str: Ending location for the partition."""
        return self.data.get('end')

    @property
    def size(self):
        """str: Size of the partition."""
        return self.data.get('size')

    @property
    def file_system(self):
        """str: File system type."""
        return self.data.get('file_system')

    @property
    def type(self):
        """str: File system type."""
        return self.data.get('type')

    @property
    def flags(self):
        """str: Partition flags."""
        return self.data.get('flags')

    def get(self, item):
        """Get information for column ``item`` or ``None`` if not present."""
        return self.data.get(item)


@mapper("parted_-l")
class PartedL(Mapper):
    """Class to represent attributes of the ``parted`` command output.

    The columns may vary depending upon the type of device.

    Attributes:
        data (dict): Dictionary of information returned by ``parted`` command.

    Raises:
        ParseException: Raised if ``parted`` output indicates "error" or
            "warning" in first line, or if "disk" field is not present, or if
            there is an error parsing the data.
        ValueError: Raised if there is an error parsing the partition table.
    """

    @property
    def partitions(self):
        """list: List of ``Partition`` objects for each partition."""
        return self._partitions

    @property
    def disk(self):
        """str: Disk information."""
        return self.data['disk']

    @property
    def logical_sector_size(self):
        """str: Logical part of sector size."""
        if self._sector_size:
            return self._sector_size[0]

    @property
    def physical_sector_size(self):
        """str: Physical part of sector size."""
        if self._sector_size:
            return self._sector_size[1]

    @property
    def boot_partition(self):
        """Partition: Returns a ``Partition`` object if `boot` is found in
        partition flags. ``None`` is returned otherwise."""
        return self._boot_partition

    def get(self, item):
        """Returns a value for the specified ``item`` key."""
        return self.data.get(item)

    def parse_content(self, content):
        # If device was not present output is error message
        if content[0].startswith("Error") or content[0].startswith("Warning"):
            raise ParseException("PartedL content indicates an error %s" % content[0])

        dev_info = {}
        table_lines = []
        for line in content:
            try:
                if line.strip():
                    if ':' in line:
                        label_value = line.split(':')
                        label = label_value[0].strip().lower()
                        value = label_value[1] if len(label_value) == 2 else None
                        value = value.strip() if value.strip() else None
                        if value:
                            # Single word labels
                            if ' ' not in label:
                                dev_info[label] = value
                            else:
                                if label.startswith("disk") and '/' in label:
                                    disk_parts = label.split()
                                    dev_info['disk'] = disk_parts[1].strip()
                                    dev_info['size'] = value
                                elif label.startswith("sector"):
                                    dev_info['sector_size'] = value
                                else:
                                    label = label.replace(' ', '_')
                                    dev_info[label] = value
                    else:
                        table_lines.append(line)
            except:
                raise ValueError("PartedL unable to parse line content: ", line)

        if 'disk' not in dev_info:
            raise ParseException("PartedL unable to locate Disk in content")

        partitions = []
        if table_lines:
            try:
                line = table_lines[0].replace('File system', 'File_system')
                cols = line.strip().split()
                columns = {}
                for n in cols:
                    columns[n] = {'name': n.lower()}
                    columns[n]['start'] = line.find(n)
                    columns[n]['end'] = columns[n]['start'] + len(n)
                for line in table_lines[1:]:
                    line = line.rstrip()
                    part = {}
                    for col in columns.values():
                        if len(line) > col['start']:
                            val = line[col['start']:]
                            val = val.strip().split(None, 1)[0]
                            part[col['name']] = val
                    if part:
                        partitions.append(part)
            except:
                raise ValueError("PartedL unable to parse partition content: ", table_lines)

        self._partitions = []
        self._boot_partition = None
        self._sector_size = None
        self.data = {}
        if dev_info:
            if partitions:
                dev_info['partitions'] = partitions
                for part in partitions:
                    self._partitions.append(Partition(part))
                    if 'flags' in part and 'boot' in part['flags']:
                        self._boot_partition = Partition(part)
            self.data = dev_info
            if 'sector_size' in self.data:
                self._sector_size = self.data['sector_size'].split('/', 1)
                if len(self._sector_size) != 2:
                    self._sector_size = None

if __name__ == "__main__":
    import doctest
    doctest.testmod()
