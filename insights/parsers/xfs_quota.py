"""
xfs_quota Commands
==================

Parser contains in this module is:

XFSQuotaState - command ``/sbin/xfs_quota -x -c 'state -gu'``
--------------------------------------------------------------
"""

from insights.core import CommandParser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.xfs_quota_state)
class XFSQuotaState(CommandParser):
    """
    The ``/sbin/xfs_quota -x -c 'state -gu'`` command provides information for the
    xfs quota devices.

    Attributes:
        group_quota (list): List of information for each group quota
        user_quota (list): List of information for each user quota

    Sample directory list collected::

        User quota state on /sdd (/dev/sdd)
          Accounting: ON
          Enforcement: ON
          Inode: #131 (1 blocks, 1 extents)
        Blocks grace time: [7 days]
        Blocks max warnings: 5
        Inodes grace time: [7 days]
        Inodes max warnings: 5
        Realtime Blocks grace time: [7 days]
        Group quota state on /sdd (/dev/sdd)
          Accounting: OFF
          Enforcement: OFF
          Inode: N/A
        Blocks grace time: [--------]
        Blocks max warnings: 0
        Inodes grace time: [--------]
        Inodes max warnings: 0
        Realtime Blocks grace time: [--------]
        User quota state on /sdb (/dev/sdb)
          Accounting: ON
          Enforcement: ON
          Inode: #131 (2 blocks, 2 extents)
        Blocks grace time: [6 days]
        Blocks max warnings: 10
        Inodes grace time: [6 days]
        Inodes max warnings: 5
        Realtime Blocks grace time: [6 days]
        Group quota state on /sdb (/dev/sdb)
          Accounting: ON
          Enforcement: ON
          Inode: #137 (2 blocks, 2 extents)
        Blocks grace time: [7 days]
        Blocks max warnings: 5
        Inodes grace time: [7 days]
        Inodes max warnings: 5
        Realtime Blocks grace time: [7 days]

    Examples:
        >>> type(quota_state)
        <class 'insights.parsers.xfs_quota.XFSQuotaState'>
        >>> len(quota_state.user_quota)
        3
        >>> quota_state.user_quota[0] == {'device': '/dev/sdd', 'accounting': 'ON', 'enforcement': 'ON', 'inode': '#131 (1 blocks, 1 extents)', 'blocks_grace_time': '7 days', 'blocks_max_warnings': '5', 'inodes_grace_time': '7 days', 'inodes_max_warnings': '5', 'realtime_blocks_grace_time': '7 days'}
        True
    """

    def parse_content(self, content):
        self.user_quota = []
        self.group_quota = []
        data = None
        for line in content:
            if not line.strip():
                continue

            if 'quota state on' in line:
                device = line.split()[-1].lstrip('(').rstrip(')')
                data = self.group_quota
                if 'User ' in line:
                    data = self.user_quota
                data.append({'device': device})

            elif ': ' in line:
                key, value = line.split(':', 1)
                data[-1]['_'.join(key.strip().lower().split())] = value.strip().lstrip('[').rstrip(']') if '-' not in value else None

        if not self.user_quota and not self.group_quota:
            raise SkipComponent("Empty result")
