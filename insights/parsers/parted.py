"""
Parted Parsers
==============

Classes to parse ``parted`` command information.

Parsers provided by this module include:

PartedL - command ``parted -l -s``
----------------------------------

"""
from insights.core import CommandParser
from insights.core.exceptions import ParseException
from insights.core.plugins import parser
from insights.parsers import parse_fixed_table
from insights.specs import Specs


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


class PartedDevice(object):
    """Class to contain information for one device of ``parted`` command output.

    The columns of partation table may vary depending upon the type of device.

    Attributes:
        device_info (dict): Dictionary of information of this device.
        partitions (list): The partitions of this device, as Partition objects.
        boot_partition (Partition): the first partition marked as bootable,
            or ``None`` if one was not found.

    Raises:
        ParseException: Raised if command output of this device indicates
            "error" or "warning" in first line, or if "disk" field is not
            present, or if there is an error parsing the data.
    """

    @property
    def data(self):
        """dict: Device information."""
        return self.device_info

    @property
    def disk(self):
        """str: Disk information."""
        return self.device_info['disk']

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

    def get(self, item):
        """Returns a value for the specified ``item`` key."""
        return self.device_info.get(item)

    def __init__(self, content):
        # If device was not present output is error message
        if content[0].startswith("Error") or content[0].startswith("Warning"):
            raise ParseException("PartedL content indicates an error %s" % content[0])

        dev_info = {}
        table_lines = []
        for line in content:
            if not line.strip():
                continue
            if ':' in line:
                label_value = line.split(':')
                label = label_value[0].strip().lower()
                if len(label_value) == 2:
                    value = label_value[1].strip()
                    value = value if value else None
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

        if 'disk' not in dev_info:
            raise ParseException("PartedL unable to locate Disk in content")

        # Now construct the partition table from the fixed table
        partitions = []
        if table_lines:
            table_lines[0] = table_lines[0].replace('File system', 'File_system').lower()
            partitions = parse_fixed_table(table_lines)

        self.partitions = [Partition(n) for n in partitions]
        self.boot_partition = None
        self._sector_size = None
        # If we got any partitions, find the first boot partition
        for part in partitions:
            if 'flags' in part and 'boot' in part['flags']:
                self.boot_partition = Partition(part)
                break
        self.device_info = dev_info
        if 'sector_size' in self.device_info:
            self._sector_size = self.device_info['sector_size'].split('/', 1)
            if len(self._sector_size) != 2:
                self._sector_size = None


@parser(Specs.parted__l)
class PartedL(CommandParser):
    """Class to represent attributes of the ``parted -l -s`` command output.

    Attributes:
        devices_info (list): The devices found in the output, as PartedDevice
            objects.

    Typical content of the ``parted -l -s`` command output looks like::

        Model: ATA TOSHIBA MG04ACA4 (scsi)
        Disk /dev/sda: 4001GB
        Sector size (logical/physical): 512B/512B
        Partition Table: gpt
        Disk Flags: pmbr_boot

        Number  Start   End     Size    File system  Name  Flags
         1      1049kB  2097kB  1049kB                     bios_grub
         2      2097kB  526MB   524MB   xfs
         3      526MB   4001GB  4000GB                     lvm


        Model: IBM 2107900 (scsi)
        Disk /dev/sdb: 2147MB
        Sector size (logical/physical): 512B/512B
        Partition Table: msdos

        Number  Start   End     Size    Type     File system  Flags
         1      32.3kB  2580kB  2548kB  primary

    The columns of partation table may vary depending upon the type of device.

    Note:
        The examples in this module may be executed with the following command:

        ``python -m insights.parsers.parted``

    Examples:
        >>> [device.disk for device in parted_l_results]
        ['/dev/sda', '/dev/sdb']
        >>> parted_info = parted_l_results.get('/dev/sda')
        >>> sorted(parted_info.device_info.items())
        [('disk', '/dev/sda'), ('disk_flags', 'pmbr_boot'), ('model', 'ATA TOSHIBA MG04ACA4 (scsi)'), ('partition_table', 'gpt'), ('sector_size', '512B/512B'), ('size', '4001GB')]
        >>> parted_info.device_info['model']
        'ATA TOSHIBA MG04ACA4 (scsi)'
        >>> parted_info.disk
        '/dev/sda'
        >>> parted_info.logical_sector_size
        '512B'
        >>> parted_info.physical_sector_size
        '512B'
        >>> parted_info.boot_partition
        >>> parted_info.device_info['disk_flags']
        'pmbr_boot'
        >>> len(parted_info.partitions)
        3
        >>> sorted(parted_info.partitions[0].data.items())
        [('end', '2097kB'), ('file_system', ''), ('flags', 'bios_grub'), ('name', ''), ('number', '1'), ('size', '1049kB'), ('start', '1049kB')]
        >>> parted_info.partitions[0].number
        '1'
        >>> parted_info.partitions[0].start
        '1049kB'
        >>> parted_info.partitions[0].end
        '2097kB'
        >>> parted_info.partitions[0].size
        '1049kB'
        >>> parted_info.partitions[0].file_system
        ''
        >>> parted_info.partitions[0].type
        >>> parted_info.partitions[0].flags
        'bios_grub'

    """

    def get(self, disk_name):
        """Returns a value for the specified ``item`` key."""
        for dev in self.devices_info:
            if dev.disk == disk_name:
                return dev

    def __iter__(self):
        for dev in self.devices_info:
            yield dev

    def parse_content(self, content):
        """Divide "content" into each device section by two empty lines."""

        device_tables = []

        # Divide "content" into each Device Section by two empty lines.
        idx, this_start_idx = 0, 0
        is_last_line_empty = False
        for idx, raw_line in enumerate(content):
            if len(raw_line.strip()) == 0:
                if is_last_line_empty:
                    # Fount this line as the second blank line
                    device_tables.append(content[this_start_idx:idx - 1])
                    this_start_idx = idx + 1
                    is_last_line_empty = False
                else:
                    is_last_line_empty = True
            else:
                is_last_line_empty = False

        # Take left "content" as the last Device Section, skip the empty case
        if this_start_idx < len(content) - 1:
            device_tables.append(content[this_start_idx:])

        devices_info = []
        for dev_table in device_tables:
            try:
                this_parsed_dev_table = PartedDevice(dev_table)
                devices_info.append(this_parsed_dev_table)
            except ParseException:
                # Mute any exception from PartedDevice parsing.
                # Keep only fully parsed Device into the final devices_info.
                pass

        self.devices_info = devices_info
