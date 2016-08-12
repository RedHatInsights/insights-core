"""
``fstab``
=========
"""

from collections import namedtuple

from falafel.core.plugins import mapper
from falafel.core import MapperOutput
from falafel.util import parse_table
from falafel.mappers import get_active_lines, optlist_to_dict

FS_HEADINGS = "fs_spec                               fs_file                 fs_vfstype fs_mntops    fs_freq fs_passno"

type_info = namedtuple('type_info', field_names=['type', 'default'])


class MountOpts(MapperOutput):
    type_infos = {
        'rw': type_info(bool, False),
        'rq': type_info(bool, False),
        'ro': type_info(bool, False),
        'sw': type_info(bool, False),
        'xx': type_info(bool, False),
        'relatime': type_info(bool, False),
        'seclabel': type_info(bool, False),
        'attr2': type_info(bool, False),
        'inode64': type_info(bool, False),
        'noquota': type_info(bool, False)
    }

    def __init__(self, data, path=None):
        super(MountOpts, self).__init__(data, path)
        attrs = {}
        for k, v in data.iteritems():
            attrs[k] = v

        for k, v in MountOpts.type_infos.iteritems():
            if k not in data:
                attrs[k] = v.default

        for k, v in attrs.iteritems():
            setattr(self, k, v)


class FSTabEntry(MapperOutput):
    def __init__(self, data, path=None):
        super(FSTabEntry, self).__init__(data, path)
        for k, v in data.iteritems():
            if k != 'fs_mntops':
                self._add_to_computed(k, v)
            else:
                self._add_to_computed(k, MountOpts(v))


@mapper("fstab")
class FSTab(MapperOutput):
    def __init__(self, data, path=None):
        self.rows = []
        for datum in data:
            self.rows.append(FSTabEntry(datum))
        super(FSTab, self).__init__(data, path)

    def __len__(self):
        return len(self.rows)

    def __iter__(self):
        for row in self.rows:
            yield row

    @classmethod
    def parse_content(cls, content):
        """Parse each line in the file ``/etc/fstab``.

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

            nfs_hostname.redhat.com:/nfs_share/data     /srv/rdu/cases/000  nfs     ro,defaults,hard,intr,bg,noatime,nodev,nosuid,nfsvers=3,tcp,rsize=32768,wsize=32768     0

        Parameters
        ----------
        context: falafel.core.context.Context
            Context object providing file content for the ``/etc/fstab`` file as
            well as metadata about the target system.

        Returns
        -------
        list
            A list of dictionaries containing information about each filesystem
            defined in the ``/etc/fstab`` file.

            .. code-block:: python

            [
                { 'fs_spec': "UUID=2c839365-37c7-4bd5-ac47-040fba761735",
                  'fs_file': '/',
                  'fs_vfstype': 'xfs',
                  'fs_mntops': {'defaults': True},
                  'fs_freq': 0,
                  'fs_passno': 0 },
                { 'fs_spec': "/dev/sdb1",
                  'fs_file': '/hdfs/data1',
                  'fs_vfstype': 'xfs',
                  'fs_mntops': {'rw': True,
                                'relatime': True,
                                'seclabel': True,
                                'attr2': True,
                                'inode64': True,
                                'noquota': True },
                  'fs_freq': 0,
                  'fs_passno': 0 }
            ]

        """
        fstab_output = parse_table([FS_HEADINGS] + get_active_lines(content))
        for line in fstab_output:
            line['fs_freq'] = int(line['fs_freq']) if 'fs_freq' in line else 0
            line['fs_passno'] = int(line['fs_passno']) if 'fs_passno' in line else 0
            line['fs_vfstype'] = line['fs_vfstype']
            line['fs_mntops'] = optlist_to_dict(line['fs_mntops'])
        return fstab_output
