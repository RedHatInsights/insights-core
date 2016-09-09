"""
DF - Disk Free
==============
"""
from falafel.core.plugins import mapper
from falafel.core import MapperOutput, computed


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
        elif not line_splits:  # Skip empty lines (might in sosreport)
            continue
        if not is_sep:
            # Last column is mount point
            df_ls[columns[-1]] = line_splits[-1]
            df_out.append(df_ls)
            df_ls = {}
    return df_out


class DF_Entry(MapperOutput):
    """Class to contain one line of ``df`` command information.

    Contains all of the fields for a single line of ``df`` output.
    Computed values are the column names except where the column
    name is invalid as a variable in Python such as `Use%` and
    `1024-blocks`.  ``get`` method is provided to access any
    value, including those that are not valid in Python. For
    valid Python names the values may be accessed as
    ``obj.column_name``.
    """
    def __init__(self, data, path=None):
        """Initialize objects for class.

        Parameters
        ----------
        data: dict
            key, value pairs for ``df`` entry
        """
        super(DF_Entry, self).__init__(data, path)
        for k, v in data.iteritems():
            self._add_to_computed(k, v)

    def __eq__(self, other):
        return self.data == other

    def __ne__(self, other):
        return not self.data == other

    def get(self, k):
        """Get any value by keyword (column) name."""
        return self.data.get(k)


class DiskFree(MapperOutput):
    """Class to contain all information from ``df`` command.

    Output of the ``df`` command is contained in this base
    class.  Data is avaliable as rows of the output contained
    in one DF_Entry object for each line of output.  Data may
    also be accessed based on filesystem name or mount name.
    """
    def __init__(self, data, path=None):
        """Initialize objects for ``df`` output.

        The column names `Filesystem` and `Mounted_on` are assumed to be
        present as column names. An iterator is provided for the rows of
        command output and returns a dict object for each row where
        key is column name and value is `str` value from command.

        Parameters
        ----------
        data: list of dict
            Each row of the output is contained in the list and
            each row contains a dictionary of key, value pairs
            from the parsed output data.
        """
        self.rows = []
        self.filesystems = {}
        self.mounts = {}
        for datum in data:
            df_entry = DF_Entry(datum)
            self.rows.append(df_entry)
            if datum['Filesystem'] not in self.filesystems:
                self.filesystems[datum['Filesystem']] = []
            self.filesystems[datum['Filesystem']].append(df_entry)
            self.mounts[datum['Mounted_on']] = df_entry
        super(DiskFree, self).__init__(data, path)

    def __len__(self):
        return len(self.rows)

    def __iter__(self):
        for row in self.rows:
            yield row

    @computed
    def filesystem_names(self):
        """Returns list of unique filesystem names."""
        return self.filesystems.keys()

    def get_filesystem(self, name):
        """Returns list of DF_Entry objecs for filesystem `name`."""
        return self.filesystems.get(name)

    @computed
    def mount_names(self):
        """Returns list of unique mount point names."""
        return self.mounts.keys()

    def get_mount(self, name):
        """Returns DF_Entry obj for mount point `name`."""
        return self.mounts.get(name)


@mapper('df_-li')
class DiskFree_LI(DiskFree):
    """Parses ``df -li`` command output."""

    @classmethod
    def parse_content(cls, content):
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
        content: list of str
            List of lines output by the ``df -li`` command.  First line of
            the list is column names.

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
        return parse_df_lines(columns, content)


@mapper('df_-alP')
class DiskFree_ALP(DiskFree):
    """Parses ``df -alP`` command output."""

    @classmethod
    def parse_content(cls, content):
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
        content: list of str
            List of lines output by the ``df -alP`` command.  First line of
            the list is column names.

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
        return parse_df_lines(columns, content)


@mapper('df_-al')
class DiskFree_AL(DiskFree):
    """Parses ``df -al`` command output."""

    @classmethod
    def parse_content(cls, content):
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

        Parameters
        ----------
        content: list of str
            List of lines output by the ``df -al`` command.  First line of
            the list is column names.

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
        columns = ['Filesystem', '1K-blocks', 'Used', 'Available', 'Use%', 'Mounted_on']
        return parse_df_lines(columns, content)
