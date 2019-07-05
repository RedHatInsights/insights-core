"""
DmesgLog - file ``/var/log/dmesg``
==================================

This module provides access to the messages from the kernel ring buffer
gathered from the ``/var/log/dmesg`` file.

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


Examples:
    >>> "SELinux" in dmesg_log
    True
    >>> "ip6_tables" in dmesg_log
    False
    >>> dmesg_log.get("SELinux")[0]["raw_message"]
    "[    2.090905] SELinux:  Completing initialization."
    >>> len(dmesg_log.get("SELinux"))
    2
"""

from insights import parser
from insights.specs import Specs
from insights.parsers.dmesg import DmesgLineList


@parser(Specs.dmesg_log)
class DmesgLog(DmesgLineList):
    """
    Class for parsing the ``/var/log/dmesg`` file using the DmesgLineList class.
    """
    pass
