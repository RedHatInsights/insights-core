"""
Repquota - command ``repquota``
===============================

Parser contains in this module is:

RepquotaAGNUV - command ``repquota -agnuv``
---------------------------------------------

"""
from insights.core import CommandParser
from insights.core.exceptions import SkipException
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.repquota_agnuv)
class RepquotaAGNUV(CommandParser):
    """
    `repquota -agnuv` prints a summary of the disc usage and quotas information for the specified file systems.

    Typical content looks like::

        *** Report for user quotas on device /dev/sdc
        Block grace time: 2days; Inode grace time: 2days
                                Block limits                File limits
        User            used    soft    hard  grace    used  soft  hard  grace
        ----------------------------------------------------------------------
        #0        --       0       0       0              3     0     0
        #1001     +-  563200  512000 1024000   none       1     0     0
        #1002     +-  579520  512000 1024000  44:58       2     0     0

        *** Status for user quotas on device /dev/sdc
        Accounting: ON; Enforcement: ON
        Inode: #131 (2 blocks, 2 extents)

        *** Report for group quotas on device /dev/sdc
        Block grace time: 7days; Inode grace time: 7days
                                Block limits                File limits
        Group           used    soft    hard  grace    used  soft  hard  grace
        ----------------------------------------------------------------------
        #0        --       0       0       0              3     0     0
        #1001     --  563200       0       0              1     0     0
        #1002     --  579520       0       0              2     0     0

        *** Status for group quotas on device /dev/sdc
        Accounting: ON; Enforcement: ON
        Inode: #132 (2 blocks, 2 extents)

    Examples:
        >>> type(repquota)
        <class 'insights.parsers.repquota.RepquotaAGNUV'>
        >>> 'enforcement' in repquota.group_quota['/dev/sdc']
        True
        >>> repquota.user_quota['/dev/sdc']['quota_info'][1] == {'user': '1001', 'status': '+-', 'block_used': '563200', 'block_soft': '512000', 'block_hard': '1024000', 'block_grace': 'none', 'file_used': '1', 'file_soft': '0', 'file_hard': '0', 'file_grace': '0'}
        True

    Raises:
        insights.core.exceptions.SkipException: if the output of the ``repquota -agnuv`` command is empty.
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
                if line_sp[5].isdigit():
                    line_sp.insert(5, '0')
                if len(line_sp) == 9:
                    line_sp.insert(9, '0')
                if line_sp[2].isdigit() and line_sp[3].isdigit() and line_sp[4].isdigit() and line_sp[6].isdigit() and line_sp[7].isdigit() and line_sp[8].isdigit():
                    info = dict(status=line_sp.pop(1))
                    info.update(zip(heading, line_sp))
                    quota_list.append(info)
                else:
                    raise SkipException("Content invalid")

            elif device and 'Accounting' in line and 'Enforcement' in line:
                data[device].update(enforcement='Enforcement: ON' in line,
                                    accounting='Accounting: ON' in line)

        if not self.user_quota and not self.group_quota:
            raise SkipException("Empty result")
