"""
Mount - command ``/bin/mount``
==============================

This module provides parsing for the ``mount`` command. The ``Mount`` class
implements parsing for the ``mount`` command output which looks like::

    sysfs on /sys type sysfs (rw,nosuid,nodev,noexec,relatime,seclabel)
    proc on /proc type proc (rw,nosuid,nodev,noexec,relatime)
    /dev/mapper/HostVG-Config on /etc/shadow type ext4 (rw,noatime,seclabel,stripe=256,data=ordered)
    dev/sr0 on /run/media/root/VMware Tools type iso9660 (ro,nosuid,nodev,relatime,uid=0,gid=0,iocharset=utf8,mode=0400,dmode=0500,uhelper=udisks2) [VMware Tools]

The information is stored as a list of ``AttributeDict`` objects.  Each
``AttributeDict`` object contains attributes for the following information that
are listed in the same order as in the command output::

    - filesystem: (str) Name of filesystem
    - mount_point: (str) Name of mount point for filesystem
    - mount_type: (str) Name of filesystem type
    - mount_options: (AttributeDict) Mount options as ``AttributeDict`` object
    - mount_label: (str) Only present if optional label is present
    - mount_clause: (str) Full string from command output

The `` mount_options`` contains the mount options as attributes accessible
via the attribute name as it appears in the command output.  For instance, the
options ``(rw,dmode=0500)`` may be accessed as ''mnt_row_info.rw`` with the value
``True`` and ``mnt_row_info.dmode`` with the value "0500".  The ``in`` operator
may be used to determine if an option is present.

MountEntry lines are also available in a ``mounts`` property, keyed on the
mount point.

Examples:
    >>> mnt_info = shared[Mount]
    >>> mnt_info
    <insights.parsers.mount.Mount at 0x7fd4a7d3bbd0>
    >>> len(mnt_info)
    4
    >>> mnt_info[3].__dict__
    {'filesystem': 'dev/sr0',
     'mount_clause': 'dev/sr0 on /run/media/root/VMware Tools type iso9660 (ro,nosuid,nodev,relatime,uid=0,gid=0,iocharset=utf8,mode=0400,dmode=0500,uhelper=udisks2) [VMware Tools]',
     'mount_label': 'VMware Tools',
     'mount_options': {'dmode': '0500', 'relatime': True, 'uid': '0',
         'iocharset': 'utf8', 'gid': '0', 'mode': '0400', 'ro': True,
         'nosuid': True, 'uhelper': 'udisks2', 'nodev': True}
     'mount_point': '/run/media/root/VMware Tools',
     'mount_type': 'iso9660'}
    >>> mnt_info[3].filesystem
    'dev/sr0'
    >>> mnt_info[3].mount_type
    'iso9660'
    >>> mnt_info[3].mount_options
    {'dmode': '0500', 'gid': '0', 'iocharset': 'utf8', 'mode': '0400', 'nodev': True,
     'nosuid': True, 'relatime': True, 'ro': True, 'uhelper': 'udisks2', 'uid': '0'}
    >>> mnt_info[3].mount_options.dmode
    >>> 'dmode' in mnt_info[3].mount_options
    True
    >>> mnt_info.mounts['/run/media/root/VMware Tools'].filesystem
    'dev/sr0'
"""

from ..parsers import optlist_to_dict, keyword_search
from .. import Parser, parser, get_active_lines, AttributeDict

import re


@parser('mount')
class Mount(Parser):
    """Class of information for all output from ``mount`` command.

    Attributes:
        rows (list of AttributeDict): List of ``AttributeDict`` objects for
            each row of the command output.

    Raises:
        ParseException: Raised when any problem parsing the command output.
    """

    def __len__(self):
        return len(self.rows)

    def __iter__(self):
        for row in self.rows:
            yield row

    def __getitem__(self, idx):
        if isinstance(idx, int):
            return self.rows[idx]
        elif isinstance(idx, str):
            return self.mounts[idx]
        else:
            raise TypeError("Mounts can only be indexed by mount string or line number")

    # /dev/mapper/fedora-home on /home type ext4 (rw,relatime,seclabel,data=ordered) [HOME]
    mount_line_re = r'^(?P<filesystem>\S+) on (?P<mount_point>.+?) type ' + \
        r'(?P<mount_type>\S+) \((?P<mount_options>[^)]+)\)' + \
        r'(?: \[(?P<mount_label>.*)\])?$'
    mount_line_rex = re.compile(mount_line_re)

    def parse_content(self, content):
        self.rows = []
        self.mounts = {}
        for line in get_active_lines(content):
            mount = {}
            mount['mount_clause'] = line
            match = self.mount_line_rex.search(line)
            if match:
                mount['filesystem'] = match.group('filesystem')
                mount['mount_point'] = match.group('mount_point')
                mount['mount_type'] = match.group('mount_type')
                mount_options = match.group('mount_options')
                mount['mount_options'] = AttributeDict(optlist_to_dict(mount_options))
                if match.group('mount_label'):
                    mount['mount_label'] = match.group('mount_label')
            else:
                mount['parse_error'] = 'Unable to parse line'

            entry = AttributeDict(mount)
            self.rows.append(entry)
            if match:
                self.mounts[mount['mount_point']] = entry

    def get_dir(self, path):
        """
        AttributeDict: returns the mount point that contains the given path.

        This finds the most specific mount path that contains the given path,
        by successively removing the directory or file name on the end of
        the path and seeing if that is a mount point.  This will always
        terminate since / is always a mount point.  Strings that are not
        absolute paths will return None.
        """
        import os
        while path != '':
            if path in self.mounts:
                return self.mounts[path]
            path = os.path.split(path)[0]
        return None

    def search(self, **kwargs):
        """
        Returns a list of the mounts (in order) matching the given criteria.
        Keys are searched for directly - see the
        :py:func:`insights.parsers.keyword_search` utility function for more
        details.  If no search parameters are given, no rows are returned.

        Examples:

            >>> mounts.search(filesystem='/dev/sda1')
            [{'filesystem': '/dev/sda1', 'mount_point': '/boot', ...}]
            >>> mounts.search(mount_options__contains='ro')
            [{'filesystem': '/dev/sr0', 'mount_point', '/mnt/CDROM', ...}, ...]

        Arguments:
            **kwargs (dict): Dictionary of key-value pairs to search for.

        Returns:
            (list): The list of mount points matching the given criteria.
        """
        return keyword_search(self.rows, **kwargs)
