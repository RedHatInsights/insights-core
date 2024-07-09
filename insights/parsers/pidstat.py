"""
Pidstat - command ``pidstat``
=============================
"""

from insights.core.plugins import parser
from insights.specs import Specs
from insights.parsers.ps import Ps


@parser(Specs.pidstat)
class PidStat(Ps):
    """
    Class ``PidStat`` parses the output of the ``pidstat`` command.  A small
    sample of the output of this command looks like::

        01:57:54 AM   UID       PID    %usr %system  %guest   %wait    %CPU   CPU  Command
        01:57:54 AM     0         1    0.00    0.00    0.00    0.00    0.00     0  systemd
        01:57:54 AM     0         2    0.00    0.00    0.00    0.00    0.00     0  kthreadd
        01:57:54 AM     0        13    0.00    0.00    0.00    0.00    0.00     0  ksoftirqd/0
        01:57:54 AM     0        14    0.00    0.00    0.00    0.05    0.00     0  rcu_sched
        01:57:54 AM     0        16    0.00    0.00    0.00    0.00    0.00     0  watchdog/0
        01:57:54 AM     0        21    0.00    0.00    0.00    0.00    0.00     0  kauditd
        01:57:54 AM     0        22    0.00    0.00    0.00    0.00    0.00     0  khungtaskd
        01:57:54 AM     0        27    0.00    0.00    0.00    0.00    0.00     0  khugepaged
        01:57:54 AM     0        36    0.00    0.00    0.00    0.00    0.00     0  kworker/0:1H-kblockd
        01:57:54 AM     0        70    0.00    0.00    0.00    0.00    0.00     0  kworker/u2:1-events_unbound
        01:57:54 AM     0       216    0.00    0.00    0.00    0.00    0.00     0  haveged
        01:57:54 AM     0       381    0.00    0.00    0.00    0.00    0.00     0  kworker/u2:3-events_unbound
        01:57:54 AM     0       493    0.00    0.00    0.00    0.00    0.00     0  xfsaild/dm-0
        01:57:54 AM     0       588    0.00    0.00    0.00    0.00    0.00     0  systemd-journal
        01:57:54 AM     0       617    0.00    0.00    0.00    0.00    0.00     0  systemd-udevd
        01:57:54 AM     0       632    0.00    0.00    0.00    0.00    0.00     0  xfsaild/vda1
        01:57:54 AM     0       663    0.00    0.00    0.00    0.00    0.00     0  auditd


    Examples:
        >>> type(pidstat_obj)
        <class 'insights.parsers.pidstat.PidStat'>
        >>> pidstat_obj.fuzzy_match('auditd')
        True
        >>> worker_process = pidstat_obj.search(Command__contains='kworker')
        >>> len(worker_process)
        3
        >>> worker_process[0]['PID']
        '36'
    """

    command_name = "Command"
    user_name = "UID"
    max_splits = 10
