"""
Mount - command ``/bin/mount``
==============================

This module provides parsing for the ``mount`` command. The ``Mount`` class
implements parsing for the ``mount`` command output which looks like::

    sysfs on /sys type sysfs (rw,nosuid,nodev,noexec,relatime,seclabel)
    proc on /proc type proc (rw,nosuid,nodev,noexec,relatime)
    /dev/mapper/HostVG-Config on /etc/shadow type ext4 (rw,noatime,seclabel,stripe=256,data=ordered)
    dev/sr0 on /run/media/root/VMware Tools type iso9660 (ro,nosuid,nodev,relatime,uid=0,gid=0,iocharset=utf8,mode=0400,dmode=0500,uhelper=udisks2) [VMware Tools]

The information is stored as a list of :class:`MountEntry` objects.  Each
:class:`MountEntry` object contains attributes for the following information that
are listed in the same order as in the command output:

 * ``filesystem`` - Name of filesystem
 * ``mount_point`` - Name of mount point for filesystem
 * ``mount_type`` - Name of filesystem type
 * ``mount_options`` - Mount options as a dictionary
 * ``mount_label`` - Only present if optional label is present
 * ``mount_clause`` - Full string from command output

The ``mount_options`` is wrapped as a :class:`MountOpts` object which contains
below fixed attributes:

* ``rw`` - Read write
* ``ro`` - Read only
* ``defaults`` - Use default options: rw, suid, dev, exec, auto, nouser, async, and relatime
* ``relatime`` - Inode access times relative to modify or change time
* ``seclabel`` - `seclabel` is enabled or not
* ``attr2`` - `opportunistic` improvement is enabled or not
* ``inode64`` - `inode64` is enabled or not
* ``noquota`` - Disk quotas are enforced or not

For instance, the option ``rw`` in ``(rw,dmode=0500)`` may be accessed as
``mnt_row_info.rw`` with the value ``True``, the ``dmode`` can be accessed as
``mnt_row_info.dmode`` with the value ``0500``.

MountEntry lines are also available in a ``mounts`` property, keyed on the
mount point.

Examples:
    >>> type(mnt_info)
    <class 'insights.parsers.mount.Mount'>
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
    >>> mnt_info[3].mount_options.ro
    True
    >>> mnt_info.mounts['/run/media/root/VMware Tools'].filesystem
    'dev/sr0'
"""

import re
from insights.specs import Specs
from ..parsers import optlist_to_dict, keyword_search, ParseException
from .. import parser, get_active_lines, LegacyItemAccess, CommandParser


class MountOpts(object):
    """
    An object representing the mount options found in mount or fstab entry.
    Each option in the comma-separated list is a key, and 'key=value'
    pairs such as 'gid=5' are split so that e.g. the key is 'gid' and the value
    is '5'.  Otherwise, the key is the option name and its value is 'True'.

    In addition, the following attributes will always be available and are
    False if not defined in the options list.

    Attributes:
        rw (bool): Read write
        ro (bool): Read only
        defaults: (bool): Use default options: rw, suid, dev, exec, auto, nouser, async, and relatime
        relatime (bool): Inode access times relative to modify or change time
        seclabel (bool): "seclabel" is enabled or not
        attr2 (bool): "opportunistic" improvement is enabled or not
        inode64 (bool): "inode64" is enabled or not
        noquota (bool): Disk quotas are enforced or not
    """
    attrs = {
        'rw': False,
        'ro': False,
        'defaults': False,
        'relatime': False,
        'seclabel': False,
        'attr2': False,
        'inode64': False,
        'noquota': False
    }

    def __init__(self, data={}):
        # Use '_data' but not 'data' since the 'data' could be an mount option
        self._data = data
        for k, v in MountOpts.attrs.items():
            if k not in data:
                setattr(self, k, v)
        for k, v in data.items():
            setattr(self, k, v)

    def __getitem__(self, item):
        return self._data[item]

    def __contains__(self, item):
        return item in self._data

    def get(self, item, default=None):
        """Returns value of key ``item`` in self._data or ``default``
        if key is not present.

        Parameters:
            item: Key to get from ``self.data``.
            default: Default value to return if key is not present.

        Returns:
            (str): String value of the stored item, or the default if not found.
        """
        return self._data.get(item, default)

    def items(self):
        """
        To keep backward compatibility and let it can be iterated as a
        dictionary.
        """
        for k, v in self._data.items():
            yield k, v


class MountEntry(LegacyItemAccess, CommandParser):
    """
    An object representing an entry in the output of ``mount`` command.  Each
    entry contains below fixed attributes:

    Attributes:
        mount_clause (str): Full string from command output
        filesystem (str): Name of filesystem
        mount_point (str): Name of mount point for filesystem
        mount_type (str): Name of filesystem type
        mount_options (MountOpts): Mount options as a :class:`insights.parsers.mount.MountOpts` object
    """
    attrs = {
            'mount_clause': '',
            'filesystem': '',
            'mount_point': '',
            'mount_type': '',
            'mount_options': MountOpts(),
    }

    def __init__(self, data={}):
        self.data = data
        for k, v in MountEntry.attrs.items():
            if k not in data:
                setattr(self, k, v)
        for k, v in data.items():
            setattr(self, k, v)

    def items(self):
        """
        To keep backward compatibility and let it can be iterated as a
        dictionary.
        """
        for k, v in self.data.items():
            yield k, v


@parser(Specs.mount)
class Mount(CommandParser):
    """Class of information for all output from ``mount`` command.

    Attributes:
        rows (list of MountEntry): List of :class:`MountEntry` objects for
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
                mount['mount_options'] = MountOpts(optlist_to_dict(mount_options))
                if match.group('mount_label'):
                    mount['mount_label'] = match.group('mount_label')
            else:
                mount['parse_error'] = 'Unable to parse line'

            entry = MountEntry(mount)
            self.rows.append(entry)
            if match:
                self.mounts[mount['mount_point']] = entry

        if '/' not in self.mounts:
            raise ParseException("Input for mount must contain '/' mount point.")

    def get_dir(self, path):
        """
        MountEntry: returns the mount point that contains the given path.

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
