"""
fstab - file ``/etc/fstab``
===========================

Parse the ``/etc/fstab`` file into a list of lines.  Each line is a dictionary
of fields, named according to their definitions in ``man fstab``:

* ``fs_spec`` - the device to mount
* ``fs_file`` - the mount point
* ``fs_vfstype`` - the type of file system
* ``raw_fs_mntops`` - the mount options as a string
* ``fs_mntops`` - the mount options as a dictionary
* ``fs_freq`` - the dump frequency
* ``fs_passno`` - check the filesystem on reboot in this pass number
* ``raw`` - the RAW line which is useful to front-end

``fs_freq`` and ``fs_passno`` are recorded as integers if found, and zero if
not present.

The ``fs_mntops`` mount options are converted to a dictionary, so that each
option's value set to True so it can be conveniently searched.

This data, as above, is available in the ``data`` property:

* As wrapped as an AttributeDict, each column can also be accessed as a property
  with the same name.
* The mount options are also an AttributeDict object with properties
  corresponding to the common mount options.

The data for each mount point is also available via the ``mounted_on``
property; the data is the same as that stored in the ``data`` list.

Typical content of the ``fstab`` looks like::

    #
    # /etc/fstab
    # Created by anaconda on Fri May  6 19:51:54 2016
    #
    /dev/mapper/rhel_hadoop--test--1-root /                       xfs     defaults        0 0
    UUID=2c839365-37c7-4bd5-ac47-040fba761735 /boot               xfs     defaults        0 0
    /dev/mapper/rhel_hadoop--test--1-home /home                   xfs     defaults        0 0
    /dev/mapper/rhel_hadoop--test--1-swap swap                    swap    defaults        0 0

    /dev/sdb1 /hdfs/data1 xfs rw,relatime,seclabel,attr2,inode64,noquota 0 0
    /dev/sdc1 /hdfs/data2 xfs rw,relatime,seclabel,attr2,inode64,noquota 0 0
    /dev/sdd1 /hdfs/data3 xfs rw,relatime,seclabel,attr2,inode64,noquota 0 0

    localhost:/ /mnt/hdfs nfs rw,vers=3,proto=tcp,nolock,timeo=600 0 0

    /dev/mapper/vg0-lv2     /test1     ext4 defaults,data=writeback     1 1
    nfs_hostname.redhat.com:/nfs_share/data     /srv/rdu/cases/000  nfs     ro,defaults,hard,intr,bg,noatime,nodev,nosuid,nfsvers=3,tcp,rsize=32768,wsize=32768     0

Examples:

    >>> fstab = shared[FSTab]
    >>> len(fstab)
    9
    >>> fstab.data[0]['fs_spec'] # Note that data is a list not a dict here
    '/dev/mapper/rhel_hadoop--test--1-root'
    >>> fstab.data[0].fs_spec
    '/dev/mapper/rhel_hadoop--test--1-root'
    >>> fstab.data[0].raw
    '/dev/mapper/rhel_hadoop--test--1-root /                       xfs    defaults        0 0'
    >>> fstab.data[0].fs_mntops.defaults
    True
    >>> 'relatime' in fstab.data[0].fs_mntops
    False
    >>> fstab.data[0].fs_mntops.get('relatime')
    None
    >>> fstab.mounted_on['/hdfs/data3'].fs_spec
    '/dev/sdd1'

"""

from collections import namedtuple

from .. import Parser, parser, get_active_lines, AttributeDict
from ..parsers import optlist_to_dict, parse_delimited_table

FS_HEADINGS = "fs_spec                               fs_file                 fs_vfstype raw_fs_mntops    fs_freq fs_passno"

type_info = namedtuple('type_info', field_names=['type', 'default'])


@parser("fstab")
class FSTab(Parser):
    """
    Parse the content of ``/etc/fstab``.

    This object provides the '__len__' and '__iter__' methods to allow it to
    be used as a list to iterate over the ``data`` data, e.g.::

        >>> if len(fstab) > 0:
        >>>     for fs in fstab:
        >>>         print fs.fs_file
        >>>         print fs.raw

    Attributes:
        data (list): a list of parsed fstab entries as AttributeDict objects.
        mounted_on (dict): a dictionary of AttributeDict objects keyed on mount
            point.
    """

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        for row in self.data:
            yield row

    def parse_content(self, content):
        """
        Parse each line in the file ``/etc/fstab``.
        """
        fstab_output = parse_delimited_table([FS_HEADINGS] + get_active_lines(content))
        self.data = []
        for line in fstab_output:
            line['fs_freq'] = int(line['fs_freq']) if 'fs_freq' in line else 0
            line['fs_passno'] = int(line['fs_passno']) if 'fs_passno' in line else 0
            # optlist_to_dict converts 'key=value' to key: value and
            # 'key' to key: True
            line['fs_mntops'] = AttributeDict(optlist_to_dict(line['raw_fs_mntops']))
            # add `raw` here for displaying convenience on front-end
            line['raw'] = [l for l in content if l.startswith(line['fs_spec'])][0]
            self.data.append(AttributeDict(line))
        # assert: all mount points of valid entries are unique by definition
        self.mounted_on = {row.fs_file: row for row in self.data}
