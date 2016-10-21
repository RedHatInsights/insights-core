"""
``dumpe2fs-h``
==============
"""

from .. import mapper, Mapper

COMPOUND_FIELDS = ['Filesystem features', 'Filesystem flags', 'Default mount options']


@mapper('dumpe2fs-h')
class DumpE2fs(Mapper):
    """Parse each line in the output of the ``dumpe2fs`` command.

    Typical contents of the ``/sbin/dumpe2fs -h /dev/device`` command looks
    like::

        dumpe2fs 1.41.12 (17-May-2010)
        Filesystem volume name:   <none>
        Last mounted on:          /usr
        Filesystem UUID:          1b332c5d-2410-4934-9118-466f8a14841f
        Filesystem magic number:  0xEF53
        Filesystem revision #:    1 (dynamic)
        Filesystem features:      has_journal ext_attr resize_inode dir_index filetype needs_recovery extent flex_bg sparse_super large_file huge_file uninit_bg dir_nlink extra_isize
        Filesystem flags:         signed_directory_hash
        Default mount options:    user_xattr acl

    Returns
    -------
    dict
        Single dictionary containing a key for the device and data
        returned from the ``dumpe2fs`` command as a dict of key/value pairs.

        .. code-block:: python
        { "/dev/device" :
                {
                    "Filesystem volume name": "<none>",
                    "Last mounted on" : "/usr",
                    "Filesystem UUID": "1b332c5d-2410-4934-9118-466f8a14841f",
                    "Filesystem magic number": "0xEF53",
                    "Filesystem revision #": "1 (dynamic)",
                    "Filesystem features": ["has_journal", "ext_attr", "resize_inode", "dir_index", "filetype", "needs_recovery",
                        "extent", "flex_bg", "sparse_super", "large_file", "huge_file", "uninit_bg", "dir_nlink", "extra_isize"],
                    "Filesystem flags: ["signed_directory_hash"],
                    "Default mount options: ["user_xattr", "acl"]
                    ...    # Other keys/values depending upon the device
                }
        }

    """
    def parse_content(self, content):
        dumpe2fs_values_dict = {}
        for line in content:
            if ":" in line:
                key, value = line.split(":", 1)
                if key in COMPOUND_FIELDS:
                    dumpe2fs_values_dict[key] = list(value.strip().split())
                else:
                    dumpe2fs_values_dict[key] = value.strip()
        dev_name = self.file_name.split('dumpe2fs_-h_')[-1].replace('.', '/')
        self.data = {dev_name: dumpe2fs_values_dict}


@mapper('dumpe2fs-h')
def get_dumpe2fs_output(context):
    """Deprecated, use DumpE2fs instead"""
    return DumpE2fs(context).data
