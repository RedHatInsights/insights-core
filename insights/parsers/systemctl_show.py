"""
Systemd command ``show`` outputs
================================
This command shows all the paramters for this service, these parameters can be set
through unit files corresponding to that service or from command line.

Parsers included in this module are:

SystemctlShowCinderVolume - command ``systemctl show openstack-cinder-volume``
------------------------------------------------------------------------------

SystemctlShowMariaDB - command ``systemctl show mariadb``
---------------------------------------------------------

SystemctlShowPulpWorkers - command ``systemctl show pulp_workers``
------------------------------------------------------------------

SystemctlShowPulpResourceManager - command ``systemctl show pulp_resource_manager``
-----------------------------------------------------------------------------------

SystemctlShowPulpCelerybeat - command ``systemctl show pulp_celerybeat``
------------------------------------------------------------------------

SystemctlShowHttpd - command ``systemctl show httpd``
-----------------------------------------------------

SystemctlShowQpidd - command ``systemctl show qpidd``
-----------------------------------------------------

SystemctlShowQdrouterd - command ``systemctl show qdrouterd``
-------------------------------------------------------------

SystemctlShowSmartpdc - command ``systemctl show smart_proxy_dynflow_core``
---------------------------------------------------------------------------
"""


from .. import LegacyItemAccess
from .. import CommandParser
from .. import parser
from ..parsers import split_kv_pairs
from ..specs import Specs


class SystemctlShow(LegacyItemAccess, CommandParser):
    """Class for parsing ``systemctl show <Service_Name>`` command output"""

    def parse_content(self, content):
        """
        Sample Input::

            TimeoutStartUSec=1min 30s
            LimitNOFILE=65536
            LimitMEMLOCK=
            LimitLOCKS=18446744073709551615

        Sample Output::

            {"LimitNOFILE"     : "65536",
            "TimeoutStartUSec" : "1min 30s",
            "LimitLOCKS"       : "18446744073709551615"}

        In CMD's output, empty properties are suppressed by default.
        We will also suppressed empty properties in return data.
        """
        data = {}
        data = split_kv_pairs(content, use_partition=False)

        """Remove empty key"""
        self.data = dict((k, v) for k, v in data.items() if not v == '')


@parser(Specs.systemctl_cinder_volume)
class SystemctlShowCinderVolume(SystemctlShow):
    """
    Class for ``systemctl show openstack-cinder-volume``.

    Typical output of ``/bin/systemctl show openstack-cinder-volume`` command is::

        Restart=no
        NotifyAccess=none
        RestartUSec=100ms
        TimeoutStartUSec=1min 30s
        TimeoutStopUSec=1min 30s
        WatchdogUSec=0
        LimitCORE=18446744073709551615
        LimitRSS=18446744073709551615
        LimitNOFILE=65536
        LimitAS=18446744073709551615
        LimitNPROC=63391
        Transient=no
        LimitNOFILE=4096
        ...

    Examples:
        >>> systemctl_show_cinder_volume["LimitNOFILE"]
        '4096'

    """
    pass


@parser(Specs.systemctl_mariadb)
class SystemctlShowMariaDB(SystemctlShow):
    """
    Class for ``systemctl show mariadb``.

    Typical output of ``/bin/systemctl show mariadb`` command is::

        Type=simple
        Restart=no
        NotifyAccess=none
        RestartUSec=100ms
        TimeoutStopUSec=5min
        ExecStartPre={ path=/usr/libexec/mariadb-prepare-db-dir ; argv[]=/usr/libexec/mariadb-prepare-db-dir %n ; ignore_errors=no ; start_time=[Mon 2017-05-22 06:49:01 EDT] ; stop_time=[Mon 2017-05-22 06:49:02 EDT] ; pid=1946 ; code=exited ; status=0 }
        ExecStart={ path=/usr/bin/mysqld_safe ; argv[]=/usr/bin/mysqld_safe --basedir=/usr ; ignore_errors=no ; start_time=[Mon 2017-05-22 06:49:02 EDT] ; stop_time=[n/a] ; pid=2304 ; code=(null) ; status=0/0 }
        ExecStartPost={ path=/usr/libexec/mariadb-wait-ready ; argv[]=/usr/libexec/mariadb-wait-ready $MAINPID ; ignore_errors=no ; start_time=[Mon 2017-05-22 06:49:02 EDT] ; stop_time=[Mon 2017-05-22 06:49:12 EDT] ; pid=2305 ; code=exited ; status=0 }
        Slice=system.slice
        ControlGroup=/system.slice/mariadb.service
        After=network.target -.mount systemd-journald.socket tmp.mount basic.target syslog.target system.slice
        MemoryCurrent=18446744073709551615
        LimitNOFILE=4096
        ...

    Examples:
        >>> systemctl_show_mariadb["LimitNOFILE"]
        '4096'

    """
    pass


