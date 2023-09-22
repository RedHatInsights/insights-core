"""
Repquota - command ``repquota``
===============================

Parser contains in this module is:

RepquotaAGNPUV - command ``repquota -agnpuv``
---------------------------------------------

"""
from insights.core import CommandParser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.repquota_agnpuv)
class RepquotaAGNPUV(CommandParser):
    """
    `repquota -agnpuv` prints a summary of the disc usage and quotas information for the specified file systems.

    Typical content looks like::

        *** Report for user quotas on device /dev/sdb
        Block grace time: 7days; Inode grace time: 7days
                                Block limits                File limits
        User            used    soft    hard  grace    used  soft  hard  grace
        ----------------------------------------------------------------------
        #0        --    5120       0       0      0       4     0     0      0
        #1009     +-   61440   51200  102400 1679983770       1     0     0      0
        #1010     --       0   51200  102400      0       0     0     0      0
        #1011     +-  107520   51200  307200 1680640819       2     0     0      0
        #1012     --   51200       0       0      0       1     0     0      0
        #1013     --       0   51200  102400      0       0     0     0      0

        *** Status for user quotas on device /dev/sdb
        Accounting: ON; Enforcement: ON
        Inode: #131 (2 blocks, 2 extents)

        *** Report for group quotas on device /dev/sdb
        Block grace time: 7days; Inode grace time: 7days
                                Block limits                File limits
        Group           used    soft    hard  grace    used  soft  hard  grace
        ----------------------------------------------------------------------
        #0        --    5120       0       0      0       4     0     0      0
        #1004     --   61440       0       0      0       1     0     0      0
        #1005     --   51200  972800 1048576      0       1     0     0      0
        #1011     --  107520       0       0      0       2     0     0      0

        *** Status for group quotas on device /dev/sdb
        Accounting: ON; Enforcement: ON
        Inode: #132 (2 blocks, 2 extents)

    Examples:
        >>> type(repquota)
        <class 'insights.parsers.repquota.RepquotaAGNPUV'>
        >>> 'enforcement' in repquota.user_quota['/dev/sdb']
        True
        >>> repquota.group_quota['/dev/sdb']['quota_info'][0] == {'group': '0', 'status': '--', 'block_used': '5120', 'block_soft': '0', 'block_hard': '0', 'block_grace': '0', 'file_used': '4', 'file_soft': '0', 'file_hard': '0', 'file_grace': '0'}
        True

    Raises:
        insights.core.exceptions.SkipComponent: if the output of the ``repquota -agnpuv`` command is empty.
    """

    def parse_content(self, content):
        self.user_quota = {}
        self.group_quota = {}
        data = device = heading = quota_list = None
        for line in content:
            if not line.strip():
                continue

            if line.startswith(('*** Report for', '*** Status for')):
                device = line.split()[-1]
                heading = ['group', 'block_used', 'block_soft', 'block_hard', 'block_grace', 'file_used', 'file_soft', 'file_hard', 'file_grace']
                data = self.group_quota
                if ' user ' in line:
                    heading[0] = 'user'
                    data = self.user_quota
                data[device] = data.get(device, dict(quota_info=[]))
                quota_list = data.get(device).get('quota_info')

            elif device and line.startswith('#'):
                line_sp = line.strip('#').split()
                info = dict(status=line_sp.pop(1))
                info.update(zip(heading, line_sp))
                quota_list.append(info)

            elif device and 'Accounting' in line and 'Enforcement' in line:
                data[device].update(enforcement='Enforcement: ON' in line,
                                    accounting='Accounting: ON' in line)

        if not self.user_quota and not self.group_quota:
            raise SkipComponent("Empty result")
