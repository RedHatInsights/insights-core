import doctest
import pytest
from insights.parsers import systemctl_show, SkipException, ParseException
from insights.parsers.systemctl_show import SystemctlShowServiceAll, SystemctlShowTarget
from insights.tests import context_wrap
# TODO: Remove the following `import`s when removing the deprecated parsers
from insights.parsers.systemctl_show import SystemctlShowCinderVolume
from insights.parsers.systemctl_show import SystemctlShowHttpd
from insights.parsers.systemctl_show import SystemctlShowMariaDB
from insights.parsers.systemctl_show import SystemctlShowPulpCelerybeat
from insights.parsers.systemctl_show import SystemctlShowPulpResourceManager
from insights.parsers.systemctl_show import SystemctlShowPulpWorkers
from insights.parsers.systemctl_show import SystemctlShowQpidd
from insights.parsers.systemctl_show import SystemctlShowQdrouterd
from insights.parsers.systemctl_show import SystemctlShowSmartpdc
from insights.parsers.systemctl_show import SystemctlShowNginx


# TODO: Remove the following test cases when removing the deprecated parsers
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


def test_systemctl_show_nginx():
    context = SystemctlShowNginx(context_wrap(SYSTEMCTL_SHOW_EXAMPLES))
    assert context["LimitNOFILE"] == "4096"
    assert len(context.data) == 21
# NOTE: Above code should be removed after removing the deprecated parsers


SYSTEMCTL_SHOW_ALL_EXAMPLES = """
KillSignal=15
SendSIGKILL=yes
SendSIGHUP=no
Id=postfix.service
Names=postfix.service
Requires=basic.target
Wants=system.slice
WantedBy=multi-user.target
LimitNOFILE=65536
LimitMEMLOCK=
LimitLOCKS=18446744073709551615

User=postgres
Group=postgres
MountFlags=0
PrivateTmp=no
PrivateNetwork=no
PrivateDevices=no
ProtectHome=no
ProtectSystem=no
SameProcessGroup=no
IgnoreSIGPIPE=yes
NoNewPrivileges=no
SystemCallErrorNumber=0
RuntimeDirectoryMode=0755
KillMode=control-group
KillSignal=15
SendSIGKILL=yes
SendSIGHUP=no
Id=postgresql.service
Names=postgresql.service
Requires=basic.target
LimitMSGQUEUE=819200
LimitNICE=0
ExecStartPre={ path=/usr/bin/postgresql-check-db-dir ; argv[]=/usr/bin/postgresql-check-db-dir ${PGDATA} ; ignore_errors=no ; start_time=[Tue 2019-11-19 23:55:49 EST]
ExecStart={ path=/usr/bin/pg_ctl ; argv[]=/usr/bin/pg_ctl start -D ${PGDATA} -s -o -p ${PGPORT} -w -t 300 ; ignore_errors=no ; start_time=[Tue 2019-11-19 23:55:50 EST]
ExecReload={ path=/usr/bin/pg_ctl ; argv[]=/usr/bin/pg_ctl reload -D ${PGDATA} -s ; ignore_errors=no ; start_time=[n/a] ; stop_time=[n/a] ; pid=0 ; code=(null) ; statu
ExecStop={ path=/usr/bin/pg_ctl ; argv[]=/usr/bin/pg_ctl stop -D ${PGDATA} -s -m fast ; ignore_errors=no ; start_time=[n/a] ; stop_time=[n/a] ; pid=0 ; code=(null) ; s
Slice=system.slice
ControlGroup=/system.slice/postgresql.service

Id=tuned.service
Names=tuned.service
Requires=polkit.service basic.target dbus.service
Wants=system.slice
WantedBy=multi-user.target
Conflicts=shutdown.target cpupower.service
Before=multi-user.target shutdown.target
After=systemd-sysctl.service system.slice network.target systemd-journald.socket
basic.target dbus.service
Documentation=man:tuned(8) man:tuned.conf(5) man:tuned-adm(8)
Description=Dynamic System Tuning Daemon
LoadState=loaded
ActiveState=active
SubState=running
FragmentPath=/usr/lib/systemd/system/tuned.service
UnitFileState=enabled
UnitFilePreset=enabled
InactiveExitTimestamp=Tue 2019-11-19 23:55:50 EST
InactiveExitTimestampMonotonic=9434667
ActiveEnterTimestamp=Tue 2019-11-19 23:55:53 EST
ActiveEnterTimestampMonotonic=12640144
ActiveExitTimestampMonotonic=0
InactiveEnterTimestampMonotonic=0
CanStart=yes
CanStop=yes
CanReload=no
CanIsolate=no
StopWhenUnneeded=no
RefuseManualStart=no
RefuseManualStop=no
AllowIsolate=no
DefaultDependencies=yes
OnFailureJobMode=replace
IgnoreOnIsolate=no
IgnoreOnSnapshot=no
NeedDaemonReload=no
JobTimeoutUSec=0
JobTimeoutAction=none
ConditionResult=yes
AssertResult=yes
ConditionTimestamp=Tue 2019-11-19 23:55:50 EST
ConditionTimestampMonotonic=9429104
AssertTimestamp=Tue 2019-11-19 23:55:50 EST
AssertTimestampMonotonic=9429105
ABC=
Transient=no
""".strip()

