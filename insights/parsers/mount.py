"""
Mount Entries
=============

Parsers provided in this module includes:

Mount - command ``/bin/mount``
------------------------------

ProcMounts - file ``/proc/mounts``
----------------------------------


The ``Mount`` class implements parsing for the ``mount`` command output which looks like::

    /dev/mapper/rootvg-rootlv on / type ext4 (rw,relatime,barrier=1,data=ordered)
    proc on /proc type proc (rw,nosuid,nodev,noexec,relatime)
    /dev/mapper/HostVG-Config on /etc/shadow type ext4 (rw,noatime,seclabel,stripe=256,data=ordered)
    dev/sr0 on /run/media/root/VMware Tools type iso9660 (ro,nosuid,nodev,relatime,uid=0,gid=0,iocharset=utf8,mode=0400,dmode=0500,uhelper=udisks2) [VMware Tools]

The information is stored as a list of :class:`MountEntry` objects.  Each
:class:`MountEntry` object contains attributes for the following information that
are listed in the same order as in the command output:

 * ``filesystem`` or ``mounted_device`` - Name of filesystem or mounted device
 * ``mount_point`` - Name of mount point for filesystem
 * ``filesystem_type`` or ``mount_type`` - Name of filesystem type
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

"""

import os
from insights.specs import Specs
from insights.parsers import optlist_to_dict, keyword_search, ParseException, SkipException
from insights import parser, get_active_lines, CommandParser


class MountOpts(dict):
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
        data = {} if data is None else data
        self.update(data)
        for k, v in MountOpts.attrs.items():
            if k not in data:
                setattr(self, k, v)
        for k, v in data.items():
            setattr(self, k, v)


