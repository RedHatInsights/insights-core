from falafel.core.plugins import mapper
from falafel.core import MapperOutput
from falafel.mappers import get_active_lines

'''
1st column -> fs_spec: This field describes the block special device or remote filesystem to be mounted.
2nd column -> fs_file: This field describes the mount point for the filesystem.
3rd column -> fs_vfstype: This field describes the type of the filesystem.
4th column -> fs_mntops: This field describes the mount options associated with the filesystem.
5th column -> fs_freq: This field is used for these filesystems by the dump(8) command to determine which filesystems need to be dumped.
6th column -> fs_passno: This field is used by the fsck(8) program to determine the order in which filesystem checks are done at reboot time.

The returned data structure:
    [
        {
            "fs_spec": "/dev/mapper/vg_ec0glz1201-lv_swap"
            "fs_file": "swap"
            "fs_vfstype":  "swap"
            "fs_mntops": "defaults"
            "fs_freq": "1"
            "fs_passno": "1"
        },
        {
            "fs_spec": "LABEL=/home"
            "fs_file": "/home"
            "fs_vfstype":  "ext3"
            "fs_mntops": "defaults,rw"
            "fs_freq": "1"
            "fs_passno": "1"
        }
    ]
'''


class FilesystemList(MapperOutput):

    def parse_fstab(self):
        """
        Parses table-like fstab. Assumes the first
        row does not contains column names.
        """
        if not self.data:
            return []
        cols = ["fs_spec", "fs_file", "fs_vfstype", "fs_mntops", "fs_freq", "fs_passno"]
        return [dict(zip(cols, row.split())) for row in get_active_lines(self.data, "#")]

    def __contains__(self, s):
        return any(s in line.split() for line in self.data)


@mapper('fstab')
def fstab(context):
    """
    Returns a list of dicts, where the keys in each dict are the column defined
    in function parse_fstab() and each item in the list represents a filesystem.
    """
    return FilesystemList(context.content)
