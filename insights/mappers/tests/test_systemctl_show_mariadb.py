from insights.mappers.systemctl_show import SystemctlShowMariaDB
from insights.tests import context_wrap

SYSTEMCTL_SHOW_MARIADB = """
Type=simple
Restart=no
NotifyAccess=none
RestartUSec=100ms
TimeoutStartUSec=5min
TimeoutStopUSec=5min
WatchdogUSec=0
PermissionsStartOnly=no
ExecStartPre={ path=/usr/libexec/mariadb-prepare-db-dir ; argv[]=/usr/libexec/mariadb-prepare-db-dir %n ; ignore_errors=no ; start_time=[Mon 2017-05-22 06:49:01 EDT] ; stop_time=[Mon 2017-05-22 06:49:02 EDT] ; pid=1946 ; code=exited ; status=0 }
ExecStart={ path=/usr/bin/mysqld_safe ; argv[]=/usr/bin/mysqld_safe --basedir=/usr ; ignore_errors=no ; start_time=[Mon 2017-05-22 06:49:02 EDT] ; stop_time=[n/a] ; pid=2304 ; code=(null) ; status=0/0 }
ExecStartPost={ path=/usr/libexec/mariadb-wait-ready ; argv[]=/usr/libexec/mariadb-wait-ready $MAINPID ; ignore_errors=no ; start_time=[Mon 2017-05-22 06:49:02 EDT] ; stop_time=[Mon 2017-05-22 06:49:12 EDT] ; pid=2305 ; code=exited ; status=0 }
Slice=system.slice
ControlGroup=/system.slice/mariadb.service
CPUShares=18446744073709551615
StartupCPUShares=18446744073709551615
CPUQuotaPerSecUSec=infinity
After=network.target -.mount systemd-journald.socket tmp.mount basic.target syslog.target system.slice
RequiresMountsFor=/var/tmp
Description=MariaDB database server
LoadState=loaded
UnitFileState=enabled
Transient=no
""".strip()

SYSTEMCTL_SHOW_MARIADB_NO_AFTER = """
Type=simple
Restart=no
NotifyAccess=none
RestartUSec=100ms
TimeoutStartUSec=5min
TimeoutStopUSec=5min
WatchdogUSec=0
PermissionsStartOnly=no
ExecStartPre={ path=/usr/libexec/mariadb-prepare-db-dir ; argv[]=/usr/libexec/mariadb-prepare-db-dir %n ; ignore_errors=no ; start_time=[Mon 2017-05-22 06:49:01 EDT] ; stop_time=[Mon 2017-05-22 06:49:02 EDT] ; pid=1946 ; code=exited ; status=0 }
ExecStart={ path=/usr/bin/mysqld_safe ; argv[]=/usr/bin/mysqld_safe --basedir=/usr ; ignore_errors=no ; start_time=[Mon 2017-05-22 06:49:02 EDT] ; stop_time=[n/a] ; pid=2304 ; code=(null) ; status=0/0 }
ExecStartPost={ path=/usr/libexec/mariadb-wait-ready ; argv[]=/usr/libexec/mariadb-wait-ready $MAINPID ; ignore_errors=no ; start_time=[Mon 2017-05-22 06:49:02 EDT] ; stop_time=[Mon 2017-05-22 06:49:12 EDT] ; pid=2305 ; code=exited ; status=0 }
Slice=system.slice
ControlGroup=/system.slice/mariadb.service
CPUShares=18446744073709551615
StartupCPUShares=18446744073709551615
CPUQuotaPerSecUSec=infinity
After=systemd-journald.socket tmp.mount basic.target syslog.target system.slice
RequiresMountsFor=/var/tmp
Description=MariaDB database server
LoadState=loaded
UnitFileState=enabled
Transient=no
""".strip()

