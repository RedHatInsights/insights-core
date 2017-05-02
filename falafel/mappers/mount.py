"""
mount - Command
===============

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

Examples:
    >>> mnt_info = shared[Mount]
    >>> mnt_info
    <falafel.mappers.mount.Mount at 0x7fd4a7d3bbd0>
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
"""

from ..mappers import optlist_to_dict, ParseException
from .. import Mapper, mapper, get_active_lines, AttributeDict


@mapper('mount')
class Mount(Mapper):
    """Class of information for all output from ``mount`` command.

    Attributes:
        rows (list of AttributeDict): List of ``AttributeDict`` objects for
            each row of the command output.

    Raises:
        ParseException: Raised when any problem parsing the command output.
    """
    def __getitem__(self, item):
        return self.rows[item]

    def __len__(self):
        return len(self.rows)

    def __iter__(self):
        for row in self.rows:
            yield row

    def parse_content(self, content):
        self.rows = []
        for line in get_active_lines(content):
            mount = {}
            try:
                mount['mount_clause'] = line
                mount['filesystem'], rest = line.split(' on ', 1)
                mount['mount_point'], rest = rest.split(' type ', 1)
                mount['mount_type'], rest = rest.split(' (', 1)
                mount_options, rest = rest.split(')', 1)
                mount['mount_options'] = AttributeDict(optlist_to_dict(mount_options))
                if len(rest) > 0:
                    mount['mount_label'] = rest.strip(' []')
                self.rows.append(AttributeDict(mount))
            except:
                raise ParseException("Mount unable to parse content: ", line)
