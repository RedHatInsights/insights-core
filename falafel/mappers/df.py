"""
``df``
======
"""

from falafel.core.plugins import mapper
from falafel.util import parse_table


def unwrap_content(content):
    prev_line = None
    lines = []
    lines.append(content[0])
    for line in content[1:]:
        if line.startswith(" "):
            prev_line = "{} {}".format(prev_line, line)
        else:
            if prev_line is not None:
                lines.append(prev_line)
            prev_line = line
    lines.append(prev_line)
    return lines


@mapper('df_-li')
def df_li(context):
    """Parse lines from output of the ``df -li`` command.

    This command displays information about filesystems in terms of inodes.
    The output of the command may visually wrap to limit the total width of
    information displayed on the terminal.

    Typical content of the ``df -li`` command output looks like::

        Filesystem        Inodes  IUsed     IFree IUse% Mounted on
        /dev/mapper/vg_lxcrhel6sat56-lv_root
                         6275072 124955   6150117    2% /
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
    context: telemetry.rules.plugins.util.Content
        Context object providing command output content for the ``df -li``
        command as well as metadata about the target system.

    Returns
    -------
    list
        A list of dictionaries containing information about each filesystem
        listed by the ``df -li`` command.

        .. code-block:: python

        [
            { 'Filesystem'    : '/dev/mapper/vg_lxcrhel6sat56-lv_root',
              'Inodes'        : 6275072,
              'IUsed'         : 124955,
              'IFree'         : 6150117,
              'IUse%'         : '2%',
              'Mounted_on'    : '/'},
            { 'Filesystem'    : 'devtmpfs',
              'Inodes'        : 1497120,
              'IUsed'         : 532,
              'IFree'         : 1496588,
              'IUse%'         : '1%',
              'Mounted_on'    : '/dev'}
        ]

    """
    context.content[0] = context.content[0].replace("Mounted on", "Mounted_on")
    content = unwrap_content(context.content)
    return parse_table(content)


@mapper('df_-alP')
def df_alP(context):
    """Parse lines from output of the ``df -alP`` command.

    This command displays information about filesystems in Posix format.

    Typical content of the ``df -alP`` command output looks like::

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
    context: telemetry.rules.plugins.util.Content
        Context object providing command output content for the ``df -alP``
        command as well as metadata about the target system.

    Returns
    -------
    list
        A list of dictionaries containing information about each filesystem
        listed by the ``df -alP`` command.

        .. code-block:: python

        [
            {
                'Filesystem'    : 'tmpfs',
                '1024-blocks'   : '5998736',
                'Used'          : '491660',
                'Available'     : '5507076',
                'Capacity'      : '9%'
                'Mounted_on'    : '/dev/shm'
            },
        ]

    """
    context.content[0] = context.content[0].replace("Mounted on", "Mounted_on")
    return parse_table(context.content)
