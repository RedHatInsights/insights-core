"""
lsblk - List Block Devices
==========================
"""

import re
from falafel.core.plugins import mapper
from falafel.core import MapperOutput

MAX_GENERATIONS = 20


class BlockDevice(MapperOutput):
    """Class to contain one line of ``lsblk`` command information.

    Contains all of the fields for a single line of ``lsblk`` output.
    Computed values are the column names except where the column
    name is an invalid variable name in Python such as `MAJ:MIN`.
    The ``get`` method is provided to access any value, including
    those that are not valid names in Python.  All other valid
    names may be accessed as ``obj.column_name``.
    """
    def __init__(self, data, path=None):
        """Initialize objects for the class.

        Parameters
        ----------
        data: dict
            key, value pairs for the ``lsblk`` entry
        """
        super(BlockDevice, self).__init__(data, path)
        for k, v in data.iteritems():
            self._add_to_computed(k, v)

    def __eq__(self, other):
        return self.data == other

    def __ne__(self, other):
        return not self.data == other

    def get(self, k):
        """Get any value by keyword (column) name."""
        return self.data.get(k)


class BlockDevices(MapperOutput):
    """Class to contain all information from ``lsblk`` command.

    Output of the ``lsblk`` command is contained in this base
    class. Data may be accessed via the iterator and each item
    represents a row of output from the command in `dict` format.
    """
    def __init__(self, data, path=None):
        """Initialize objects for ``lsblk`` command output."""
        self.rows = []
        for datum in data:
            self.rows.append(BlockDevice(datum))
        super(BlockDevices, self).__init__(data, path)

    def __len__(self):
        return len(self.rows)

    def __iter__(self):
        for row in self.rows:
            yield row


@mapper('lsblk')
class LSBlock(BlockDevices):
    """Parses ``lsblk`` command output."""

    @classmethod
    def parse_content(cls, content):
        """Parse output of the ``lsblk`` command.

        The specific lsblk commands are ``/bin/lsblk`` and ``/usr/bin/lsblk``.
        Typical content of the ``lsblk`` command output looks like::

            NAME                            MAJ:MIN RM  SIZE RO TYPE  MOUNTPOINT
            sda                               8:0    0   80G  0 disk
            |-sda1                            8:1    0  256M  0 part  /boot
            `-sda2                            8:2    0 79.8G  0 part
              |-volgrp01-root (dm-0)        253:0    0   15G  0 lvm   /
              `-volgrp01-swap (dm-1)        253:1    0    8G  0 lvm   [SWAP]

        Parameters
        ----------
        content: list
            Lines in list represent output of the ``lsblk`` command.

        Returns
        -------
        dict
            A list of dictionaries containing information about each block device
            listed by the ``lsblk`` command.  Blank values in content will not be
            present in the dictionary. The ``PARENT_NAMES`` key is represented by
            a list of all parent devices to support multipath where duplicate
            child names will appear for different parents.

            .. code-block:: python

            [
                { 'NAME': 'sda',
                  'MAJ:MIN': '8:0',
                  'RM': '0',
                  'RO': "0",
                  'TYPE': 'disk',
                  'SIZE': '80G' },
                { 'NAME': 'sda1',
                  'PARENT_NAMES': ['sda']
                  'MAJ:MIN': '8:1',
                  'RM': '0',
                  'RO': '0',
                  'TYPE': 'part',
                  'SIZE': '256M',
                  'MOUNTPOINT': '/boot' }
            ]


        """
        r = re.compile(r"([\s\|\`\-]*)(\S+.*) (\d+:\d+)\s+(\d)\s+(\d+(\.\d)?[A-Z])\s+(\d)\s+([a-z]+)(.*)")
        device_list = []
        parents = [None] * MAX_GENERATIONS
        for line in content[1:]:
            name_match = r.match(line)
            generation = 0
            if name_match and len(name_match.groups()) == 9:
                device = {}
                name = name_match.group(2).strip()
                generation = len(name_match.group(1)) / 2
                parents[generation] = name
                device['NAME'] = name
                device['MAJ:MIN'] = name_match.group(3)
                device['RM'] = name_match.group(4)
                device['SIZE'] = name_match.group(5)
                device['RO'] = name_match.group(7)
                device['TYPE'] = name_match.group(8)
                mountpoint = name_match.group(9).strip()
                if len(mountpoint) > 0:
                    device['MOUNTPOINT'] = mountpoint
                if generation > 0:
                    device['PARENT_NAMES'] = parents[:generation]
                device_list.append(device)

        return device_list