SYSTEMCTL_SHOW_MARIADB_ONLY_NETWORK = """
Type=simple
Restart=no
NotifyAccess=none
RestartUSec=100ms
TimeoutStartUSec=5min
TimeoutStopUSec=5min
WatchdogUSec=0
PermissionsStartOnly=no
ExecStartPre={ path=/usr/libexec/mariadb-prepare-db-dir ; argv[]=/usr/libexec/mariadb-prepare-db-dir %n ; ignore_errors=no ; start_time=[Mon 2017-05-22 06:49:01 EDT] ; stop_time=[Mon 2017-05-22 06:49:02 EDT] ; pid=1946 ; code=exited ; status=0 }
ExecStart={ path=/usr/bin/mysqld_safe ; argv[]=/usr/bin/mysqld_safe --basedir=/usr ; ignore_errors=no ; start_time=[Mon 2017-05-22 06:49:02 EDT] ; stop_time=[n/a] ; pid=2304 ; code=(null) ; status=0/0 }
ExecStartPost={ path=/usr/libexec/mariadb-wait-ready ; argv[]=/usr/libexec/mariadb-wait-ready $MAINPID ; ignore_errors=no ; start_time=[Mon 2017-05-22 06:49:02 EDT] ; stop_time=[Mon 2017-05-22 06:49:12 EDT] ; pid=2305 ; code=exited ; status=0 }
Slice=system.slice
ControlGroup=/system.slice/mariadb.service
CPUShares=18446744073709551615
StartupCPUShares=18446744073709551615
CPUQuotaPerSecUSec=infinity
After=network.target
RequiresMountsFor=/var/tmp
Description=MariaDB database server
LoadState=loaded
UnitFileState=enabled
Transient=no
""".strip()

SYSTEMCTL_SHOW_MARIADB_ONLINE_NETWORK = """
Type=simple
Restart=no
NotifyAccess=none
RestartUSec=100ms
TimeoutStartUSec=5min
TimeoutStopUSec=5min
WatchdogUSec=0
PermissionsStartOnly=no
ExecStartPre={ path=/usr/libexec/mariadb-prepare-db-dir ; argv[]=/usr/libexec/mariadb-prepare-db-dir %n ; ignore_errors=no ; start_time=[Mon 2017-05-22 06:49:01 EDT] ; stop_time=[Mon 2017-05-22 06:49:02 EDT] ; pid=1946 ; code=exited ; status=0 }
ExecStart={ path=/usr/bin/mysqld_safe ; argv[]=/usr/bin/mysqld_safe --basedir=/usr ; ignore_errors=no ; start_time=[Mon 2017-05-22 06:49:02 EDT] ; stop_time=[n/a] ; pid=2304 ; code=(null) ; status=0/0 }
ExecStartPost={ path=/usr/libexec/mariadb-wait-ready ; argv[]=/usr/libexec/mariadb-wait-ready $MAINPID ; ignore_errors=no ; start_time=[Mon 2017-05-22 06:49:02 EDT] ; stop_time=[Mon 2017-05-22 06:49:12 EDT] ; pid=2305 ; code=exited ; status=0 }
Slice=system.slice
ControlGroup=/system.slice/mariadb.service
CPUShares=18446744073709551615
StartupCPUShares=18446744073709551615
CPUQuotaPerSecUSec=infinity
After=network-online.target
RequiresMountsFor=/var/tmp
Description=MariaDB database server
LoadState=loaded
UnitFileState=enabled
Transient=no
""".strip()


def test_systemctl_show_mariadb():
    context = context_wrap(SYSTEMCTL_SHOW_MARIADB)
    result = SystemctlShowMariaDB(context).data
    assert "network.target" in result["After"]

    context = context_wrap(SYSTEMCTL_SHOW_MARIADB_NO_AFTER)
    result = SystemctlShowMariaDB(context).data
    assert "network.target" not in result["After"]

    context = context_wrap(SYSTEMCTL_SHOW_MARIADB_ONLY_NETWORK)
    result = SystemctlShowMariaDB(context).data
    assert "network.target" in result["After"]

    context = context_wrap(SYSTEMCTL_SHOW_MARIADB_ONLINE_NETWORK)
    result = SystemctlShowMariaDB(context).data
    assert "network-online.target" in result["After"]
