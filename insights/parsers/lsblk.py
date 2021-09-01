"""
Block device listing
====================

Module for processing output of the ``lsblk`` command.  Different information
is provided by the ``lsblk`` command depending upon the options.  Parsers
included here are:

LSBlock - Command ``lsblk``
---------------------------

The ``LSBlock`` class parses output of the ``lsblk`` command with no options.

LSBlockPairs - Command ``lsblk -P -o [columns...]``
---------------------------------------------------

The ``LSBlockPairs`` class parses output of the ``lsblk -P -o [columns...]``
command.

These classes based on ``BlockDevices`` which implements all of the
functionality except the parsing of command specific information.
Information is stored in the attribute ``self.rows`` which is a ``list`` of
``BlockDevice`` objects.

Each ``BlockDevice`` object provides the functionality for one row of data from the
command output.  Data in a ``BlockDevice`` object is accessible by multiple methods.
For example the NAME field can be accessed in the following four ways::

    lsblk_info.rows[0].data['NAME']
    lsblk_info.rows[0].NAME
    lsblk_info.rows[0].name
    lsblk_info.rows[0].get('NAME')

Sample output of the ``lsblk`` command looks like::

    NAME          MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
    vda           252:0    0    9G  0 disk
    |-vda1        252:1    0  500M  0 part /boot
    `-vda2        252:2    0  8.5G  0 part
      |-rhel-root 253:0    0  7.6G  0 lvm  /
      |-rhel-swap 253:1    0  924M  0 lvm  [SWAP]
    sda             8:0    0  500G  0 disk
    `-sda1          8:1    0  500G  0 part /data

Note the hierarchy demonstrated in the name column. For instance ``vda1`` and
``vda2`` are children of ``vda``.  Likewise, ``rhel-root`` and ``rhel-swap``
are children of ``vda2``.  This relationship is demonstrated in the
``PARENT_NAMES`` key, which is only present if the row is a *child* row.  For
example ``PARENT_NAMES`` value for ``rhel-root`` will be ``['vda', 'vda2']``
meaning that ``vda2`` is the immediate parent and ``vda`` is parent of
``vda2``.

Also note that column names that are not valid Python property names been
changed.  For example ``MAJ:MIN`` has been changed to ``MAJ_MIN``.

Examples:
    >>> lsblk_info = shared[LSBlock]
    >>> lsblk_info
    <insights.parsers.lsblk.LSBlock object at 0x7f1f6a422d50>
    >>> lsblk_info.rows
    [disk:vda,
     part:vda1(/boot),
     part:vda2,
     lvm:rhel-root(/),
     lvm:rhel-swap([SWAP]),
     disk:sda,
     part:sda1(/data)]
    >>> lsblk_info.rows[0]
    disk:vda
    >>> lsblk_info.rows[0].data
    {'READ_ONLY': False, 'NAME': 'vda', 'REMOVABLE': False, 'MAJ_MIN': '252:0',
     'TYPE': 'disk', 'SIZE': '9G'}
    >>> lsblk_info.rows[0].data['NAME']
    'vda'
    >>> lsblk_info.rows[0].NAME
    'vda'
    >>> lsblk_info.rows[0].name
    'vda'
    >>> lsblk_info.rows[0].data['MAJ_MIN']
    '252:0'
    >>> lsblk_info.rows[0].MAJ_MIN
    '252:0'
    >>> lsblk_info.rows[0].maj_min
    '252:0'
    >>> lsblk_info.rows[0].removable
    False
    >>> lsblk_info.rows[0].read_only
    False
    >>> lsblk_info.rows[2].data
    {'READ_ONLY': False, 'PARENT_NAMES': ['vda'], 'NAME': 'vda2',
     'REMOVABLE': False, 'MAJ_MIN': '252:2', 'TYPE': 'part', 'SIZE': '8.5G'}
    >>> lsblk_info.rows[2].parent_names
    ['vda']
    >>> lsblk_info.rows[3].parent_names
    ['vda', 'vda2']
    >>> lsblk_info.device_data['vda'] # Access devices by name
    'disk:vda'
    >>> lsblk_info.search(NAME='vda2')
    [{'READ_ONLY': False, 'PARENT_NAMES': ['vda'], 'NAME': 'vda2',
     'REMOVABLE': False, 'MAJ_MIN': '252:2', 'TYPE': 'part', 'SIZE': '8.5G'}]
"""

from __future__ import division
import re
from .. import parser, CommandParser
from . import ParseException, keyword_search
from insights.specs import Specs

MAX_GENERATIONS = 20