SYSTEMCTL_SHOW_ALL_EXP = """
KillSignal=15
SendSIGKILL=yes
SendSIGHUP=no
Requires=basic.target
Wants=system.slice
WantedBy=multi-user.target
LimitNOFILE=65536
LimitMEMLOCK=
LimitLOCKS=18446744073709551615

""".strip()

SYSTEMCTL_SHOW_TARGET = """
Id=network.target
Names=network.target
WantedBy=NetworkManager.service
Conflicts=shutdown.target
Before=tuned.service network-online.target rhsmcertd.service kdump.service httpd.service rsyslog.service rc-local.service insights-client.timer insights-client.service sshd.service postfix.service
After=firewalld.service network-pre.target network.service NetworkManager.service
Documentation=man:systemd.special(7) http://www.freedesktop.org/wiki/Software/systemd/NetworkTarget
Description=Network
LoadState=loaded
ActiveState=active
SubState=active
FragmentPath=/usr/lib/systemd/system/network.target
UnitFileState=static
UnitFilePreset=disabled
InactiveExitTimestamp=Tue 2020-02-25 10:39:46 GMT
InactiveExitTimestampMonotonic=15332468
ActiveEnterTimestamp=Tue 2020-02-25 10:39:46 GMT
ActiveEnterTimestampMonotonic=15332468
ActiveExitTimestampMonotonic=0
InactiveEnterTimestampMonotonic=0
CanStart=no

Id=swap.target
Names=swap.target
Requires=dev-mapper-rhel\x5cx2dswap.swap
WantedBy=sysinit.target
Conflicts=shutdown.target
Before=sysinit.target tmp.mount
After=dev-disk-by\x5cx2did-dm\x5cx2duuid\x5cx2dLVM\x5cx2deP73apHGoZ6LcvX230L0BUHQiPDhXceEkTtrOvL6P2biOWacMR3YS7rISVOgnPdc.swap dev-dm\x5cx2d1.swap dev-rhel-swap.swap dev-disk-by\x5cx2did-dm\x5cx2dname\x5cx2drhel\x5cx2dswap.swap dev-disk-by\x5cx2duuid-1ffaf940\x5cx2de836\x5cx2d4f08\x5cx2d9e5f\x5cx2d4dbe425d787f.swap dev-mapper-rhel\x5cx2dswap.swap
Documentation=man:systemd.special(7)
Description=Swap
LoadState=loaded
ActiveState=active
SubState=active
FragmentPath=/usr/lib/systemd/system/swap.target
UnitFileState=static
UnitFilePreset=disabled
InactiveExitTimestamp=Tue 2020-02-25 10:39:35 GMT
InactiveExitTimestampMonotonic=4692015
ActiveEnterTimestamp=Tue 2020-02-25 10:39:35 GMT
ActiveEnterTimestampMonotonic=4692015
ActiveExitTimestamp=Tue 2020-02-25 10:39:34 GMT
ActiveExitTimestampMonotonic=3432423

Id=paths.target
Names=paths.target
WantedBy=basic.target
Conflicts=shutdown.target
Before=basic.target
After=brandbot.path systemd-ask-password-console.path systemd-ask-password-wall.path
Documentation=man:systemd.special(7)
Description=Paths
LoadState=loaded
ActiveState=active
SubState=active
FragmentPath=/usr/lib/systemd/system/paths.target
UnitFileState=static
UnitFilePreset=disabled
InactiveExitTimestamp=Tue 2020-02-25 10:39:38 GMT
InactiveExitTimestampMonotonic=7782864
ActiveEnterTimestamp=Tue 2020-02-25 10:39:38 GMT
ActiveEnterTimestampMonotonic=7782864
ActiveExitTimestamp=Tue 2020-02-25 10:39:34 GMT
ActiveExitTimestampMonotonic=3427228
InactiveEnterTimestamp=Tue 2020-02-25 10:39:34 GMT

Id=sockets.target
Names=sockets.target
Wants=rpcbind.socket systemd-initctl.socket systemd-udevd-kernel.socket dbus.socket dm-event.socket systemd-udevd-control.socket systemd-journald.socket systemd-shutdownd.socket
WantedBy=basic.target
Conflicts=shutdown.target
Before=basic.target
After=systemd-udevd-kernel.socket systemd-shutdownd.socket sshd.socket systemd-udevd-control.socket systemd-initctl.socket systemd-journald.socket rpcbind.socket syslog.socket dbus.socket
Documentation=man:systemd.special(7)
Description=Sockets
LoadState=loaded
ActiveState=active
SubState=active
FragmentPath=/usr/lib/systemd/system/sockets.target
UnitFileState=static
UnitFilePreset=disabled
InactiveExitTimestamp=Tue 2020-02-25 10:39:38 GMT
InactiveExitTimestampMonotonic=7786499
ActiveEnterTimestamp=Tue 2020-02-25 10:39:38 GMT
ActiveEnterTimestampMonotonic=7786499
ActiveExitTimestamp=Tue 2020-02-25 10:39:34 GMT
ActiveExitTimestampMonotonic=3427060
""".strip()


