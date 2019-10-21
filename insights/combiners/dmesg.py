"""
Dmesg
=====

Combiner for Dmesg information. It uses the results of the following parsers (if they are present):
:class:`insights.parsers.dmesg.DmesgLineList`,
:class:`insights.parsers.dmesg_log.DmesgLog`

Typical output of the ``/var/log/dmesg`` file is::

[    0.000000] Initializing cgroup subsys cpu
[    0.000000] Linux version 3.10.0-862.el7.x86_64 (mockbuild@x86-034.build.eng.bos.redhat.com) \
(gcc version 4.8.5 20150623 (Red Hat 4.8.5-28) (GCC) ) #1 SMP Wed Mar 21 18:14:51 EDT 2018
[    2.090905] SELinux:  Completing initialization.
[    2.090907] SELinux:  Setting up existing superblocks.
[    2.099684] systemd[1]: Successfully loaded SELinux policy in 82.788ms.
[    2.117410] ip_tables: (C) 2000-2006 Netfilter Core Team
[    2.117429] systemd[1]: Inserted module 'ip_tables'
[    2.376551] systemd-journald[441]: Received request to flush runtime journal from PID 1
[    2.716874] cryptd: max_cpu_qlen set to 100
[    2.804152] AES CTR mode by8 optimization enabled

Typical output of the ``dmesg`` command is::

[    2.939498] [TTM] Initializing pool allocator
[    2.939502] [TTM] Initializing DMA pool allocator
[    2.940800] [drm] fb mappable at 0xFC000000
[    2.940947] fbcon: cirrusdrmfb (fb0) is primary device
[    2.957375] Console: switching to colour frame buffer device 128x48
[    2.959322] cirrus 0000:00:02.0: fb0: cirrusdrmfb frame buffer device
[    2.959334] [drm] Initialized cirrus 1.0.0 20110418 for 0000:00:02.0 on minor 0
[    3.062459] XFS (vda1): Ending clean mount
[    5.048484] ip6_tables: (C) 2000-2006 Netfilter Core Team
[    5.102434] Ebtables v2.0 registered


Examples:
    >>> dmesg.dmesg_cmd_available
    True
    >>> dmesg.dmesg_log_available
    True
    >>> dmesg.dmesg_log_wrapped
    False
"""

from insights.core.filters import add_filter
from insights.core.plugins import combiner
from insights.parsers.dmesg import DmesgLineList
from insights.parsers.dmesg_log import DmesgLog
from insights.specs import Specs

add_filter(Specs.dmesg, 'Linux version')


@combiner([DmesgLineList, DmesgLog])
class Dmesg(object):
    """
    Combiner for ``dmesg`` command and ``/var/log/dmesg`` file.
    """

    def __init__(self, dmesg_cmd, dmesg_log):
        if dmesg_cmd is not None:
            self.dmesg_cmd_available = True
            self.dmesg_cmd = dmesg_cmd
            self.dmesg_cmd_wrapped = True if 'Linux version' not in dmesg_cmd else False
        else:
            self.dmesg_cmd_available = False

        if dmesg_log is not None:
            self.dmesg_log_available = True
            self.dmesg_log = dmesg_log
            self.dmesg_log_wrapped = True if 'Linux version' not in dmesg_log else False
        else:
            self.dmesg_log_available = False
