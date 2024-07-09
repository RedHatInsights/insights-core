import doctest
import pytest

from insights.core.exceptions import ParseException
from insights.parsers import pidstat
from insights.tests import context_wrap


PIDSTAT_OUTPUT = """
01:57:54 AM   UID       PID    %usr %system  %guest   %wait    %CPU   CPU  Command
01:57:54 AM     0         1    3.00   12.00   11.00    1.00    2.00     0  systemd
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
"""

PIDSTAT_BAD_OUTPUT_NO_UID = """
01:57:54 AM   PID    %usr %system  %guest   %wait    %CPU   CPU  Command
01:57:54 AM     1    3.00   12.00   11.00    1.00    2.00     0  systemd
01:57:54 AM     2    0.00    0.00    0.00    0.00    0.00     0  kthreadd
01:57:54 AM    13    0.00    0.00    0.00    0.00    0.00     0  ksoftirqd/0
01:57:54 AM    14    0.00    0.00    0.00    0.05    0.00     0  rcu_sched
01:57:54 AM    16    0.00    0.00    0.00    0.00    0.00     0  watchdog/0
01:57:54 AM    21    0.00    0.00    0.00    0.00    0.00     0  kauditd
01:57:54 AM    22    0.00    0.00    0.00    0.00    0.00     0  khungtaskd
01:57:54 AM    27    0.00    0.00    0.00    0.00    0.00     0  khugepaged
01:57:54 AM    36    0.00    0.00    0.00    0.00    0.00     0  kworker/0:1H-kblockd
01:57:54 AM    70    0.00    0.00    0.00    0.00    0.00     0  kworker/u2:1-events_unbound
01:57:54 AM   216    0.00    0.00    0.00    0.00    0.00     0  haveged
01:57:54 AM   381    0.00    0.00    0.00    0.00    0.00     0  kworker/u2:3-events_unbound
01:57:54 AM   493    0.00    0.00    0.00    0.00    0.00     0  xfsaild/dm-0
01:57:54 AM   588    0.00    0.00    0.00    0.00    0.00     0  systemd-journal
01:57:54 AM   617    0.00    0.00    0.00    0.00    0.00     0  systemd-udevd
01:57:54 AM   632    0.00    0.00    0.00    0.00    0.00     0  xfsaild/vda1
01:57:54 AM   663    0.00    0.00    0.00    0.00    0.00     0  auditd
"""


def test_pidstat_parser():
    pidstat_obj = pidstat.PidStat(context_wrap(PIDSTAT_OUTPUT))
    assert len(pidstat_obj.data) == 17
    systemd_processes = pidstat_obj.search(Command__startswith='systemd')
    assert len(systemd_processes) == 3
    assert systemd_processes[0]['UID'] == '0'
    assert systemd_processes[0]['PID'] == '1'
    assert systemd_processes[0]['%usr'] == '3.00'
    assert systemd_processes[0]['%system'] == '12.00'
    assert systemd_processes[0]['%guest'] == '11.00'
    assert systemd_processes[0]['%wait'] == '1.00'
    assert systemd_processes[0]['%CPU'] == '2.00'
    assert systemd_processes[0]['CPU'] == '0'
    assert systemd_processes[0]['Command'] == 'systemd'
    assert systemd_processes[1]['Command'] == 'systemd-journal'
    assert systemd_processes[2]['Command'] == 'systemd-udevd'

    assert '663' in pidstat_obj.running_pids()


def test_doc_examples():
    env = {
        'pidstat_obj': pidstat.PidStat(context_wrap(PIDSTAT_OUTPUT)),
    }
    failed, _ = doctest.testmod(pidstat, globs=env)
    assert failed == 0


def test_exception():
    with pytest.raises(ParseException):
        pidstat.PidStat(context_wrap(PIDSTAT_BAD_OUTPUT_NO_UID))
