import shlex
from falafel.core.plugins import mapper


@mapper("blkid")
def get_blkid_info(context):
    """
    Parse each line in the output of "blkid -c /dev/null"

    ------------------------------Sample of the blkid output ---------------------------------------
    /dev/sda1: UUID="3676157d-f2f5-465c-a4c3-3c2a52c8d3f4" TYPE="xfs"
    /dev/sda2: UUID="UVTk76-UWOc-vk7s-galL-dxIP-4UXO-0jG4MH" TYPE="LVM2_member"
    /dev/mapper/rhel_hp--dl160g8--3-root: UUID="11124c1d-990b-4277-9f74-c5a34eb2cd04" TYPE="xfs"
    /dev/mapper/rhel_hp--dl160g8--3-swap: UUID="c7c45f2d-1d1b-4cf0-9d51-e2b0046682f8" TYPE="swap"
    /dev/mapper/rhel_hp--dl160g8--3-home: UUID="c7116820-f2de-4aee-8ea6-0b23c6491598" TYPE="xfs"
    /dev/mapper/rhel_hp--dl160g8--3-lv_test: UUID="d403bcbd-0eea-4bff-95b9-2237740f5c8b" TYPE="ext4"
    /dev/cciss/c0d1p3: LABEL="/u02" UUID="004d0ca3-373f-4d44-a085-c19c47da8b5e" TYPE="ext3"
    /dev/cciss/c0d1p2: LABEL="/u01" UUID="ffb8b27e-5a3d-434c-b1bd-16cb17b0e325" TYPE="ext3"
    /dev/loop0: LABEL="Satellite-5.6.0 x86_64 Disc 0" TYPE="iso9660"
    ------------------------------------------------------------------------------------------------

    Return a dict which key is the non-repeated 'device name' as below

    { "/dev/sda1" :
        {
            'UUID': '3676157d-f2f5-465c-a4c3-3c2a52c8d3f4',
            'TYPE': 'xfs'
        },
      "/dev/cciss/c0d1p3" :
        {
            'LABEL': '/u02',
            'UUID': '004d0ca3-373f-4d44-a085-c19c47da8b5e',
            'TYPE': 'ext3'
        }
    }
    """
    blkid_output = {}
    for line in context.content:
        if line.strip():
            para_dict = {}
            line_split = shlex.split(line)
            dev_name = line_split[0].strip(':')
            para_line = line_split[1:]
            for item in para_line:
                (k, v) = item.split('=', 1)
                para_dict[k] = v.strip('"')
            blkid_output[dev_name] = para_dict
    return blkid_output
