"""
Parted - Partition Editor
=========================
"""
from falafel.core import MapperOutput, computed
from falafel.core.plugins import mapper
from falafel.mappers import ParseException


class Partition(MapperOutput):
    """Class to contain information for one partition.

    The ``parted`` command provides disk information including a list
    of partitions on the disk.  Objects of this class contain the information
    for a single partition.

    Attributes
    ----------
    data: dict
        Possible keys for the data include: ``number, start, end,
        size, files_system, type, name``, and ``flags``. If a value is
        not present for a key then it will not be present in ``data``.
        Attributes are also available as computed values if present.
    """
    def __init__(self, data, path=None):
        """Initialize objects for the class.

        Parameters
        ----------
        data: dict
            key, value pairs for the ``partition`` info.
        """
        super(Partition, self).__init__(data, path)
        for k, v in data.iteritems():
            self._add_to_computed(k, v)


@mapper("parted_-l")
class PartedL(MapperOutput):
    """Class to represent attributes of the ``parted`` command output.

    Attributes
    ----------
    data: dict
        Possible attributes include: ``disk, model, sector_size,
        partition_table, disk_flags``, and ``disk_label_type``. If a value
        is blank for any key then it will not be present in ``data``."""

    def __init__(self, data, path=None):
        """Initialize objects for ``parted`` command output."""
        self._partitions = []
        self._boot_partition = None
        self._sector_size = None
        if 'partitions' in data:
            for part in data['partitions']:
                self._partitions.append(Partition(part, path))
                if 'flags' in part and 'boot' in part['flags']:
                    self._boot_partition = Partition(part)
        if 'sector_size' in data:
            self._sector_size = data['sector_size'].split('/', 1)
            if len(self._sector_size) != 2:
                self._sector_size = None
        super(PartedL, self).__init__(data, path)

    @property
    def partitions(self):
        return self._partitions

    @computed
    def disk(self):
        return self.data['disk']

    @computed
    def logical_sector_size(self):
        if self._sector_size:
            return self._sector_size[0]

    @computed
    def physical_sector_size(self):
        if self._sector_size:
            return self._sector_size[1]

    @property
    def boot_partition(self):
        return self._boot_partition

    @staticmethod
    def parse_content(content):
        """Parse lines from the command output of ``parted -l device_name``.

        Typical content of the ``parted -l device_name`` command output
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

        Parameters
        ----------
        context: falafel.core.context.Context
            Context object providing file content for the ``parted`` command as
            well as metadata about the target system.

        Returns
        -------
        PartedInfo: falafel.mappers.parted.PartedInfo
            Container object with methods for access to all data or specific
            items of the data output from the ``parted`` command.  Specific
            data may be accessed by the computed class attributes. The data
            attribute of the object is stored in the format:

            .. code-block:: python

                {
                    'model': 'ATA TOSHIBA MG04ACA4 (scsi)',
                    'disk': '/dev/sda',
                    'size': '4001GB',               # obj disk_size attrib
                    'sector_size': '512B/512B',     # logical, physical
                    'partition_table': 'gpt',
                    'disk_flags': 'pmbr_boot',
                    'partitions': [
                        {
                            'number'     : '1',
                            'start'      : '1049kB',
                            'end'        : '2097kB',
                            'size'       : '1049kB',
                            'flags'      : 'bios_grub'
                        },
                        ...
                    ]
                }

        """
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

        if dev_info:
            if partitions:
                dev_info['partitions'] = partitions
            return dev_info
