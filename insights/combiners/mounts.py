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
from insights.core.plugins import combiner
from insights.parsers import keyword_search
from insights.parsers.mount import Mount, ProcMounts, MountInfo
from insights.parsers.mount import MountEntry, MountAddtlInfo


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
            addtlinfo = {}
            if this_binmount:
                if 'mount_label' in this_binmount:
                    addtlinfo['mount_label'] = this_binmount['mount_label']
                addtlinfo['mount_clause_binmount'] = this_binmount['mount_clause']
            if this_procmounts:
                addtlinfo['fs_freq'], addtlinfo['fs_passno'] = this_procmounts['mount_label']
                addtlinfo['mount_clause_procmounts'] = this_procmounts['mount_clause']
            if this_mountinfo:
                for k, v in this_mountinfo['mount_addtlinfo'].items():
                    addtlinfo[k] = v
                addtlinfo['mount_clause_mountinfo'] = this_mountinfo['mount_clause']
            entry_addtlinfo = MountAddtlInfo(addtlinfo)

            # create MountEntry
            source_mount = this_mountinfo if this_mountinfo else (
                            this_procmounts if this_procmounts else this_binmount)
            basicinfo = {}
            basicinfo['mount_point'] = mount_point
            basicinfo['mount_source'] = source_mount.get('mount_source') or source_mount.get('filesystem')
            basicinfo['mount_type'] = source_mount.get('mount_type')
            basicinfo['mount_options'] = source_mount.get('mount_options')
            basicinfo['mount_addtlinfo'] = entry_addtlinfo
            entry_info = MountEntry(basicinfo)

            self._mounts[mount_point] = entry_info
            self.rows = sorted(self._mounts.values(), key=lambda r:
                        (r.mount_addtlinfo.get('mount_id', '-1'), r.mount_point))

    @property
    def mount_points(self):
        """
        Returns:
            (list): list of `mount_point` for each mount entry
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
        return keyword_search(self.rows, **kwargs)

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
            MountEntry : a object that represents a mount entry
        """
        return self._mounts.get(mount_point)

    def __len__(self):
        return len(self._mounts)

    def __iter__(self):
        for row in self.rows:
            yield row
