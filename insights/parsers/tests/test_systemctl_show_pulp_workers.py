from insights.parsers.systemctl_show import SystemctlShowPulpWorkers
from insights.tests import context_wrap


SYSTEMCTL_SHOW_PULP_WORKERS = """
WatchdogUSec=0
WatchdogTimestamp=Thu 2018-01-11 14:22:33 CST
WatchdogTimestampMonotonic=105028136
StartLimitInterval=10000000
StartLimitBurst=5
StartLimitAction=none
FailureAction=none
PermissionsStartOnly=no
RootDirectoryStartOnly=no
RemainAfterExit=no
GuessMainPID=yes
MainPID=2810
ControlPID=0
FileDescriptorStoreMax=0
StatusErrno=0
Result=success
ExecMainStartTimestamp=Thu 2018-01-11 14:22:33 CST
ExecMainStartTimestampMonotonic=105028117
ExecMainExitTimestampMonotonic=0
ExecMainPID=2810
LimitNOFILE=4096
"""


def test_systemctl_show_pulp_workers():
    context = context_wrap(SYSTEMCTL_SHOW_PULP_WORKERS)
    result = SystemctlShowPulpWorkers(context).data
    assert result["LimitNOFILE"] == "4096"
    assert len(result) == 21
