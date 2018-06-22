import doctest

from insights.parsers import systemctl_show
from insights.parsers.systemctl_show import SystemctlShowCinderVolume
from insights.parsers.systemctl_show import SystemctlShowHttpd
from insights.parsers.systemctl_show import SystemctlShowMariaDB
from insights.parsers.systemctl_show import SystemctlShowPulpCelerybeat
from insights.parsers.systemctl_show import SystemctlShowPulpResourceManager
from insights.parsers.systemctl_show import SystemctlShowPulpWorkers
from insights.parsers.systemctl_show import SystemctlShowQpidd
from insights.parsers.systemctl_show import SystemctlShowQdrouterd
from insights.parsers.systemctl_show import SystemctlShowSmartpdc
from insights.tests import context_wrap


SYSTEMCTL_SHOW_EXAMPLES = """
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
ExecMainPID=2811
LimitNOFILE=4096
"""


def test_systemctl_show_cinder_volume():
    context = SystemctlShowCinderVolume(context_wrap(SYSTEMCTL_SHOW_EXAMPLES))
    assert context["LimitNOFILE"] == "4096"
    assert len(context.data) == 21


def test_systemctl_show_mariadb():
    context = SystemctlShowMariaDB(context_wrap(SYSTEMCTL_SHOW_EXAMPLES))
    assert context["LimitNOFILE"] == "4096"
    assert len(context.data) == 21


def test_systemctl_show_pulp_workers():
    context = SystemctlShowPulpWorkers(context_wrap(SYSTEMCTL_SHOW_EXAMPLES))
    assert context["LimitNOFILE"] == "4096"
    assert len(context.data) == 21


def test_systemctl_show_pulp_resource_manager():
    context = SystemctlShowPulpResourceManager(context_wrap(SYSTEMCTL_SHOW_EXAMPLES))
    assert context["LimitNOFILE"] == "4096"
    assert len(context.data) == 21


def test_systemctl_show_pulp_celerybeat():
    context = SystemctlShowPulpCelerybeat(context_wrap(SYSTEMCTL_SHOW_EXAMPLES))
    assert context["LimitNOFILE"] == "4096"
    assert len(context.data) == 21


def test_systemctl_show_httpd():
    context = SystemctlShowHttpd(context_wrap(SYSTEMCTL_SHOW_EXAMPLES))
    assert context["LimitNOFILE"] == "4096"
    assert len(context.data) == 21


def test_systemctl_show_qpidd():
    context = SystemctlShowQpidd(context_wrap(SYSTEMCTL_SHOW_EXAMPLES))
    assert context["LimitNOFILE"] == "4096"
    assert len(context.data) == 21


def test_systemctl_show_qdrouterd():
    context = SystemctlShowQdrouterd(context_wrap(SYSTEMCTL_SHOW_EXAMPLES))
    assert context["LimitNOFILE"] == "4096"
    assert len(context.data) == 21


def test_systemctl_show_smartpdc():
    context = SystemctlShowSmartpdc(context_wrap(SYSTEMCTL_SHOW_EXAMPLES))
    assert context["LimitNOFILE"] == "4096"
    assert len(context.data) == 21


def test_systemctl_show_doc_examples():
    env = {
        'systemctl_show_cinder_volume': SystemctlShowCinderVolume(context_wrap(SYSTEMCTL_SHOW_EXAMPLES)),
        'systemctl_show_mariadb': SystemctlShowMariaDB(context_wrap(SYSTEMCTL_SHOW_EXAMPLES)),
        'systemctl_show_pulp_workers': SystemctlShowPulpWorkers(context_wrap(SYSTEMCTL_SHOW_EXAMPLES)),
        'systemctl_show_pulp_resource_manager': SystemctlShowPulpResourceManager(context_wrap(SYSTEMCTL_SHOW_EXAMPLES)),
        'systemctl_show_pulp_celerybeat': SystemctlShowPulpCelerybeat(context_wrap(SYSTEMCTL_SHOW_EXAMPLES)),
        'systemctl_show_httpd': SystemctlShowHttpd(context_wrap(SYSTEMCTL_SHOW_EXAMPLES)),
        'systemctl_show_qpidd': SystemctlShowQpidd(context_wrap(SYSTEMCTL_SHOW_EXAMPLES)),
        'systemctl_show_qdrouterd': SystemctlShowQdrouterd(context_wrap(SYSTEMCTL_SHOW_EXAMPLES)),
        'systemctl_show_smartpdc': SystemctlShowSmartpdc(context_wrap(SYSTEMCTL_SHOW_EXAMPLES))
    }
    failed, total = doctest.testmod(systemctl_show, globs=env)
    assert failed == 0