def test_systemctl_show_service_all():
    svc_all = SystemctlShowServiceAll(context_wrap(SYSTEMCTL_SHOW_ALL_EXAMPLES))
    assert len(svc_all) == 3

    assert 'postfix.service' in svc_all
    assert 'LimitMEMLOCK' not in svc_all['postfix.service']
    assert svc_all['postfix.service']["LimitNOFILE"] == "65536"
    assert svc_all['postfix.service']["KillSignal"] == "15"
    assert svc_all['postfix.service']["LimitLOCKS"] == "18446744073709551615"
    assert len(svc_all['postfix.service']) == 10

    assert 'postgresql.service' in svc_all
    assert svc_all['postgresql.service']["User"] == "postgres"
    assert svc_all['postgresql.service']["ControlGroup"] == "/system.slice/postgresql.service"
    assert len(svc_all['postgresql.service']) == 28

    assert 'tuned.service' in svc_all
    assert svc_all['tuned.service']["Id"] == "tuned.service"
    assert svc_all['tuned.service']["Transient"] == "no"
    assert "ABC" not in svc_all['tuned.service']
    assert len(svc_all['tuned.service']) == 44


def test_systemctl_show_target():
    data = SystemctlShowTarget(context_wrap(SYSTEMCTL_SHOW_TARGET))
    assert 'network.target' in data
    assert data.get('network.target').get('WantedBy', None) == 'NetworkManager.service'
    assert data.get('network.target').get('RequiredBy', None) is None


def test_systemctl_show_service_all_ab():
    with pytest.raises(SkipException):
        SystemctlShowServiceAll(context_wrap(''))

    with pytest.raises(ParseException):
        SystemctlShowServiceAll(context_wrap(SYSTEMCTL_SHOW_ALL_EXP))


def test_systemctl_show_doc_examples():
    env = {
        'systemctl_show_all': SystemctlShowServiceAll(context_wrap(SYSTEMCTL_SHOW_ALL_EXAMPLES)),
        'systemctl_show_target': SystemctlShowTarget(context_wrap(SYSTEMCTL_SHOW_TARGET)),
        # TODO: Remove the following test when removing the deprecated parsers.
        'systemctl_show_cinder_volume': SystemctlShowCinderVolume(context_wrap(SYSTEMCTL_SHOW_EXAMPLES)),
        'systemctl_show_mariadb': SystemctlShowMariaDB(context_wrap(SYSTEMCTL_SHOW_EXAMPLES)),
        'systemctl_show_pulp_workers': SystemctlShowPulpWorkers(context_wrap(SYSTEMCTL_SHOW_EXAMPLES)),
        'systemctl_show_pulp_resource_manager': SystemctlShowPulpResourceManager(context_wrap(SYSTEMCTL_SHOW_EXAMPLES)),
        'systemctl_show_pulp_celerybeat': SystemctlShowPulpCelerybeat(context_wrap(SYSTEMCTL_SHOW_EXAMPLES)),
        'systemctl_show_httpd': SystemctlShowHttpd(context_wrap(SYSTEMCTL_SHOW_EXAMPLES)),
        'systemctl_show_qpidd': SystemctlShowQpidd(context_wrap(SYSTEMCTL_SHOW_EXAMPLES)),
        'systemctl_show_qdrouterd': SystemctlShowQdrouterd(context_wrap(SYSTEMCTL_SHOW_EXAMPLES)),
        'systemctl_show_smartpdc': SystemctlShowSmartpdc(context_wrap(SYSTEMCTL_SHOW_EXAMPLES)),
        'systemctl_show_nginx': SystemctlShowNginx(context_wrap(SYSTEMCTL_SHOW_EXAMPLES))
    }
    failed, total = doctest.testmod(systemctl_show, globs=env)
    assert failed == 0
