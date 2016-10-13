"""
Mount
=====
"""

from ..mappers import optlist_to_dict, ParseException
from .. import Mapper, mapper, get_active_lines


class AttributesAsDict(object):

    def __getitem__(self, item):
        return self.__dict__[item]

    def __contains__(self, item):
        return item in self.__dict__

    def get(self, item, default=None):
        return self.__dict__.get(item, default)


class MountOpts(AttributesAsDict):
    """Class for mount options for one mount entry.

    Provides mount options as attributes and may also
    be accessed as a dictionary.
    """
    def __init__(self, data):
        for k, v in data.iteritems():
            setattr(self, k, v)


class MountEntry(AttributesAsDict):
    """Class for a row of information from ``mount`` command.

    Contains all infomation from one row of the ``mount``
    command output.  Values are provided as attributes by
    column name except where column name is not a valid Python
    name.  All values may also be access in dictionary format
    or via the ``get`` method.
    """
    def __init__(self, data):
        for k, v in data.iteritems():
            setattr(self, k, MountOpts(v) if k == 'mount_options' else v)


@mapper('mount')
class Mount(Mapper):
    """Class of information for all output from ``mount`` command.

    Contains all rows of output from the ``mount`` command as
    ``MountEntry`` objects.
    """

    def __getitem__(self, item):
        return self.rows[item]

    def __len__(self):
        return len(self.rows)

    def __iter__(self):
        for row in self.rows:
            yield row

    def parse_content(self, content):
        """Parse each line of output from the ``mount`` command.

        The specific mount commands are ``/bin/mount`` and ``/usr/bin/mount``.
        Typical content of the ``mount`` command output looks like::
            sysfs on /sys type sysfs (rw,nosuid,nodev,noexec,relatime,seclabel)
            proc on /proc type proc (rw,nosuid,nodev,noexec,relatime)
            /dev/mapper/HostVG-Config on /etc/shadow type ext4 (rw,noatime,seclabel,stripe=256,data=ordered)
            dev/sr0 on /run/media/root/VMware Tools type iso9660 (ro,nosuid,nodev,relatime,uid=0,gid=0,iocharset=utf8,mode=0400,dmode=0500,uhelper=udisks2) [VMware Tools]

        Parameters
        ----------
        context: telemetry.rules.plugins.util.Content
            Context object providing file content for the ``/bin/mount`` command
            as well as metadata about the target system.

        Returns
        -------
        list
            A list of dictionaries containing information about each filesystem
            listed by the ``mount`` command.

            .. code-block:: python

            [
                { "filesystem": "/dev/mapper/HostVG-Config",
                  "mount_point": "/etc/shadow",
                  "mount_type": "ext4",
                  "mount_options": ["rw", "noatime", "seclabel", "stripe=256", "data=ordered"],
                  "mount_clause": "/dev/mapper/HostVG-Config on /etc/shadow type ext4 (rw,noatime,seclabel,stripe=256,data=ordered)"}
            ]

        """
        self.rows = []
        for line in get_active_lines(content):
            mount = {}
            try:
                mount['mount_clause'] = line
                mount['filesystem'], rest = line.split(' on ', 1)
                mount['mount_point'], rest = rest.split(' type ', 1)
                mount['mount_type'], rest = rest.split(' (', 1)
                mount_options, rest = rest.split(')', 1)
                mount['mount_options'] = optlist_to_dict(mount_options)
                if len(rest) > 0:
                    mount['mount_label'] = rest.strip(' []')
                self.rows.append(MountEntry(mount))
            except:
                raise ParseException("Mount unable to parse content: ", line)
