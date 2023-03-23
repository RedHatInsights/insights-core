"""
Repquota - Command ``repquota -aguv``
=====================================

Parser for the output of ``repquota -aguv`` command
"""
from insights.core import Parser
from insights.core.exceptions import ParseException
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.repoquota_augv)
class RepquotaAUGV(Parser):
    """
    `repquota -aguv` prints a summary of the disc usage and quotas information for the specified file systems.

    Typical content looks like::

        *** Report for user quotas on device /dev/sdb
        Block grace time: 7days; Inode grace time: 7days
                                Block limits                File limits
        User            used    soft    hard  grace    used  soft  hard  grace
        ----------------------------------------------------------------------
        root      --       0       0       0              3     0     0
        user1     +-   61440   51200  102400  6days       1     0     0

        *** Status for user quotas on device /dev/sdb
        Accounting: ON; Enforcement: ON
        Inode: #131 (2 blocks, 2 extents)

        *** Report for user quotas on device /dev/sdc
        Block grace time: 7days; Inode grace time: 7days
                                Block limits                File limits
        User            used    soft    hard  grace    used  soft  hard  grace
        ----------------------------------------------------------------------
        root      --      20       0       0              2     0     0
        user2     +-  100000   50000  100000  7days       1     0     0

        Statistics:
        Total blocks: 7
        Data blocks: 1
        Entries: 2
        Used average: 2.000000

        *** Report for group quotas on device /dev/sdb
        Block grace time: 7days; Inode grace time: 7days
                                Block limits                File limits
        Group           used    soft    hard  grace    used  soft  hard  grace
        ----------------------------------------------------------------------
        root      --       0       0       0              3     0     0
        group1    --   61440       0       0              1     0     0

        *** Status for group quotas on device /dev/sdb
        Accounting: ON; Enforcement: OFF
        Inode: #132 (2 blocks, 2 extents)

        *** Report for group quotas on device /dev/sdc
        Block grace time: 7days; Inode grace time: 7days
                                Block limits                File limits
        Group           used    soft    hard  grace    used  soft  hard  grace
        ----------------------------------------------------------------------
        root      --      20       0       0              2     0     0
        group1    --  100000       0       0              3     2     4  6days

        Statistics:
        Total blocks: 7
        Data blocks: 1
        Entries: 2
        Used average: 2.000000

    Examples:
        >>> type(repquota)
        <class 'insights.parsers.repquota.RepquotaAUGV'>
        >>> 'enforcement' in repquota.user_quota['/dev/sdb']
        True
        >>> repquota.group_quota['/dev/sdb']['quota_info'][0] == {'group': 'root', 'flag': '--', 'block_used': '0', 'block_soft': '0', 'block_hard': '0', 'block_grace': '-', 'file_used': '3', 'file_soft': '0', 'file_hard': '0', 'file_grace': '-'}
        True

    Raises:
        insights.core.exceptions.ParseException: if the output of the ``repquota -aguv`` command is empty.
    """

    def parse_content(self, content):
        if len(content) == 0:
            raise ParseException("Error: empty output")
        flag = False
        data = {'user': {}, 'group': {}}
        self.raw = []
        quota_type = None
        quota_device = None
        hearding = ['flag', 'block_used', 'block_soft', 'block_hard', 'block_grace', 'file_used', 'file_soft', 'file_hard', 'file_grace']
        All_hearding = None
        for line in content:
            if not line:
                flag = False
                continue
            self.raw.append(line.strip())

            if line.startswith('*** Report'):
                split_list = line.split()
                if len(split_list) != 8:
                    raise ParseException("Error: content invalid")
                quota_type = split_list[3]
                quota_device = split_list[7]
                All_hearding = [quota_type] + hearding
                data[quota_type][quota_device] = {'quota_info': []}
                continue

            if line.startswith('----------'):
                flag = True
                continue
            if flag:
                split_line = line.split()
                if split_line[5].isdigit():
                    split_line.insert(5, '-')
                if len(split_line) == 9:
                    split_line.insert(9, '-')
                quota_info = dict(zip(All_hearding, split_line))
                data[quota_type][quota_device]['quota_info'].append(quota_info)
                continue

            if 'Accounting' in line and 'Enforcement' in line:
                data[quota_type][quota_device]['enforcement'] = True if line.split('Enforcement:')[1].strip().upper() == 'ON' else False

        self.user_quota = data['user']
        self.group_quota = data['group']