class BlockDevice(object):
    """Class to contain one line of ``lsblk`` command information.

    Contains all of the fields for a single line of ``lsblk`` output.
    Computed values are the column names except where the column
    name is an invalid variable name in Python such as `MAJ:MIN`.
    The ``get`` method is provided to access any value, including
    those that are not valid names in Python.  All other valid
    names may be accessed as ``obj.column_name``.
    """
    def __init__(self, data):
        self.data = data
        for k, v in data.items():
            k = re.sub(r'[-:\.]', "_", k)
            setattr(self, k, v)
            setattr(self, k.lower(), v)

    def __contains__(self, item):
        return hasattr(self, item)

    def __eq__(self, other):
        return self.data == other

    def iteritems(self):
        return self.items()

    def items(self):
        return self.data.items()

    def get(self, k, default=None):
        """Get any value by keyword (column) name."""
        return self.data.get(k, default)

    def __str__(self):
        if 'TYPE' in self.data and 'MOUNTPOINT' in self.data:
            return '{type}:{name}({mnt})'.format(
                type=self.data['TYPE'], name=self.data['NAME'],
                mnt=self.data['MOUNTPOINT']
            )
        else:
            # As long as the regular expression in LsBlock works, we must end
            # up with NAME and TYPE records here.  In LSBlockPairs this is
            # enforced with an explicit check.
            return '{type}:{name}'.format(type=self.data['TYPE'], name=self.data['NAME'])


class BlockDevices(CommandParser):
    """Class to contain all information from ``lsblk`` command.

    Output of the ``lsblk`` command is contained in this base
    class. Data may be accessed via the iterator and each item
    represents a row of output from the command in `dict` format.

    Attributes:
        rows (list of BlockDevice): List of ``BlockDevice`` objects for each
            row of the input. Input column name matches key name except any
            '-' is replaced with '_' and the following names are changed::

                Column Name     Key Name
                MAJ:MIN         MAJ_MIN
                RM              REMOVABLE
                RO              READD_ONLY
        device_data (dict of BlockDevice): A dictionary of ``BlockDevice``
            objects keyed on the 'NAME' column (e.g. ``sda`` or ``rhel-swap``)
    """

    def __len__(self):
        return len(self.rows)

    def __iter__(self):
        for row in self.rows:
            yield row

    def search(self, **kwargs):
        """
        Returns a list of the block devices (in order) matching the given
        criteria. Keys are searched for directly - see the
        :py:func:`insights.parsers.keyword_search` utility function for more
        details.  If no search parameters are given, no rows are returned.
        Keys need to be in all upper case, as they appear in the source data.

        Examples:

            >>> blockdevs.search(NAME='sda1')
            [{'NAME': '/dev/sda1', 'TYPE': 'disk', 'SIZE', '80G', ...}]
            >>> blockdevs.search(TYPE='lvm')
            [{'NAME': 'volgrp01-root', 'TYPE': 'lvm', 'SIZE', '15G', ...}...]

        Arguments:
            **kwargs (dict): Dictionary of key-value pairs to search for.

        Returns:
            (list): The list of mount points matching the given criteria.
        """
        return keyword_search(self.rows, **kwargs)


@parser(Specs.lsblk)
class LSBlock(BlockDevices):
    """Parse output of the ``lsblk`` command.

    The specific lsblk commands are ``/bin/lsblk`` and ``/usr/bin/lsblk``.
    Typical content of the ``lsblk`` command output looks like::

        NAME                            MAJ:MIN RM  SIZE RO TYPE  MOUNTPOINT
        sda                               8:0    0   80G  0 disk
        |-sda1                            8:1    0  256M  0 part  /boot
        `-sda2                            8:2    0 79.8G  0 part
          |-volgrp01-root (dm-0)        253:0    0   15G  0 lvm   /
          `-volgrp01-swap (dm-1)        253:1    0    8G  0 lvm   [SWAP]

    Note:
        See the discussion of the key ``PARENT_NAMES`` above.
    """
    def parse_content(self, content):
        r = re.compile(r"([\s\|\`\-]*)(\S+.*) (\d+:\d+)\s+(\d)\s+(\d+(\.\d)?[A-Z])\s+(\d)\s+([a-z0-9]+)(.*)")
        device_list = []
        parents = [None] * MAX_GENERATIONS
        for line in content[1:]:
            name_match = r.match(line)
            generation = 0
            if name_match and len(name_match.groups()) == 9:
                device = {}
                name = name_match.group(2).strip()
                generation = len(name_match.group(1)) // 2
                parents[generation] = name
                device['NAME'] = name
                device['MAJ_MIN'] = name_match.group(3)
                device['REMOVABLE'] = bool(int(name_match.group(4)))
                device['SIZE'] = name_match.group(5)
                device['READ_ONLY'] = bool(int(name_match.group(7)))
                # TYPE is enforced by the regex, no need to check here
                device['TYPE'] = name_match.group(8)
                mountpoint = name_match.group(9).strip()
                if len(mountpoint) > 0:
                    device['MOUNTPOINT'] = mountpoint
                if generation > 0:
                    device['PARENT_NAMES'] = parents[:generation]
                device_list.append(device)

        self.rows = [BlockDevice(d) for d in device_list]
        self.device_data = dict((dev.name, dev) for dev in self.rows)


