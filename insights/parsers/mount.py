"""
Mount Entries
=============

Parsers provided in this module includes:

Mount - command ``/bin/mount``
------------------------------

ProcMounts - file ``/proc/mounts``
----------------------------------

MountInfo - file ``/proc/self/mountinfo``
-----------------------------------------

The ``Mount`` class implements parsing for the ``mount`` command output which looks like::

    /dev/mapper/rootvg-rootlv on / type ext4 (rw,relatime,barrier=1,data=ordered)
    proc on /proc type proc (rw,nosuid,nodev,noexec,relatime)
    /dev/mapper/HostVG-Config on /etc/shadow type ext4 (rw,noatime,seclabel,stripe=256,data=ordered)
    dev/sr0 on /run/media/root/VMware Tools type iso9660 (ro,nosuid,nodev,relatime,uid=0,gid=0,iocharset=utf8,mode=0400,dmode=0500,uhelper=udisks2) [VMware Tools]

The information is stored as a list of :class:`MountEntry` objects.  Each
:class:`MountEntry` object contains attributes for the following information that
are listed in the same order as in the command output:

 * ``mount_source`` - Name of filesystem or the mounted device
 * ``mount_point`` - Name of mount point for filesystem
 * ``mount_type`` - Name of filesystem type
 * ``mount_options`` -  Mount options as ``MountOpts`` object
 * ``mount_label`` - Optional label of this mount entry, empty string by default
 * ``mount_addtlinfo`` - Additional mount information as ``MountAddtlInfo`` object
 * ``mount_clause`` - Full raw string from command output
 * ``filesystem`` - Name of filesystem or the mounted device (Deprecated)

``ProcMounts`` and ``MountInfo`` classes have the similar style as ``mount``.

MountEntry lines are also available in a ``mounts`` property, keyed on the
mount point.
"""
import os

from insights.core import CommandParser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.plugins import parser
from insights.parsers import get_active_lines, keyword_search, optlist_to_dict
from insights.specs import Specs


class AttributeAsDict(object):
    """
    Set the given key, value pair data as attribute of object.

    The ``in`` operator could be used to determine if an attribute exists before
    direct accessing.
    """

    def __init__(self, data=None):
        data = {} if data is None else data
        for k, v in data.items():
            setattr(self, k, v)

    def __contains__(self, item):
        return item in self.__dict__

    def __getitem__(self, item):
        return self.__dict__[item]

    def __len__(self):
        return len(self.__dict__)

    def get(self, item, default=None):
        return self.__dict__.get(item, default)

    def items(self):
        for k, v in self.__dict__.items():
            yield k, v


class MountOpts(AttributeAsDict):
    """
    An object representing the mount options found in mount or fstab entry as
    attributes accessible via the attribute name as it appears in the command
    output.  For instance, the options ``(rw,dmode=0500)`` may be accessed as
    ``mnt_row_info.rw`` with the value ``True`` and ``mnt_row_info.dmode``
    with the value "0500".
    """
    pass


class MountAddtlInfo(AttributeAsDict):
    """
    An object representing the additional information for an mount entry as
    attributes accessible via the attribute name.
    Object will provides different set of attributes according to different data
    sources.

    Attributes:
        mount_label (str): Label of this mount entry from command ``/bin/mount``
        fs_freq (str): fs_freq of this mount entry from file ``/proc/mounts``
        fs_passno (str): fs_passno of this mount entry from file ``/proc/mounts``
        mount_id (str): Unique identifier of the mount from file ``/proc/self/mountinfo``
        parent_id (str): Unique identifier of the parent mount from file ``/proc/self/mountinfo``
        major_minor (str): Value of st_dev for files on filesystem from file ``/proc/self/mountinfo``
        root (str): Root of the mount within the filesystem from file ``/proc/self/mountinfo``
        optional_fields (str): Zero or more fields of the form "tag[:value]" from file ``/proc/self/mountinfo``
        mount_clause_binmount (str): Full raw string from command ``/bin/mount``
        mount_clause_procmounts (str): Full raw string from file ``/proc/mounts``
        mount_clause_mountinfo (str): Full raw string from file ``/proc/self/mountinfo``

    For instance, the major:minor number ``253:4`` could be accessed as
    ``mnt_row_info.major_minor`` with the value ``253:4``.
    """
    pass


class MountEntry(AttributeAsDict):
    """
    An object representing an mount entry of ``mount`` command, ``/proc/mounts``
    or ``/proc/self/mountinfo`` file. Each entry contains below attributes:

    Attributes:
        mount_source(str): Name of filesystem of mounted device
        mount_point (str): Name of mount point for filesystem
        mount_type (str): Name of filesystem type
        mount_options (MountOpts): Mount options as :class:`MountOpts`
        mount_label (str): Optional label of this mount entry, an empty string by default
        mount_addtlinfo (MountAddtlInfo): Additional mount information as :class:`MountAddtlInfo`
        mount_clause (str): Full raw string from command output
        filesystem (str): Name of filesystem of mounted device (Deprecated, use
                `mount_source` instead)
    """
    pass


