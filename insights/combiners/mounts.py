"""
Mounts
======

This combiner provides information about mount entries.
More specifically this consolidates data from
:py:class:`insights.parsers.mount.Mount`,
:py:class:`insights.parsers.mount.ProcMounts` and
:py:class:`insights.parsers.mount.MountInfo`.

Examples:

    >>> type(mounts)
    <class 'insights.combiners.mounts.Mounts'>
    >>> len(mounts)
    19
    >>> '/boot' in mounts
    True
    >>> mounts['/boot'].mount_source
    '/dev/sda1'
    >>> mounts['/boot'].mount_options.get('data')
    'ordered'
    >>> mounts['/boot'].mount_addtlinfo.major_minor
    '8:1'
"""

import os
from collections import namedtuple
from insights.core.plugins import combiner
from insights.parsers import keyword_search
from insights.parsers.mount import Mount, ProcMounts, MountInfo

MOUNTADDTLINFO_FIELD_NAMES = [
    "mount_label",
    "fs_freq",
    "fs_passno",
    "mount_id",
    "parent_id",
    "major_minor",
    "root",
    "optional_fields",
    "mount_clause_binmount",
    "mount_clause_procmounts",
    "mount_clause_mountinfo",
]
MountAddtlInfo = namedtuple("MountAddtlInfo", field_names=MOUNTADDTLINFO_FIELD_NAMES)
"""
A namedtuple object representing the additional infomation for a mount entry.
For a missing field, default to an empty string

Attributes:
    mount_label (str): Label of this mount entry from command ``/bin/mount``
    fs_freq (str): fs_freq of this mount entry from file ``/proc/mounts``
    fs_passno (str): fs_passno of this mount entry from file ``/proc/mounts``
    mount_id (str): Unique identifier of the mount
    parent_id (str): Unique identifier of the parent mount
    major_minor (str): Value of st_dev for files on filesystem
    root (str): Root of the mount within the filesystem
    optional_fields (str): Zero or more fields of the form "tag[:value]"
    mount_clause_binmount (str): Full raw string from command ``/bin/mount``
    mount_clause_procmounts (str): Full raw string from file ``/proc/mounts``
    mount_clause_mountinfo (str): Full raw string from file ``/proc/self/mountinfo``
"""

MOUNTENTRY_FIELD_NAMES = [
    "mount_source",
    "mount_point",
    "mount_type",
    "mount_options",
    "mount_addtlinfo",
]
MountEntry = namedtuple("MountEntry", field_names=MOUNTENTRY_FIELD_NAMES)
"""
A namedtuple object representing a mount entry.

Attributes:
    mount_source (str): Name of mounted device for filesystem
    mount_point (str): Name of mount point for filesystem
    mount_type (str): Name of filesystem type
    mount_options (dict): Mount options
    mount_addtlinfo (MountAddtlInfo): Additional mount information as namedtuple `MountAddtlInfo`
"""


@combiner([Mount, ProcMounts, MountInfo])
class Mounts(object):
    """
    ``Mounts`` combiner consolidates data from the parsers in
    ``insights.parsers.mounts`` module.

    Attributes:
        rows (list): list of :class:`MountEntry` objects for each mount entry
    """

    def __init__(self, binmount, procmounts, mountinfo):
        self._mounts = {}

        all_mount_points = set().union(
                    binmount.mounts.keys() if binmount else [],
                    procmounts.mounts.keys() if procmounts else [],
                    mountinfo.mounts.keys() if mountinfo else [])
        for mount_point in all_mount_points:
            this_binmount = binmount.get_dir(mount_point) if binmount else None
            this_procmounts = procmounts.get_dir(mount_point) if procmounts else None
            this_mountinfo = mountinfo.get_dir(mount_point) if mountinfo else None

            # create MountAddtlInfo
            addtlinfo = self.__init_a_addtlinfo()
            if this_binmount:
                if 'mount_label' in this_binmount:
                    addtlinfo['mount_label'] = this_binmount['mount_label']
                addtlinfo['mount_clause_binmount'] = this_binmount['mount_clause']
            if this_procmounts:
                addtlinfo['fs_freq'], addtlinfo['fs_passno'] = this_procmounts['mount_label']
                addtlinfo['mount_clause_procmounts'] = this_procmounts['mount_clause']
            if this_mountinfo:
                this_addtlinfo = this_mountinfo.get('mount_addtlinfo')
                for k in MOUNTADDTLINFO_FIELD_NAMES[3:8]:
                    addtlinfo[k] = this_addtlinfo.__getattribute__(k)
                addtlinfo['mount_clause_mountinfo'] = this_mountinfo['mount_clause']
            entry_addtlinfo = MountAddtlInfo(**addtlinfo)

            # create MountEntry
            source_mount = this_mountinfo if this_mountinfo else (
                            this_procmounts if this_procmounts else this_binmount)
            basicinfo = {}
            basicinfo['mount_point'] = mount_point
            basicinfo['mount_source'] = source_mount.get('mount_source') or source_mount.get('filesystem')
            basicinfo['mount_type'] = source_mount.get('mount_type')
            # covert `mount_options` into a real dict instead of MountOpts(AttributeAsDict)
            mount_ops = source_mount.get('mount_options')
            basicinfo['mount_options'] = dict([k, v] for k, v in mount_ops.items())
            basicinfo['mount_addtlinfo'] = entry_addtlinfo
            entry_info = MountEntry(**basicinfo)

            self._mounts[mount_point] = entry_info
            self.rows = sorted(self._mounts.values(), key=lambda r: (r.mount_addtlinfo[3], r.mount_point))

    @property
    def mount_points(self):
        """
        Returns:
            list: list of :str:`mount_point` for each mount entry
        """
        return list(self._mounts.keys())

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
            if path in self._mounts:
                return self._mounts[path]
            path = os.path.split(path)[0]
        return None

    def search(self, **kwargs):
        """
        Returns a list of the mounts matching the given criteria.
        Keys are searched for directly - see the
        :py:func:`insights.parsers.keyword_search` utility function for more
        details.  If no search parameters are given, no rows are returned.

        Arguments:
            **kwargs (dict): Dictionary of key-value pairs to search for.

        Returns:
            (list): The list of mount points matching the given criteria.

        Examples:

            >>> mounts.search(mount_point='/proc')[0]['mount_source']
            'proc'
            >>> mounts.search(mount_type__contains='nfs')[0]['mount_point']
            '/shared/dir1'
        """
        return keyword_search([r._asdict() for r in self.rows], **kwargs)

    def __contains__(self, mount_point):
        """
        Check if a specific mount_point is mounted.

        Args:
            mount_point (str): a mount_point string

        Returns:
            bool: True if mount_point is mounted, otherwise False
        """
        return mount_point in self._mounts

    def __getitem__(self, mount_point):
        """
        Retrieve a specific mount entry by its mount_point.

        Args:
            mount_point (str): a mount_point string

        Returns:
            MountEntry: a namedtuple that represents a mount entry
        """
        return self._mounts.get(mount_point)

    def __len__(self):
        return len(self._mounts)

    def __iter__(self):
        for row in self.rows:
            yield row

    def __init_a_addtlinfo(self):
        return dict([k, ''] for k in MOUNTADDTLINFO_FIELD_NAMES)
