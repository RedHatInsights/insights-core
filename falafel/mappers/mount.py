"""
``mount``
=========
"""

from falafel.core.plugins import mapper
from falafel.mappers import optlist_to_dict


@mapper('mount')
def get_mount(context):
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
    mount_list = []
    for line in context.content:
        mount = {}
        mount['mount_clause'] = line
        mount['filesystem'], rest = line.split(' on ', 1)
        mount['mount_point'], rest = rest.split(' type ', 1)
        mount['mount_type'], rest = rest.split(' (', 1)
        mount_options, rest = rest.split(')', 1)
        mount['mount_options'] = optlist_to_dict(mount_options)
        if len(rest) > 0:
            mount['mount_label'] = rest.strip(' []')
        mount_list.append(mount)
    return mount_list