@parser(Specs.systemctl_pulp_workers)
class SystemctlShowPulpWorkers(SystemctlShow):
    """
    Class for ``systemctl show pulp_workers``.

    Typical output of ``/bin/systemctl show pulp_workers`` command is::

        Type=oneshot
        Restart=no
        NotifyAccess=none
        RestartUSec=100ms
        TimeoutStartUSec=0
        TimeoutStopUSec=1min 30s
        WatchdogUSec=0
        WatchdogTimestampMonotonic=0
        ExecMainStartTimestamp=Thu 2018-01-11 14:22:33 CST
        ExecMainStartTimestampMonotonic=105521850
        ExecMainExitTimestamp=Thu 2018-01-11 14:22:33 CST
        ExecMainExitTimestampMonotonic=105593405
        ExecStart={ path=/usr/libexec/pulp-manage-workers ; argv[]=/usr/libexec/pulp-manage-workers start ; ignore_err
        ExecStop={ path=/usr/libexec/pulp-manage-workers ; argv[]=/usr/libexec/pulp-manage-workers stop ; ignore_error
        Slice=system.slice
        After=systemd-journald.socket system.slice network.target basic.target
        LimitNOFILE=4096
        ...

    Examples:
        >>> systemctl_show_pulp_workers["LimitNOFILE"]
        '4096'

    """
    pass


@parser(Specs.systemctl_pulp_resmg)
class SystemctlShowPulpResourceManager(SystemctlShow):
    """
    Class for ``systemctl show pulp_resource_manager``.

    Typical output of ``/bin/systemctl show pulp_resource_manager`` command is::

        Type=simple
        Restart=no
        NotifyAccess=none
        RestartUSec=100ms
        TimeoutStartUSec=1min 30s
        TimeoutStopUSec=1min 30s
        ExecMainStartTimestamp=Thu 2018-01-11 14:22:33 CST
        ExecMainStartTimestampMonotonic=105028117
        ExecMainExitTimestampMonotonic=0
        ExecMainPID=2810
        ExecMainCode=0
        ExecMainStatus=0
        ExecStart={ path=/usr/bin/celery ; argv[]=/usr/bin/celery worker -A pulp.server.async.app -n resource_manager@
        Slice=system.slice
        After=basic.target network.target system.slice -.mount systemd-journald.socket
        LimitNOFILE=4096
        ...

    Examples:
        >>> systemctl_show_pulp_resource_manager["LimitNOFILE"]
        '4096'

    """
    pass


@parser(Specs.systemctl_pulp_celerybeat)
class SystemctlShowPulpCelerybeat(SystemctlShow):
    """
    Class for ``systemctl show pulp_celerybeat``.

    Typical output of ``/bin/systemctl show pulp_celerybeat`` command is::

        Type=simple
        Restart=no
        NotifyAccess=none
        RestartUSec=100ms
        TimeoutStartUSec=1min 30s
        TimeoutStopUSec=1min 30s
        ExecMainStartTimestamp=Thu 2018-01-11 14:22:32 CST
        ExecMainStartTimestampMonotonic=104261679
        ExecMainExitTimestampMonotonic=0
        ExecMainPID=2747
        ExecMainCode=0
        ExecMainStatus=0
        ExecStart={ path=/usr/bin/celery ; argv[]=/usr/bin/celery beat --scheduler=pulp.server.async.scheduler.Schedul
        Slice=system.slice
        After=basic.target network.target system.slice -.mount systemd-journald.socket
        LimitNOFILE=4096
        ...

    Examples:
        >>> systemctl_show_pulp_celerybeat["LimitNOFILE"]
        '4096'

    """
    pass


