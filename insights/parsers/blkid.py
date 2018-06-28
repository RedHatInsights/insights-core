"""
BlockIDInfo - command ``blkid``
===============================

This module provides the class ``BlockIDInfo`` which processes ``blkid`` command
output.  Typical output looks like::

    /dev/sda1: UUID="3676157d-f2f5-465c-a4c3-3c2a52c8d3f4" TYPE="xfs"
    /dev/sda2: UUID="UVTk76-UWOc-vk7s-galL-dxIP-4UXO-0jG4MH" TYPE="LVM2_member"
    /dev/mapper/rhel_hp--dl160g8--3-root: UUID="11124c1d-990b-4277-9f74-c5a34eb2cd04" TYPE="xfs"
    /dev/mapper/rhel_hp--dl160g8--3-swap: UUID="c7c45f2d-1d1b-4cf0-9d51-e2b0046682f8" TYPE="swap"
    /dev/mapper/rhel_hp--dl160g8--3-home: UUID="c7116820-f2de-4aee-8ea6-0b23c6491598" TYPE="xfs"
    /dev/mapper/rhel_hp--dl160g8--3-lv_test: UUID="d403bcbd-0eea-4bff-95b9-2237740f5c8b" TYPE="ext4"
    /dev/cciss/c0d1p3: LABEL="/u02" UUID="004d0ca3-373f-4d44-a085-c19c47da8b5e" TYPE="ext3"
    /dev/cciss/c0d1p2: LABEL="/u01" UUID="ffb8b27e-5a3d-434c-b1bd-16cb17b0e325" TYPE="ext3"
    /dev/loop0: LABEL="Satellite-5.6.0 x86_64 Disc 0" TYPE="iso9660"
    /dev/block/253:1: UUID="f8508c37-eeb1-4598-b084-5364d489031f" TYPE="ext3"

The class has one attribute ``data`` which is a ``list`` representing each line
of the input data as a ``dict`` with keys corresponding to the keys in the
output.

Examples:
    >>> block_id = shared[BlockIDInfo]
    >>> block_id.data[0]
    {'NAME': '/dev/sda1', 'UUID': '3676157d-f2f5-465c-a4c3-3c2a52c8d3f4', 'TYPE': 'xfs'}
    >>> block_id.data[0]['TYPE']
    'xfs'
    >>> block_id.filter_by_type('ext3')
    [{'NAME': '/dev/cciss/c0d1p3', 'LABEL': '/u02', 'UUID': '004d0ca3-373f-4d44-a085-c19c47da8b5e',
      'TYPE': 'ext3'},
     {'NAME': '/dev/block/253:1', 'UUID': 'f8508c37-eeb1-4598-b084-5364d489031f','TYPE': 'ext3'},
     {'NAME': '/dev/cciss/c0d1p2', 'LABEL': '/u01', 'UUID': 'ffb8b27e-5a3d-434c-b1bd-16cb17b0e325',
      'TYPE': 'ext3'}]

"""
import re
from .. import parser, CommandParser
from insights.specs import Specs


@parser(Specs.blkid)
class BlockIDInfo(CommandParser):
    """Class to process the ``blkid`` command output.

    Attributes:
        data (list): A list containing a dictionary for each line of the output in
            the form::

                [
                    {
                        'NAME': "/dev/sda1"
                        'UUID': '3676157d-f2f5-465c-a4c3-3c2a52c8d3f4',
                        'TYPE': 'xfs'
                    },
                    {
                        'NAME': "/dev/cciss/c0d1p3",
                        'LABEL': '/u02',
                        'UUID': '004d0ca3-373f-4d44-a085-c19c47da8b5e',
                        'TYPE': 'ext3'
                    }
                ]
    """
    def parse_content(self, content):
        blkid_output = []
        for line in (l for l in content if l.strip()):
            dev_name, attributes = line.rsplit(":", 1)
            device = dict((k, v) for k, v in re.findall(r'(\S+)=\"(.*?)\"\s?', line))
            device['NAME'] = dev_name.strip()
            blkid_output.append(device)

        self.data = blkid_output
        """list of dict: List containing dict for each line of command output."""

    def filter_by_type(self, fs_type):
        """list: Returns a list of all entries where TYPE = ``fs_type``."""
        return [row for row in self.data if row['TYPE'] == fs_type]
