"""
DF - Disk Free
==============
"""
from falafel.core.plugins import mapper


def parse_df_lines(columns, df_content):
    """Parse contents of each line in ``df`` output.

    Parsed each line of ``df`` output ensuring that wrapped lines are
    reassembled prior to parsing, and that mount names containing spaces
    are maintained.

    Parameters
    ----------
    columns: list
        list of column headings to be used as dictionary keys

    df_content: list
        lines of df output to be parsed

    Returns
    -------
    list
        A list of dictionaries for each line of the ``df`` output with
        columns as the key values.
    """
    # Parse the header as keys of the inner dict
    header_split = df_content[0].split(None, 5)
    # Update the keys according to the actual names in header line
    if len(header_split) == 6:
        columns[0:5] = header_split[0:5]
    df_ls = {}
    df_out = []
    is_sep = False
    for line in df_content[1:]:  # [1:] -> Skip the header
        line_splits = line.split()
        if len(line_splits) >= 6:
            # Re-split to avoid this kind of "Mounted on": "VMware Tools"
            line_splits = line.split(None, 5)
            for i, name in enumerate(columns[:-1]):
                df_ls[name] = line_splits[i]
            is_sep = False
        elif len(line_splits) == 1:
            # First line of the separated line
            df_ls[columns[0]] = line_splits[0]
            is_sep = True
        elif is_sep and len(line_splits) >= 5:
            # Re-split to avoid this kind of "Mounted on": "VMware Tools"
            line_splits = line.split(None, 4)
            # Last line of the separated line
            for i, name in enumerate(columns[1:-1]):
                df_ls[name] = line_splits[i]
            is_sep = False
        if not is_sep:
            # Last column is mount point
            df_ls[columns[-1]] = line_splits[-1]
            df_out.append(df_ls)
            df_ls = {}
    return df_out


@mapper('df_-li')
def df_li(context):
    """Parse lines from the output of the ``df -li`` command.

    Typical content of the ``df -li`` command output looks like::

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

    Parameters
    ----------
    context: falafel.core.context.Context
        Context object providing the file content for the ``df -li`` command
        as well as metadata about the target system.

    Returns
    -------
    list
        A list of the ``df`` information with one dictionary for each line
        of command output.  For example,

        .. code-block:: python

            [
                {
                    'Filesystem'    : 'tmpfs',
                    'Inodes'        : '1499684',
                    'IUsed'         : '331',
                    'IFree'         : '1499353',
                    'IUse%'         : '1%',
                    'Mounted_on'    : '/dev/shm'
                },
            ]

    """
    columns = ['Filesystem', 'Inodes', 'IUsed', 'IFree', 'IUse%', 'Mounted_on']
    return parse_df_lines(columns, context.content)


@mapper('df_-alP')
def df_alP(context):
    """Parse lines from the output of the ``df -alP`` command.

    Typical content of the ``df -alP`` command looks like::

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

    Parameters
    ----------
    context: falafel.core.context.Context
        Context object providing file content for the ``df -alP`` command as well
        as metadata about the target system.

    Returns
    -------
    list
        A list of the ``df`` information with one dictionary for each line of
        command output.  For example,

        .. code-block:: python

            [
                {
                    'Filesystem'    : 'tmpfs',
                    '1024-blocks'   : '5998736',
                    'Used'          : '491660',
                    'Available'     : '5507076',
                    'Capacity'      : '9%',
                    'Mounted_on'    : '/dev/shm'
                },
            ]

    """
    columns = ['Filesystem', '1024-blocks', 'Used', 'Available', 'Capacity', 'Mounted_on']
    return parse_df_lines(columns, context.content)