class MountedFileSystems(CommandParser):
    """
    Base Class for :class:`Mount`, :class:`ProcMounts` and :class:`MountInfo`.

    Attributes:
        rows (list): List of :class:`MountEntry` objects for each row of the
            content.
        mounts (dict): Dict with the `mount_point` as the key and the
            :class:`MountEntry` objects as the value.

    Raises:
        SkipComponent: When the file is empty.
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
            raise SkipComponent('Empty content')

        self._parse_mounts(content)

        if '/' not in self.mounts:
            raise ParseException("Input for mount must contain '/' mount point.")

    def get_dir(self, path):
        """
        This finds the most specific mount path that contains the given path,
        by successively removing the directory or file name on the end of
        the path and seeing if that is a mount point.  This will always
        terminate since / is always a mount point.  Strings that are not
        absolute paths will return None.

        Arguments:
            path (str): The path to check.
        Returns:
            MountEntry: The mount point that contains the given path.
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

    The typical output of ``mount`` command looks like::

        /dev/mapper/rootvg-rootlv on / type ext4 (rw,relatime,barrier=1,data=ordered)
        proc on /proc type proc (rw,nosuid,nodev,noexec,relatime)
        /dev/mapper/HostVG-Config on /etc/shadow type ext4 (rw,noatime,seclabel,stripe=256,data=ordered)
        dev/sr0 on /run/media/root/VMware Tools type iso9660 (ro,nosuid,nodev,relatime,uid=0,gid=0,iocharset=utf8,mode=0400,dmode=0500,uhelper=udisks2) [VMware Tools]

    Examples:

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
        >>> 'ro' in mnt_info[3].mount_options
        True
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
            mount['mount_source'] = line_sp[0]
            mount['filesystem'] = mount['mount_source']  # compatible for deprecation
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

    The typical content of ``/proc/mounts`` file looks like::

        /dev/mapper/rootvg-rootlv / ext4 rw,relatime,barrier=1,data=ordered 0 0
        proc /proc proc rw,nosuid,nodev,noexec,relatime 0 0
        /dev/mapper/HostVG-Config /etc/shadow ext4 rw,noatime,seclabel,stripe=256,data=ordered 0 0
        dev/sr0 /run/media/root/VMware\040Tools iso9660 ro,nosuid,nodev,relatime,uid=0,gid=0,iocharset=utf8,mode=0400,dmode=0500,uhelper=udisks2 0 0

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
            # Handle the '\040' in `mount_point`, e.g. "VMware\040Tools"
            line_sp = line.encode().decode("unicode-escape")
            line_sp = _customized_split(raw=line, l=line_sp)
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


@parser(Specs.mountinfo)
class MountInfo(MountedFileSystems):
    """
    Class to parse the content of ``/proc/self/mountinfo`` file.

    .. note::
        Please refer to its super-class :class:`MountedFileSystems` for more details.

    The typical content of ``/proc/self/mountinfo`` file looks like::

        39 0 253:0 / / rw,relatime shared:1 - xfs /dev/mapper/rootvg-lvlocroot rw,attr2,inode64,noquota
        47 39 8:1 / /boot rw,relatime shared:30 - xfs /dev/sda1 rw,attr2,inode64,noquota
        65 39 253:19 / /data rw,relatime shared:44 - ext4 /dev/mapper/vgdata-lvdata rw,data=ordered
        58 39 253:15 / /opt rw,relatime shared:45 - xfs /dev/mapper/rootvg-lvlocopt rw,attr2,inode64,noquota
        61 39 253:17 / /home rw,nosuid,relatime shared:46 - xfs /dev/mapper/rootvg-lvlochome rw,attr2,inode64,noquotao

    Examples:

        >>> type(proc_mountinfo)
        <class 'insights.parsers.mount.MountInfo'>
        >>> len(proc_mountinfo)
        5
        >>> proc_mountinfo[2].mount_source
        '/dev/mapper/vgdata-lvdata'
        >>> proc_mountinfo[2].mount_type
        'ext4'
        >>> proc_mountinfo[2].mount_point
        '/data'
        >>> 'data' in proc_mountinfo[2].mount_options
        True
        >>> proc_mountinfo[2].mount_options.data
        'ordered'
        >>> 'major_minor' in proc_mountinfo[4]
        False
        >>> 'major_minor' in proc_mountinfo[4].mount_addtlinfo
        True
        >>> proc_mountinfo[4].mount_addtlinfo.major_minor
        '253:17'
        >>> proc_mountinfo['/boot'].mount_source
        '/dev/sda1'
    """

    def _parse_mounts(self, content):
        rows = []
        for line in get_active_lines(content):
            mount = {}
            mount['mount_clause'] = line
            line_own_sp = _customized_split(line, line, sep=' - ')
            line_left_sp = _customized_split(line, line_own_sp[0], num=6)
            mount['mount_point'] = line_left_sp[4]
            line_right_sp = _customized_split(line, line_own_sp[1], num=3)
            mount['mount_type'] = line_right_sp[0]
            mount['mount_source'] = line_right_sp[1]
            mount['filesystem'] = mount['mount_source']  # compatible for deprecation
            optional_fields = line_left_sp[5].split()[1] if ' ' in line_left_sp[5] else ''
            mntopt = line_left_sp[5].split()[0] if ' ' in line_left_sp[5] else line_left_sp[5]
            unioned_options = ','.join([mntopt, line_right_sp[2]])
            mount['mount_options'] = MountOpts(optlist_to_dict(unioned_options))
            mount['mount_addtlinfo'] = MountAddtlInfo({
                    'mount_id': line_left_sp[0],
                    'parent_id': line_left_sp[1],
                    'major_minor': line_left_sp[2],
                    'root': line_left_sp[3],
                    'optional_fields': optional_fields,
            })
            entry = MountEntry(mount)
            rows.append(entry)
        self.rows = rows
        self.mounts = dict([mnt['mount_point'], rows[idx]] for idx, mnt in enumerate(rows))


def _customized_split(raw, l, sep=None, num=2, reverse=False, check=True):
    if num >= 2:
        if reverse is False:
            line_sp = l.split(sep, num - 1)
        else:
            line_sp = l.rsplit(sep, num - 1)
        if check and len(line_sp) < num:
            raise ParseException('Unable to parse: "{0}"'.format(raw))
    return line_sp
