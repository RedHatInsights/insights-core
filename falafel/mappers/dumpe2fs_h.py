from falafel.core.plugins import mapper

FITLER = ['Filesystem features', 'Default mount options']

@mapper('dumpe2fs-h', FITLER)
def get_dumpe2fs_output(context):
    """
    Parse each line in the output of /sbin/dumpe2fs -h /dev/device

    ------------------------------Sample of the output ---------------------------------------
    dumpe2fs 1.41.12 (17-May-2010)
    Filesystem volume name:   <none>
    Last mounted on:          /usr
    Filesystem UUID:          1b332c5d-2410-4934-9118-466f8a14841f
    Filesystem magic number:  0xEF53
    Filesystem revision #:    1 (dynamic)
    Filesystem features:      has_journal ext_attr resize_inode dir_index filetype needs_recovery extent flex_bg sparse_super large_file huge_file uninit_bg dir_nlink extra_isize
    Filesystem flags:         signed_directory_hash
    Default mount options:    user_xattr acl
    ------------------------------------------------------------------------------------------------

    Return a dict:
    { "/dev/device" :
            {
                "Last mounted on" : "/usr",
                "Filesystem UUID": "1b332c5d-2410-4934-9118-466f8a14841f",
                "Filesystem magic number":  "0xEF53"
            }
    }
    """
    dumpe2fs_output = {}
    dumpe2fs_values_dict = {}
    for line in context.content:
        if line and ":" in line:
            key, value = line.split(":", 1)
            if key in FITLER:
                dumpe2fs_values_dict[key] = list(value.strip().split())
            else:
                dumpe2fs_values_dict[key] = value.strip()
    dev_name = context.path.split('dumpe2fs_-h_')[-1].replace('.', '/')
    dumpe2fs_output[dev_name] = dumpe2fs_values_dict
    return dumpe2fs_output
