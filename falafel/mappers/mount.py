import re
from falafel.core.plugins import mapper

MOUNT_REGEX = re.compile(r'(.*) on (.*) type (\S+) \((.*)\)(.*)')


@mapper('mount')
def get_mount(context):
    """
    The format of command /usr/bin/mount output will be like:
    sysfs on /sys type sysfs (rw,nosuid,nodev,noexec,relatime,seclabel)
    proc on /proc type proc (rw,nosuid,nodev,noexec,relatime)
    /dev/mapper/HostVG-Config on /etc/shadow type ext4 (rw,noatime,seclabel,stripe=256,data=ordered) [CONFIG]
    dev/sr0 on /run/media/root/VMware Tools type iso9660 (ro,nosuid,nodev,relatime,uid=0,gid=0,iocharset=utf8,mode=0400,dmode=0500,uhelper=udisks2) [VMware Tools]
    This function returns a list of directory that includes mount point key-value info
    """
    mount_list = []
    for line in context.content:
        if line:
            m = MOUNT_REGEX.match(line)
            if m:
                mount_dict = {}
                mount_dict["filesystem"] = m.group(1)
                mount_dict["mount_point"] = m.group(2)
                mount_dict["mount_type"] = m.group(3)
                mount_dict["mount_options"] = m.group(4).split(",")
                mount_dict["mount_clause"] = line
                mount_list.append(mount_dict)
    return mount_list