@parser(Specs.lsblk_pairs)
class LSBlockPairs(BlockDevices):
    """Parse output of the ``lsblk -P -o`` command.

    ``lsblk`` command with ``-P -o`` options provides explicit selection of
    output columns in keyword=value pairs.

    The specific lsblk commands are ``/bin/lsblk -P -o column_names`` and
    ``/usr/bin/lsblk -P -o column_names``.  Typical content of the ``lsblk``
    command output looks like::

        ALIGNMENT="0" DISC-ALN="0" DISC-GRAN="0B" DISC-MAX="0B" DISC-ZERO="0" \
            FSTYPE="" GROUP="cdrom" KNAME="sr0" LABEL="" LOG-SEC="512" MAJ:MIN="11:0" \
            MIN-IO="512" MODE="brw-rw----" MODEL="DVD+-RW DVD8801 " MOUNTPOINT="" \
            NAME="sr0" OPT-IO="0" OWNER="root" PHY-SEC="512" RA="128" RM="1" RO="0" \
            ROTA="1" RQ-SIZE="128" SCHED="cfq" SIZE="1024M" STATE="running" TYPE="rom" UUID=""
        ALIGNMENT="0" DISC-ALN="0" DISC-GRAN="0B" DISC-MAX="0B" DISC-ZERO="0" \
            FSTYPE="" GROUP="disk" KNAME="sda" LABEL="" LOG-SEC="512" MAJ:MIN="8:0" \
            MIN-IO="512" MODE="brw-rw----" MODEL="WDC WD1600JS-75N" MOUNTPOINT="" \
            NAME="sda" OPT-IO="0" OWNER="root" PHY-SEC="512" RA="128" RM="0" RO="0" \
            ROTA="1" RQ-SIZE="128" SCHED="cfq" SIZE="149G" STATE="running" TYPE="disk" UUID=""
        ALIGNMENT="0" DISC-ALN="0" DISC-GRAN="0B" DISC-MAX="0B" DISC-ZERO="0" \
            FSTYPE="ext4" GROUP="disk" KNAME="sda1" LABEL="" LOG-SEC="512" MAJ:MIN="8:1" \
            MIN-IO="512" MODE="brw-rw----" MODEL="" MOUNTPOINT="/boot" NAME="sda1" \
            OPT-IO="0" OWNER="root" PHY-SEC="512" RA="128" RM="0" RO="0" ROTA="1" \
            RQ-SIZE="128" SCHED="cfq" SIZE="500M" STATE="" TYPE="part" \
            UUID="c7c4c016-8b00-4ded-bffb-5cc4719b7d45"

    Attributes:
        rows (list of BlockDevice): List of ``BlockDevice`` objects for each row of
            the input. Input column name matches key name except that
            any '-', ':', or '.' is replaced with
            '_' and the following names are changed::

                Column Name     Key Name
                RM              removable
                RO              read_only
        failed_device_paths (set): Set of device names that failed to get device path

    Note:
        ``PARENT_NAMES`` is not available as a key because it is not listed
        in the ``LsBlockPairs`` output and cannot always be correctly
        inferred from the other data present.
    """
    def parse_content(self, content):
        self.rows = []
        self.failed_device_paths = set()
        if "invalid option" in content[0] and "lsblk:" in content[0]:
            raise ParseException(content[0])
        for line in content:
            if ' TYPE=' not in line:
                if 'failed to get device path' in line:
                    self.failed_device_paths.add(line.split(":")[1].strip())
                    continue
                else:
                    raise ParseException(
                        "TYPE not found in LsBlockPairs line '{l}'".format(l=line)
                    )

            d = dict((k, v) for k, v in re.findall(r'(\S+)=\"(.*?)\"\s?', line) if len(v) > 0)

            def str2bool(s):
                return bool(int(s))

            for original, replace, transform in [("RM", "REMOVABLE", str2bool),
                                                 ("RO", "READ_ONLY", str2bool)]:
                if original in d:
                    d[replace] = transform(d[original]) if transform else d[original]
                    del d[original]
            self.rows.append(BlockDevice(d))
        self.device_data = dict((dev.name, dev) for dev in self.rows)
