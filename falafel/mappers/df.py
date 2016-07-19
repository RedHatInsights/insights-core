from falafel.core.plugins import mapper


def parse_df_lines(five_keys, df_content):
    """
    Parse each line in df output.
    - The df output might be separated to two line when the name of the
      filesystem is too long.
      But for a long "Mounted on", the output will not be separated.

    """
    # Parse the header as keys of the inner dict
    header_split = df_content[0].split(None, 5)
    # Update the keys according to the actual names in header line
    if len(header_split) == 6:
        five_keys = header_split[0:5]
    df_ls = {}
    df_out = {}
    is_sep = False
    for line in df_content[1:]:  # [1:] -> Skip the header
        line_splits = line.split()
        if len(line_splits) >= 6:
            # Re-split to avoid this kind of "Mounted on": "VMware Tools"
            line_splits = line.split(None, 5)
            for i, key in enumerate(five_keys):
                df_ls[key] = line_splits[i]
            is_sep = False
        elif len(line_splits) == 1:
            # First line of the separated line
            df_ls[five_keys[0]] = line_splits[0]
            is_sep = True
        elif is_sep and len(line_splits) >= 5:
            # Re-split to avoid this kind of "Mounted on": "VMware Tools"
            line_splits = line.split(None, 4)
            # Last line of the separated line
            for i, key in enumerate(five_keys[1:]):
                df_ls[key] = line_splits[i]
            is_sep = False
        if not is_sep:
            # The last 'Mounted on' is the key
            df_out[line_splits[-1]] = df_ls
            df_ls = {}
    return df_out


@mapper('df_-li')
def df_li(context):
    """
    ------------------ Output sample of df -li -------------------------------
    Filesystem        Inodes  IUsed     IFree IUse% Mounted on
    /dev/mapper/vg_lxcrhel6sat56-lv_root
                     6275072 124955 6150117    2% /
    devtmpfs         1497120    532   1496588    1% /dev
    tmpfs            1499684    331   1499353    1% /dev/shm
    tmpfs            1499684    728   1498956    1% /run
    tmpfs            1499684     16   1499668    1% /sys/fs/cgroup
    /dev/sda3       15728640 180293  15548347    2% /
    tmpfs            1499684     54   1499630    1% /tmp
    /dev/sda2      106954752 298662 106656090    1% /home
    /dev/sda1         128016    429    127587    1% /boot
    tmpfs            1499684      6   1499678    1% /run/user/988
    tmpfs            1499684     15   1499669    1% /run/user/100
    ------------------ Output sample of df -li -------------------------------

    Returns a dict where key is the non-repeating 'Mounted on', just like below:
    { "/dev/shm":
        {
            'Filesystem'    : 'tmpfs',
            'Inodes'        : '1499684',
            'IUsed'         : '331',
            'IFree'         : '1499353',
            'IUse%'         : '1%'
        },
    }
    """
    five_keys = ['Filesystem', 'Inodes', 'IUsed', 'IFree', 'IUse%']
    return parse_df_lines(five_keys, context.content)


@mapper('df_-alP')
def df_alP(context):
    """
    ----------------- Output sample of df -alP -------------------------------
    Filesystem                           1024-blocks      Used Available Capacity Mounted on
    /dev/mapper/vg_lxcrhel6sat56-lv_root    98571884   4244032  89313940       5% /
    sysfs                                          0         0         0        - /sys
    proc                                           0         0         0        - /proc
    devtmpfs                                 5988480         0   5988480       0% /dev
    securityfs                                     0         0         0        - /sys/kernel/security
    tmpfs                                    5998736    491660   5507076       9% /dev/shm
    devpts                                         0         0         0        - /dev/pts
    tmpfs                                    5998736      1380   5997356       1% /run
    tmpfs                                    5998736         0   5998736       0% /sys/fs/cgroup
    cgroup                                         0         0         0        - /sys/fs/cgroup/systemd
    ----------------- Output sample of df -alP -------------------------------

    Returns a dict where key is the non-repeating 'Mounted on', just like below:
    { "/dev/shm":
        {
            'Filesystem'    : 'tmpfs',
            '1024-blocks'   : '5998736',
            'Used'          : '491660',
            'Available'     : '5507076',
            'Capacity'      : '9%'
        },
    }
    """
    five_keys = ['Filesystem', '1024-blocks', 'Used', 'Available', 'Capacity']
    return parse_df_lines(five_keys, context.content)