@parser(Specs.systemctl_httpd)
class SystemctlShowHttpd(SystemctlShow):
    """
    Class for ``systemctl show httpd``.

    Typical output of ``/bin/systemctl show httpd`` command is::

        Type=simple
        Restart=no
        NotifyAccess=none
        RestartUSec=100ms
        TimeoutStartUSec=1min 30s
        TimeoutStopUSec=1min 30s
        ExecMainStartTimestamp=Thu 2018-01-11 14:22:32 CST
        ExecMainStartTimestampMonotonic=104261679
        ExecMainExitTimestampMonotonic=0
        ExecMainPID=2747
        ExecMainCode=0
        ExecMainStatus=0
        ExecStart={ path=/usr/sbin/httpd ; argv[]=/usr/sbin/httpd $OPTIONS -DFOREGROUND ; ignore_errors=no ; start_time=[Tue 2018-05-15 09:30:08 CST] ; stop_time=[n/a] ; pid=1605 ; code=(null) ; status=0/0 }
        ExecReload={ path=/usr/sbin/httpd ; argv[]=/usr/sbin/httpd $OPTIONS -k graceful ; ignore_errors=no ; start_time=[Wed 2018-05-16 03:07:01 CST] ; stop_time=[Wed 2018-05-16 03:07:01 CST] ; pid=21501 ; code=exited ; status=0 }
        ExecStop={ path=/bin/kill ; argv[]=/bin/kill -WINCH ${MAINPID} ; ignore_errors=no ; start_time=[n/a] ; stop_time=[n/a] ; pid=0 ; code=(null) ; status=0/0 }
        Slice=system.slice
        ControlGroup=/system.slice/httpd.service
        LimitNOFILE=4096
        ...

    Examples:
        >>> systemctl_show_httpd["LimitNOFILE"]
        '4096'

    """
    pass


@parser(Specs.systemctl_qpidd)
class SystemctlShowQpidd(SystemctlShow):
    """
    Class for ``systemctl show qpidd``.

    Typical output of ``/bin/systemctl show qpidd`` command is::

        Type=simple
        Restart=no
        NotifyAccess=none
        RestartUSec=100ms
        TimeoutStartUSec=1min 30s
        TimeoutStopUSec=1min 30s
        ExecMainStartTimestamp=Thu 2018-01-11 14:22:32 CST
        ExecMainStartTimestampMonotonic=104261679
        ExecMainExitTimestampMonotonic=0
        ExecMainPID=2747
        ExecMainCode=0
        ExecMainStatus=0
        ExecStart={ path=/usr/sbin/qpidd ; argv[]=/usr/sbin/qpidd --config /etc/qpid/qpi
        Slice=system.slice
        ControlGroup=/system.slice/qpidd.service
        LimitNOFILE=4096
        ...

    Examples:
        >>> systemctl_show_qpidd["LimitNOFILE"]
        '4096'

    """
    pass


@parser(Specs.systemctl_qdrouterd)
class SystemctlShowQdrouterd(SystemctlShow):
    """
    Class for ``systemctl show qdrouterd``.

    Typical output of ``/bin/systemctl show qdrouterd`` command is::

        Type=simple
        Restart=no
        NotifyAccess=none
        RestartUSec=100ms
        TimeoutStartUSec=1min 30s
        TimeoutStopUSec=1min 30s
        ExecMainStartTimestamp=Thu 2018-01-11 14:22:32 CST
        ExecMainStartTimestampMonotonic=104261679
        ExecMainExitTimestampMonotonic=0
        ExecMainPID=2747
        ExecMainCode=0
        ExecMainStatus=0
        Slice=system.slice
        LimitNOFILE=4096
        ...

    Examples:
        >>> systemctl_show_qdrouterd["LimitNOFILE"]
        '4096'

    """
    pass


@parser(Specs.systemctl_smartpdc)
class SystemctlShowSmartpdc(SystemctlShow):
    """
    Class for ``systemctl show smart_proxy_dynflow_core``.

    Typical output of ``/bin/systemctl show smart_proxy_dynflow_core`` command is::

        Type=simple
        Restart=no
        NotifyAccess=none
        RestartUSec=100ms
        TimeoutStartUSec=1min 30s
        TimeoutStopUSec=1min 30s
        ExecMainStartTimestamp=Thu 2018-01-11 14:22:32 CST
        ExecMainStartTimestampMonotonic=104261679
        ExecMainExitTimestampMonotonic=0
        ExecMainPID=2747
        ExecMainCode=0
        ExecMainStatus=0
        Slice=system.slice
        LimitNOFILE=4096
        ...

    Examples:
        >>> systemctl_show_smartpdc["LimitNOFILE"]
        '4096'

    """
    pass