class MountEntry(dict):
    """
    An object representing an mount entry of ``mount`` command or
    ``/proc/mounts`` file.  Each entry contains below fixed attributes:

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
        data = {} if data is None else data
        self.update(data)
        for k, v in MountEntry.attrs.items():
            if k not in data:
                setattr(self, k, v)
        for k, v in data.items():
            setattr(self, k, v)


class MountedFileSystems(CommandParser):
    """
    Base Class for :class:`Mount` and :class:`ProcMounts`.

    Attributes:
        rows (list): List of :class:`MountEntry` objects for each row of the
            content.
        mounts (dict): Dict with the `mount_point` as the key and the
            :class:`MountEntry` objects as the value.

    Raises:
        SkipException: When the file is empty.
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

    def parse_content(self, content):
        # No content found or file is empty
        if not content:
            raise SkipException('Empty content')

        self._parse_mounts(content)

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

            >>> mounts.search(filesystem='proc')[0].mount_clause
            'proc on /proc type proc (rw,nosuid,nodev,noexec,relatime)'
            >>> mounts.search(mount_options__contains='seclabel')[0].mount_clause
            '/dev/mapper/HostVG-Config on /etc/shadow type ext4 (rw,noatime,seclabel,stripe=256,data=ordered)'

        Arguments:
            **kwargs (dict): Dictionary of key-value pairs to search for.

        Returns:
            (list): The list of mount points matching the given criteria.
        """
        return keyword_search(self.rows, **kwargs)


@parser(Specs.mount)
class Mount(MountedFileSystems):
    """
    Class of information for all output from ``mount`` command.

    .. note::
        Please refer to its super-class :class:`MountedFileSystems` for more
        details.

        >>> type(mnt_info)
        <class 'insights.parsers.mount.Mount'>
        >>> len(mnt_info)
        4
        >>> mnt_info[3].filesystem
        'dev/sr0'
        >>> mnt_info[3].mount_label
        '[VMware Tools]'
        >>> mnt_info[3].mount_type
        'iso9660'
        >>> mnt_info['/run/media/root/VMware Tools'].filesystem
        'dev/sr0'
        >>> mnt_info['/run/media/root/VMware Tools'].mount_label
        '[VMware Tools]'
        >>> mnt_info['/run/media/root/VMware Tools'].mount_options.ro
        True
    """
    def _parse_mounts(self, content):
        self.rows = []
        self.mounts = {}
        for line in get_active_lines(content):
            mount = {}
            mount['mount_clause'] = line
            # Get the mounted filesystem by checking the ' on '
            line_sp = _customized_split(line, line, sep=' on ')
            mount['filesystem'] = line_sp[0]
            # Get the mounted point by checking the last ' type ' before the last '('
            mnt_pt_sp = _customized_split(raw=line, l=line_sp[1], sep=' (', reverse=True)
            line_sp = _customized_split(raw=line, l=mnt_pt_sp[0], sep=' type ', reverse=True)
            mount['mount_point'] = line_sp[0]
            mount['mount_type'] = line_sp[1].split()[0]
            line_sp = _customized_split(raw=line, l=mnt_pt_sp[1], sep=None, check=False)
            mount['mount_options'] = MountOpts(optlist_to_dict(line_sp[0].strip('()')))
            if len(line_sp) == 2:
                mount['mount_label'] = line_sp[1]

            entry = MountEntry(mount)
            self.rows.append(entry)
            self.mounts[mount['mount_point']] = entry


@parser(Specs.mounts)
class ProcMounts(MountedFileSystems):
    """
    Class to parse the content of ``/proc/mounts`` file.

    This class is required to parse the ``/proc/mounts`` file in addition to the
    ``/bin/mount`` command because it lists the mount points of those process's
    which are not present in the output of the ``/bin/mount`` command.

    .. note::
        Please refer to its super-class :class:`MountedFileSystems` for more
        details.

    Examples:
        >>> type(proc_mnt_info)
        <class 'insights.parsers.mount.ProcMounts'>
        >>> len(proc_mnt_info)
        4
        >>> proc_mnt_info[3].filesystem == 'dev/sr0'
        True
        >>> proc_mnt_info[3].mounted_device == 'dev/sr0'
        True
        >>> proc_mnt_info[3].mounted_device == proc_mnt_info[3].filesystem
        True
        >>> proc_mnt_info[3].mount_type == 'iso9660'
        True
        >>> proc_mnt_info[3].filesystem_type == 'iso9660'
        True
        >>> proc_mnt_info['/run/media/root/VMware Tools'].mount_label == ['0', '0']
        True
        >>> proc_mnt_info['/run/media/root/VMware Tools'].mount_options.ro
        True
        >>> proc_mnt_info['/run/media/root/VMware Tools'].mounted_device == 'dev/sr0'
        True
    """

    def _parse_mounts(self, content):

        self.rows = []
        self.mounts = {}
        for line in get_active_lines(content):
            mount = {}
            mount['mount_clause'] = line
            # Handle the the '\040' in `mount_point`
            line_sp = line.encode().decode("unicode-escape")
            line_sp = _customized_split(raw=line, l=line)
            mount['filesystem'] = mount['mounted_device'] = line_sp[0]
            line_sp = _customized_split(raw=line, l=line_sp[1], num=3, reverse=True)
            mount['mount_label'] = line_sp[-2:]
            line_sp = _customized_split(raw=line, l=line_sp[0], reverse=True)
            mount['mount_options'] = MountOpts(optlist_to_dict(line_sp[1]))
            line_sp = _customized_split(raw=line, l=line_sp[0], reverse=True)
            mount['mount_type'] = mount['filesystem_type'] = line_sp[1]
            mount['mount_point'] = line_sp[0]

            entry = MountEntry(mount)
            self.rows.append(entry)
            self.mounts[mount['mount_point']] = entry


def _customized_split(raw, l, sep=None, num=2, reverse=False, check=True):
    if num >= 2:
        if reverse is False:
            line_sp = l.split(sep, num - 1)
        else:
            line_sp = l.rsplit(sep, num - 1)
        if check and len(line_sp) < num:
            raise ParseException('Unable to parse: "{0}"'.format(raw))
    return line_sp
