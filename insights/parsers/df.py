"""
Disk free space commands
========================

Module for the processing of output from the ``df`` command.  The base class
``DiskFree`` provides all of the functionality for all classes.
Data is avaliable as rows of the output contained
in one ``Record`` object for each line of output.

Sample input data for the ``df -li`` command looks like::

    Filesystem        Inodes  IUsed     IFree IUse% Mounted on
    /dev/mapper/vg_lxcrhel6sat56-lv_root
                     6275072 124955   6150117    2% /
    devtmpfs         1497120    532   1496588    1% /dev
    tmpfs            1499684    331   1499353    1% /dev/shm
    tmpfs            1499684    728   1498956    1% /run
    tmpfs            1499684     16   1499668    1% /sys/fs/cgroup
    tmpfs            1499684     54   1499630    1% /tmp
    /dev/sda2      106954752 298662 106656090    1% /home
    /dev/sda1         128016    429    127587    1% /boot
    tmpfs            1499684      6   1499678    1% /V M T o o l s
    tmpfs            1499684     15   1499669    1% /VM Tools

This module provides two parsers:

DiskFree_LI - command ``df -li``
--------------------------------

DiskFree_ALP - command ``df -alP``
----------------------------------

DiskFree_AL - command ``df -al``
--------------------------------

This example demonstrates the ``DiskFree_LI`` class but all classes will provide
the same functionality.

Examples:
    >>> df_info = shared[DiskFree_LI]
    >>> df_info.filesystem_names
    ['tmpfs', '/dev/mapper/vg_lxcrhel6sat56-lv_root', 'devtmpfs', '/dev/sda2', '/dev/sda1']
    >>> df_info.get_filesystem('/dev/sda2')
    [Record(filesystem='/dev/sda2', total='106954752', used='298662', available='106656090', capacity='1%', mounted_on='/home')]
    >>> df_info.mount_names
    ['/tmp', '/home', '/dev', '/boot', '/VM Tools', '/sys/fs/cgroup', '/', '/run', '/V M T o o l s', '/dev/shm']
    >>> df_info.get_mount('/boot')
    Record(filesystem='/dev/sda1', total='128016', used='429', available='127587', capacity='1%', mounted_on='/boot')
    >>> len(df_info)
    10
    >>> [d.mounted_on for d in df_info if 'sda' in d.filesystem]
    ['/home', '/boot']
    >>> df_info.data[0].filesystem
    '/dev/mapper/vg_lxcrhel6sat56-lv_root'
    >>> df_info.data[0]
    Record(filesystem='/dev/mapper/vg_lxcrhel6sat56-lv_root', total='6275072', used='124955', available='6150117', capacity='2%', mounted_on='/')
"""
from .. import parser, CommandParser
from collections import namedtuple, defaultdict

from insights.parsers import ParseException
from insights.specs import Specs

Record = namedtuple("Record", ['filesystem', 'total', 'used', 'available', 'capacity', 'mounted_on'])
"""namedtuple: Represents the information parsed from ``df`` command output."""


def parse_df_lines(df_content):
    """Parse contents of each line in ``df`` output.

    Parse each line of ``df`` output ensuring that wrapped lines are
    reassembled prior to parsing, and that mount names containing spaces
    are maintained.

    Parameters:
        df_content (list): Lines of df output to be parsed.

    Returns:
        list: A list of ``Record`` ``namedtuple``'s. One for each line of the
        ``df`` output with columns as the key values. The fields of
        ``Record`` provide information about the file system attributes
        as determined by the arguments to the ``df`` command.  So, for
        example, if ``df`` is given the ``-alP``, the values are in
        terms of 1024 blocks.  If ``-li`` is given, then the values are
        in terms of inodes::

            - filesystem: Name of the filesystem
            - total: total number of resources on the filesystem
            - used: number of the resources used on the filesystem
            - available: number of the resource available on the filesystem
            - capacity: percentage of the resource used on the filesystem
            - mounted_on: mount point of the filesystem
    """
    df_ls = {}
    df_out = []
    is_sep = False
    columns = Record._fields
    for line in df_content[1:]:  # [1:] -> Skip the header
        # Stop at 5 splits to avoid splitting spaces in path
        line_splits = line.rstrip().split(None, 5)
        if len(line_splits) >= 6:
            for i, name in enumerate(columns):
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
            for i, name in enumerate(columns[1:]):
                df_ls[name] = line_splits[i]
            is_sep = False
        elif not line_splits:  # Skip empty lines (might in sosreport)
            continue
        else:
            raise ParseException("Could not parse line '{l}'".format(l=line))
        # Only add this record if we've got a line and it's not separated
        if df_ls and not is_sep:
            rec = Record(**df_ls)
            df_out.append(rec)
            df_ls = {}
    return df_out