@mapper('lsblk_-P-o')
class LSBlock_PO(BlockDevices):
    """Parses ``lsblk -P -o`` command output."""

    @classmethod
    def parse_content(cls, content):
        """Parse output of the ``lsblk -P -o`` command.

        ``lsblk`` command with ``-P -o`` options provides explicit selection of
        output columns in keyword=value pairs.

        The specific lsblk commands are ``/bin/lsblk -P -o column_names`` and
        ``/usr/bin/lsblk -P -o column_names``.  Typical content of the ``lsblk``
        command output looks like::

            ALIGNMENT="0" DISC-ALN="0" DISC-GRAN="0B" DISC-MAX="0B" DISC-ZERO="0" FSTYPE="" GROUP="cdrom" KNAME="sr0" LABEL="" LOG-SEC="512" MAJ:MIN="11:0" MIN-IO="512" MODE="brw-rw----" MODEL="DVD+-RW DVD8801 " MOUNTPOINT="" NAME="sr0" OPT-IO="0" OWNER="root" PHY-SEC="512" RA="128" RM="1" RO="0" ROTA="1" RQ-SIZE="128" SCHED="cfq" SIZE="1024M" STATE="running" TYPE="rom" UUID=""
            ALIGNMENT="0" DISC-ALN="0" DISC-GRAN="0B" DISC-MAX="0B" DISC-ZERO="0" FSTYPE="" GROUP="disk" KNAME="sda" LABEL="" LOG-SEC="512" MAJ:MIN="8:0" MIN-IO="512" MODE="brw-rw----" MODEL="WDC WD1600JS-75N" MOUNTPOINT="" NAME="sda" OPT-IO="0" OWNER="root" PHY-SEC="512" RA="128" RM="0" RO="0" ROTA="1" RQ-SIZE="128" SCHED="cfq" SIZE="149G" STATE="running" TYPE="disk" UUID=""
            ALIGNMENT="0" DISC-ALN="0" DISC-GRAN="0B" DISC-MAX="0B" DISC-ZERO="0" FSTYPE="ext4" GROUP="disk" KNAME="sda1" LABEL="" LOG-SEC="512" MAJ:MIN="8:1" MIN-IO="512" MODE="brw-rw----" MODEL="" MOUNTPOINT="/boot" NAME="sda1" OPT-IO="0" OWNER="root" PHY-SEC="512" RA="128" RM="0" RO="0" ROTA="1" RQ-SIZE="128" SCHED="cfq" SIZE="500M" STATE="" TYPE="part" UUID="c7c4c016-8b00-4ded-bffb-5cc4719b7d45"

        Parameters
        ----------
        content: list
            Lines in list represent output of the ``lsblk -P -o`` command.

        Returns
        -------
        dict
            A list of dictionaries containing information about each block device
            listed by the ``lsblk`` command.  Blank values in content will not be
            present in the dictionary.

            .. code-block:: python

            [
                { 'NAME': 'sda',
                  'MAJ:MIN': '8:0',
                  'RM': '0',
                  'RO': '0',
                  'TYPE': 'disk',
                  'SIZE': '149G',
                  # All other fields listed in the example above with non-null values
                },
                { 'NAME': 'sda1',
                  'MAJ:MIN': '8:1',
                  'RM': '0',
                  'RO': '0',
                  'TYPE': 'part',
                  'SIZE': '500M',
                  'MOUNTPOINT': '/boot',
                  'FSTYPE': 'ext4',
                  # All other fields listed in the example above with non-null values
                }
            ]


        """
        device_list = []
        for line in content:
            device_list.append({k: v for k, v in re.findall(r'(\S+)=\"(.*?)\"\s?', line) if len(v) > 0})
        return device_list
