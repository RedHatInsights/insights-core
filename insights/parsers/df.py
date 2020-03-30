"""
Disk free space commands
========================

Module for the processing of output from the ``df`` command.  The base class
``DiskFree`` provides all of the functionality for all classes.
Data is avaliable as rows of the output contained in one ``Record`` object
for each line of output.

Parsers contained in this module are:

DiskFree_LI - command ``df -li``
--------------------------------

DiskFree_ALP - command ``df -alP``
----------------------------------

DiskFree_AL - command ``df -al``
--------------------------------

"""
from collections import namedtuple
from insights import parser, CommandParser
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
            - total (str): total number of resources on the filesystem
            - used (str): number of the resources used on the filesystem
            - available (str): number of the resource available on the filesystem
            - capacity (str): percentage of the resource used on the filesystem
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
    """
    Class to provide methods used by all ``df`` command classes.

    Attributes:
        data (list of Record): List of ``Record`` objects for each line of command
            output.
        filesystems (dict of list): Dictionary with each entry being a
            list of ``Record`` objects, for all lines in the command output. The
            dictionary is keyed by the ``filesystem`` value of the Record.
        mounts (dict): Dictionary with each entry being a ``Record`` object
            corresponding to the ``mounted_on`` key.

    Raises:
        ParseException: When there are lines cannot be parsed or the
            ``block size`` cannot be recognized.
    """
    def __init__(self, context):
        super(DiskFree, self).__init__(context)
        self.filesystems = {}
        self.mounts = {}
        for datum in self.data:
            if datum.filesystem not in self.filesystems:
                self.filesystems[datum.filesystem] = []
            self.filesystems[datum.filesystem].append(datum)
            self.mounts[datum.mounted_on] = datum

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        for row in self.data:
            yield row

    def parse_content(self, content):
        def _digital_block_size(_block_size):
            """
            # man df
            SIZE  may be (or may be an integer optionally followed by) one
            of following: KB 1000, K 1024, MB 1000*1000, M 1024*1024, and so
            on for G, T, P, E, Z, Y.
            """
            units = {
                '': 1,
                'B': 1,
                'K': 1024,
                'KB': 1000,
                'M': 1024 * 1024,
                'MB': 1000 * 1000,
                'G': 1024 * 1024 * 1024,
                'GB': 1000 * 1000 * 1000,
                'T': 1024 * 1024 * 1024 * 1024,
                'TB': 1000 * 1000 * 1000 * 1000,
                'P': 1024 * 1024 * 1024 * 1024 * 1024,
                'PB': 1000 * 1000 * 1000 * 1000 * 1000,
                'E': 1024 * 1024 * 1024 * 1024 * 1024 * 1024,
                'EB': 1000 * 1000 * 1000 * 1000 * 1000 * 1000,
                'Z': 1024 * 1024 * 1024 * 1024 * 1024 * 1024 * 1024,
                'ZB': 1000 * 1000 * 1000 * 1000 * 1000 * 1000 * 1000,
                'Y': 1024 * 1024 * 1024 * 1024 * 1024 * 1024 * 1024 * 1024,
                'YB': 1000 * 1000 * 1000 * 1000 * 1000 * 1000 * 1000 * 1000,
            }
            suffix = _block_size[-2:].lstrip('0123456789')
            suffix_up = suffix.upper()
            if suffix_up in units:
                return units[suffix_up] * int(_block_size.rstrip('kKMGTPEZYB'))
            raise ParseException("Unknown block size: '{0}'".format(suffix))

        bad_lines = ["no such file or directory"]
        content = [l for l in content if bad_lines[0] not in l.lower()]
        self.block_size = self.raw_block_size = None
        # Get the block_size when there is such column
        header = content[0]
        if 'blocks' in header:
            block_size = [i.split('-')[0] for i in header.split() if 'blocks' in i][0]
            self.raw_block_size = block_size
            self.block_size = _digital_block_size(block_size)
        self.data = parse_df_lines(content)

    @property
    def filesystem_names(self):
        """list: Returns list of unique filesystem names."""
        return sorted(self.filesystems.keys())

    def get_filesystem(self, name):
        """str: Returns list of Record objects for filesystem ``name``."""
        return self.filesystems.get(name, [])

    @property
    def mount_names(self):
        """list: Returns list of unique mount point names."""
        return sorted(self.mounts.keys())

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

        Filesystem       Inodes IUsed    IFree IUse% Mounted on
        devtmpfs         242224   359   241865    1% /dev
        tmpfs            246028     1   246027    1% /dev/shm
        tmpfs            246028   491   245537    1% /run
        tmpfs            246028    17   246011    1% /sys/fs/cgroup
        /dev/sda2       8911872 58130  8853742    1% /
        /dev/sdb1      26213888 19662 26194226    1% /opt/data
        /dev/sda1        524288   306   523982    1% /boot
        tmpfs            246028     5   246023    1% /run/user/0

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

    Examples:
        >>> len(df_li)
        8
        >>> len(df_li.filesystem_names)
        5
        >>> df_li.get_filesystem('/dev/sda1')[0].mounted_on == '/boot'
        True
        >>> '/opt/data' in df_li.mount_names
        True
        >>> df_li.get_mount('/sys/fs/cgroup').available == '246011'
        True
        >>> [d.mounted_on for d in df_li if 'sda' in d.filesystem] == ['/', '/boot']
        True
        >>> df_li.data[0].filesystem == 'devtmpfs'
        True
        >>> df_li.data[0].capacity == '1%'
        True
    """
    pass


@parser(Specs.df__alP)
class DiskFree_ALP(DiskFree):
    """Parse lines from the output of the ``df -alP`` command.

    Typical content of the ``df -alP`` command looks like::

        Filesystem     1024-blocks    Used Available Capacity Mounted on
        sysfs                    0       0         0        - /sys
        proc                     0       0         0        - /proc
        devtmpfs            968896       0    968896       0% /dev
        securityfs               0       0         0        - /sys/kernel/security
        tmpfs               984112       0    984112       0% /dev/shm
        devpts                   0       0         0        - /dev/pts
        tmpfs               984112    8660    975452       1% /run
        tmpfs               984112       0    984112       0% /sys/fs/cgroup
        cgroup                   0       0         0        - /sys/fs/cgroup/systemd
        cgroup                   0       0         0        - /sys/fs/cgroup/pids
        cgroup                   0       0         0        - /sys/fs/cgroup/rdma
        configfs                 0       0         0        - /sys/kernel/config
        /dev/sda2         17813504 2127172  15686332      12% /
        selinuxfs                0       0         0        - /sys/fs/selinux
        systemd-1                -       -         -        - /proc/sys/fs/binfmt_misc
        debugfs                  0       0         0        - /sys/kernel/debug
        mqueue                   0       0         0        - /dev/mqueue
        hugetlbfs                0       0         0        - /dev/hugepages
        /dev/sdb1         52402180 1088148  51314032       3% /V M T o o l s
        /dev/sda1          1038336  185676    852660      18% /boot

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
        raw_block_size (str): The unit of display values.
        block_size (int): The unit of display values, which is converted to integer.

    Examples:
        >>> len(df_alP)
        20
        >>> len(df_alP.filesystem_names)
        16
        >>> df_alP.raw_block_size
        '1024'
        >>> df_alP.block_size
        1024
        >>> df_alP.get_filesystem('/dev/sda2')[0].mounted_on == '/'
        True
        >>> '/V M T o o l s' in df_alP.mount_names
        True
        >>> df_alP.get_mount('/boot').available
        '852660'
        >>> int(int(df_alP.get_mount('/boot').available) * df_alP.block_size / 1024)  # to KB
        852660
        >>> int(int(df_alP.get_mount('/boot').available) * df_alP.block_size / 1024 / 1024)  # to MB
        832
        >>> [d.mounted_on for d in df_alP if 'sda' in d.filesystem] == ['/', '/boot']
        True
        >>> df_alP.data[0].filesystem == 'sysfs'
        True
    """
    pass


@parser(Specs.df__al)
class DiskFree_AL(DiskFree):
    """Parse lines from the output of the ``df -al`` command.

    Typical content of the ``df -al`` command looks like::

        Filesystem     1K-blocks    Used Available Use% Mounted on
        sysfs                  0       0         0    - /sys
        proc                   0       0         0    - /proc
        devtmpfs          968896       0    968896   0% /dev
        securityfs             0       0         0    - /sys/kernel/security
        tmpfs             984112       0    984112   0% /dev/shm
        devpts                 0       0         0    - /dev/pts
        tmpfs             984112    8660    975452   1% /run
        tmpfs             984112       0    984112   0% /sys/fs/cgroup
        cgroup                 0       0         0    - /sys/fs/cgroup/systemd
        cgroup                 0       0         0    - /sys/fs/cgroup/pids
        cgroup                 0       0         0    - /sys/fs/cgroup/rdma
        configfs               0       0         0    - /sys/kernel/config
        /dev/sda2       17813504 2127172  15686332  12% /
        selinuxfs              0       0         0    - /sys/fs/selinux
        systemd-1              -       -         -    - /proc/sys/fs/binfmt_misc
        debugfs                0       0         0    - /sys/kernel/debug
        mqueue                 0       0         0    - /dev/mqueue
        hugetlbfs              0       0         0    - /dev/hugepages
        /dev/sdb1       52402180 1088148  51314032   3% /V M T o o l s
        /dev/sda1        1038336  185676    852660  18% /boot

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
        raw_block_size (str): The unit of display values.
        block_size (int): The unit of display values, which is converted to integer.

    Examples:
        >>> len(df_al)
        20
        >>> len(df_al.filesystem_names)
        16
        >>> df_al.raw_block_size
        '1K'
        >>> df_al.block_size
        1024
        >>> df_al.get_filesystem('/dev/sda2')[0].mounted_on == '/'
        True
        >>> '/V M T o o l s' in df_al.mount_names
        True
        >>> df_al.get_mount('/').used
        '2127172'
        >>> int(int(df_al.get_mount('/').used) * df_alP.block_size / 1024)  # to KB
        2127172
        >>> int(int(df_al.get_mount('/').used) * df_alP.block_size / 1024 / 1024)  # to MB
        2077
        >>> [d.mounted_on for d in df_al if 'sda' in d.filesystem] == ['/', '/boot']
        True
        >>> df_al.data[0].filesystem == 'sysfs'
        True
    """
    pass