class DiskFree(CommandParser):
    """Class to provide methods used by all ``df`` command classes.

    Attributes:
        data (list of Record): List of ``Record`` objects for each line of command
            output.
        filesystems (dict of list): Dictionary with each entry being a
            list of ``Record`` objects, for all lines in the command output. The
            dictionary is keyed by the ``filesystem`` value of the Record.
        mounts (dict): Dictionary with each entry being a ``Record`` object
            corresponding to the ``mounted_on`` key.
    """
    def __init__(self, context):
        super(DiskFree, self).__init__(context)
        filesystems = defaultdict(list)
        self.mounts = {}
        for datum in self.data:
            filesystems[datum.filesystem].append(datum)
            self.mounts[datum.mounted_on] = datum
        self.filesystems = dict(filesystems)

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        for row in self.data:
            yield row

    def parse_content(self, content):
        self.data = parse_df_lines(content)

    @property
    def filesystem_names(self):
        """list: Returns list of unique filesystem names."""
        return self.filesystems.keys()

    def get_filesystem(self, name):
        """str: Returns list of Record objects for filesystem ``name``."""
        return self.filesystems.get(name, [])

    @property
    def mount_names(self):
        """list: Returns list of unique mount point names."""
        return self.mounts.keys()

    def get_mount(self, name):
        """Record: Returns Record obj for mount point ``name``."""
        return self.mounts.get(name)

    def get_dir(self, path):
        """
        Record: returns the Record object that contains the given path.

        This finds the most specific mount path that contains the given path.
        """
        try:
            longest = max(m for m in self.mounts if path.startswith(m))
            return self.mounts[longest]
        except ValueError:
            return None


@parser(Specs.df__li)
class DiskFree_LI(DiskFree):
    """Parse lines from the output of the ``df -li`` command.

    Typical content of the ``df -li`` command output looks like::

        Filesystem        Inodes  IUsed     IFree IUse% Mounted on
        /dev/mapper/vg_lxcrhel6sat56-lv_root
                         6275072 124955 6150117    2% /
        devtmpfs         1497120    532   1496588    1% /dev
        tmpfs            1499684    331   1499353    1% /dev/shm
        tmpfs            1499684    728   1498956    1% /tmp
        /dev/sda2      106954752 298662 106656090    1% /home
        /dev/sda1         128016    429    127587    1% /boot
        tmpfs            1499684      6   1499678    1% /run/user/988
        tmpfs            1499684     15   1499669    1% /run/user/100

    Attributes:
        data (list): A list of the ``df`` information with one ``Record`` object for
            each line of command output. Mapping of input columns to output
            fields is::

                Input column   Output Field
                ------------   ------------
                Filesystem     filesystem
                Inodes         total
                IUsed          used
                IFree          available
                IUse%          capacity
                Mounted on     mounted_on
    """
    pass


@parser(Specs.df__alP)
class DiskFree_ALP(DiskFree):
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

    Attributes:
        data (list): A list of the ``df`` information with one ``Record`` object for
            each line of command output. Mapping of input columns to output
            fields is::

                Input column   Output Field
                ------------   ------------
                Filesystem     filesystem
                1024-blocks    total
                Used           used
                Available      available
                Capacity       capacity
                Mounted on     mounted_on
    """
    pass


@parser(Specs.df__al)
class DiskFree_AL(DiskFree):
    """Parse lines from the output of the ``df -al`` command.

    Typical content of the ``df -al`` command looks like::

        Filesystem                             1K-blocks      Used Available     Use% Mounted on
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

    Attributes:
        data (list): A list of the ``df`` information with one ``Record`` object for
            each line of command output. Mapping of input columns to output
            fields is::

                Input column   Output Field
                ------------   ------------
                Filesystem     filesystem
                1K-blocks      total
                Used           used
                Available      available
                Use%           capacity
                Mounted on     mounted_on
    """
    pass
