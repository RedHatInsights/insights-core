"""
FSTab - file ``/etc/fstab``
===========================

Parse the ``/etc/fstab`` file into a list of lines.  Each line is a dictionary
of fields, named according to their definitions in ``man fstab``:

* ``fs_spec`` - the device to mount
* ``fs_file`` - the mount point
* ``fs_vfstype`` - the type of file system
* ``fs_mntops`` - the mount options as a dictionary
* ``fs_freq`` - the dump frequency
* ``fs_passno`` - check the filesystem on reboot in this pass number
* ``raw_fs_mntops`` - the mount options as a string
* ``raw`` - the RAW line which is useful to front-end

``fs_freq`` and ``fs_passno`` are recorded as integers if found, and zero if
not present.

``fs_mntops`` is wrapped as a as a :class:`insights.parsers.mount.MountOpts`
object.  For instance, the option ``rw`` in ``rw,dmode=0500`` may be accessed as
``mnt_row_info.rw`` with the value ``True``, and the ``dmode`` can be accessed
as ``mnt_row_info.dmode`` with the value ``0500``.

This data, as above, is available in the ``data`` property:

* Wrapped as an :class:`FSTabEntry`, each column can also be accessed as an
  attribute with the same name.

The :class:`FSTabEntry` for each mount point is also available via the
:attr:`FSTab.mounted_on` property; the data is the same as that stored in the
:attr:`FSTab.data` list.

"""


from insights import Parser, parser, get_active_lines
from insights.specs import Specs
from insights.parsers import optlist_to_dict, parse_delimited_table, keyword_search
from insights.parsers.mount import MountOpts, AttributeAsDict

FS_HEADINGS = "fs_spec fs_file fs_vfstype raw_fs_mntops fs_freq fs_passno"


class FSTabEntry(AttributeAsDict):
    """
    An object representing an entry in ``/etc/fstab``.  Each entry contains
    below fixed attributes:

    Attributes:
        fs_spec (str): the device to mount
        fs_file (str): the mount point
        fs_vfstype (str): the type of file system
        fs_mntops (dict): the mount options as a :class:`insights.parser.mount.MountOpts`
        fs_freq (int): the dump frequency
        fs_passno (int): check the filesystem on reboot in this pass number
        raw_fs_mntops (str): the mount options as a string
        raw (str): the RAW line which is useful to front-end
    """
    pass


@parser(Specs.fstab)
class FSTab(Parser):
    """
    Parse the content of ``/etc/fstab``.

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

        >>> type(fstab)
        <class 'insights.parsers.fstab.FSTab'>
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


    Attributes:
        data (list): a list of parsed fstab entries as :class:`FSTabEntry` objects.
        mounted_on (dict): a dictionary of :class:`FSTabEntry` objects keyed on mount point.
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
        fstab_output = parse_delimited_table([FS_HEADINGS] + get_active_lines(content), raw_line_key='raw')
        self.data = []
        for line in fstab_output:
            line['fs_spec'] = line.get('fs_spec', '')
            line['fs_vfstype'] = line.get('fs_vfstype', '')
            # Decode fs_file to transfer the '\040' to ' '.
            # Encode first and then decode works for both Python2 and Python3.
            line['fs_file'] = line.get('fs_file', '').encode().decode("unicode-escape")
            line['fs_freq'] = int(line.get('fs_freq', '0'))
            line['fs_passno'] = int(line.get('fs_passno', '0'))
            # if there is no mntops, it is defaults.
            # (/dev/foo /foo somefs defaults   0 0) and (/dev/foo /foo somefs) are same
            line['raw_fs_mntops'] = line.get('raw_fs_mntops', 'defaults')
            # optlist_to_dict converts 'key=value' to key: value and 'key' to key: True
            line['fs_mntops'] = MountOpts(optlist_to_dict(line.get('raw_fs_mntops')))
            self.data.append(FSTabEntry(line))
        # assert: all mount points of valid entries are unique by definition
        self.mounted_on = dict((row.fs_file, row) for row in self.data)

    def search(self, **kwargs):
        """
        Search for the given key/value pairs in the data.  Please refer to the
        :py:meth:`insights.parsers.keyword_search` function documentation for
        a more complete description of how to use this.

        Fields that can be searched (as per ``man fstab``):

        * ``fs_spec``: the block special or remote filesystem path or label.
        * ``fs_file``: The mount point for the filesystem.
        * ``fs_vfstype``: The file system type.
        * ``fs_mntops``: The mount options.  Since this is also a dictionary,
          this can be searched using __contains - see the examples below.
        * ``fs_freq``: The dump frequency - rarely used.
        * ``fs_passno``: The pass for file system checks - rarely used.

        Examples:

            Search for the root file system:
                ``fstab.search(fs_file='/')``
            Search for file systems mounted from a LABEL declaration
                ``fstab.search(fs_spec__startswith='LABEL=')``
            Search for file systems that use the 'uid' mount option:
                ``fstab.search(fs_mntops__contains='uid')``
            Search for XFS file systems using the 'relatime' option:
                ``fstab.search(fs_vfstype='xfs', fs_mntops__contains='relatime')``
        """
        return keyword_search(self.data, **kwargs)

    def fsspec_of_path(self, path):
        """
        Return the device name if longest-matched mount-point of path is found,
        else None.
        If path contains any blank, pass it in directly or escape with '\040',
        eg: '/VM TOOLS/cache' or '/VM\040TOOLS/cache'
        """
        path = path.strip() if path else path
        if not path or not path.startswith('/'):
            return

        mos = self.mounted_on
        mps = sorted(mos, reverse=True)

        path = path if path.endswith('/') else path + '/'
        for mp in mps:
            tmp = mp if mp.endswith('/') else mp + '/'
            if path.startswith(tmp):
                return mos[mp].get('fs_spec', None)
