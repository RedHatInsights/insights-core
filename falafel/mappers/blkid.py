"""
Block ID
========
"""

import re
from falafel.core.plugins import mapper
from falafel.core import MapperOutput


@mapper("blkid")
class BlockIDInfo(MapperOutput):
    """
    Typical content of the ``blkid`` command output looks like::

        /dev/sda1: UUID="3676157d-f2f5-465c-a4c3-3c2a52c8d3f4" TYPE="xfs"
        /dev/sda2: UUID="UVTk76-UWOc-vk7s-galL-dxIP-4UXO-0jG4MH" TYPE="LVM2_member"
        /dev/mapper/rhel_hp--dl160g8--3-root: UUID="11124c1d-990b-4277-9f74-c5a34eb2cd04" TYPE="xfs"
        /dev/mapper/rhel_hp--dl160g8--3-swap: UUID="c7c45f2d-1d1b-4cf0-9d51-e2b0046682f8" TYPE="swap"
        /dev/mapper/rhel_hp--dl160g8--3-home: UUID="c7116820-f2de-4aee-8ea6-0b23c6491598" TYPE="xfs"
        /dev/mapper/rhel_hp--dl160g8--3-lv_test: UUID="d403bcbd-0eea-4bff-95b9-2237740f5c8b" TYPE="ext4"
        /dev/cciss/c0d1p3: LABEL="/u02" UUID="004d0ca3-373f-4d44-a085-c19c47da8b5e" TYPE="ext3"
        /dev/cciss/c0d1p2: LABEL="/u01" UUID="ffb8b27e-5a3d-434c-b1bd-16cb17b0e325" TYPE="ext3"
        /dev/loop0: LABEL="Satellite-5.6.0 x86_64 Disc 0" TYPE="iso9660"

    Parameters
    ----------
    context: falafel.core.context.Context
        Context object providing file content for the ``blkid`` command as well
        as metadata about the target system.

    Returns
    -------
    list
        A list of device info in dictionary format containing only values
        present in the ``blkid`` output.  For example,

        .. code-block:: python

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
    @staticmethod
    def parse_content(content):
        blkid_output = []
        if len(content) > 0:
            for line in content:
                dev_name, attributes = line.split(":", 1)
                device = {k: v for k, v in re.findall(r'(\S+)=\"(.*?)\"\s?', line)}
                device['NAME'] = dev_name.strip()
                blkid_output.append(device)

        return blkid_output

    def filter_by_type(self, fs_type):
        return [row for row in self.data if row['TYPE'] == fs_type]
