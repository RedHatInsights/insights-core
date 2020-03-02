"""
SystemctlShow - command ``systemctl show``
==========================================

Parsers included in this module are:

SystemctlShowServiceAll - command ``systemctl show *.service``
--------------------------------------------------------------
SystemctlShowTarget - command ``systemctl show *.target``
-------------------------------------------------------------------
"""
from insights import parser, CommandParser
from insights.parsers import split_kv_pairs, SkipException, ParseException
from insights.specs import Specs
from insights.util import deprecated


@parser(Specs.systemctl_show_all_services)
class SystemctlShowServiceAll(CommandParser, dict):
    """
    Class for parsing ``systemctl show *.service`` command output.
    Empty properties are suppressed.

    Sample Input::

        Id=postfix.service
        Names=postfix.service
        TimeoutStartUSec=1min 30s
        LimitNOFILE=65536
        LimitMEMLOCK=
        LimitLOCKS=18446744073709551615

        Id=postgresql.service
        Names=postgresql.service
        Requires=basic.target
        LimitMSGQUEUE=819200
        LimitNICE=0

    Sample Output::

        {
            "postfix.service": {
                "Id"               : "postfix.service",
                "Names"            : "postfix.service",
                "LimitNOFILE"      : "65536",
                "TimeoutStartUSec" : "1min 30s",
                "LimitLOCKS"       : "18446744073709551615",
            },
            "postgresql.service": {
                "Id"               : "postgresql.service",
                "Names"            : "postgresql.service",
                "Requires"         : "basic.target",
                "LimitMSGQUEUE"    : "819200",
                "LimitNICE"        : "0",
            }
        }

    Examples:
        >>> 'postfix' in systemctl_show_all  # ".service" is needed
        False
        >>> 'postfix.service' in systemctl_show_all
        True
        >>> systemctl_show_all['postfix.service']['Id']
        'postfix.service'
        >>> 'LimitMEMLOCK' in systemctl_show_all['postfix.service']
        False
        >>> systemctl_show_all['postfix.service']['LimitLOCKS']
        '18446744073709551615'
        >>> 'postgresql.service' in systemctl_show_all
        True
        >>> systemctl_show_all['postgresql.service']['LimitNICE']
        '0'

    Raises:
        SkipException: When nothing needs to parse
        ParseException: When something cannot be parsed
    """

    def parse_content(self, content):
        if not content:
            raise SkipException

        sidx = 0
        idx_list = []
        for i, l in enumerate(content):
            if l.strip() == '':
                idx_list.append((sidx, i))
                sidx = i + 1
        idx_list.append((sidx, len(content)))
        for s, e in idx_list:
            data = split_kv_pairs(content[s:e], use_partition=False)
            name = data.get('Names', data.get('Id'))
            if not name:
                raise ParseException('"Names" or "Id" not found!')
            self[name] = dict((k, v) for k, v in data.items() if v)

        if len(self) == 0:
            raise SkipException


@parser(Specs.systemctl_show_target)
class SystemctlShowTarget(SystemctlShowServiceAll):
    """
    Class for parsing ``systemctl show *.target`` command output.
    Empty properties are suppressed.

    This class is inherited from :py:class:`SystemctlShowServiceAll`.

    Sample Input::

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

    Sample Output::

        {'network.target': {'ActiveEnterTimestamp': 'Tue 2020-02-25 10:39:46 GMT',
                            'ActiveEnterTimestampMonotonic': '15332468',
                            'ActiveExitTimestampMonotonic': '0',
                            'ActiveState': 'active',
                            'After': 'firewalld.service network-pre.target '
                                     'network.service NetworkManager.service',
                            'Before': 'tuned.service network-online.target '
                                      'rhsmcertd.service kdump.service httpd.service '
                                      'rsyslog.service rc-local.service '
                                      'insights-client.timer insights-client.service '
                                      'sshd.service postfix.service',
                            'CanStart': 'no',
                            'Conflicts': 'shutdown.target',
                            'Description': 'Network',
                            'Documentation': 'man:systemd.special(7) '
                                             'http://www.freedesktop.org/wiki/Software/systemd/NetworkTarget',
                            'FragmentPath': '/usr/lib/systemd/system/network.target',
                            'Id': 'network.target',
                            'InactiveEnterTimestampMonotonic': '0',
                            'InactiveExitTimestamp': 'Tue 2020-02-25 10:39:46 GMT',
                            'InactiveExitTimestampMonotonic': '15332468',
                            'LoadState': 'loaded',
                            'Names': 'network.target',
                            'SubState': 'active',
                            'UnitFilePreset': 'disabled',
                            'UnitFileState': 'static',
                            'WantedBy': 'NetworkManager.service'})

    Examples:
        >>> 'network.target' in systemctl_show_target
        True
        >>> systemctl_show_target.get('network.target').get('WantedBy', None)
        'NetworkManager.service'
        >>> systemctl_show_target.get('network.target').get('RequiredBy', None)

    Raises:
        SkipException: When nothing needs to parse
        ParseException: When something cannot be parsed
    """
    pass


class SystemctlShow(CommandParser, dict):
    """
    .. warning::
        This class is deprecated, please use :py:class:`SystemctlShowServiceAll` instead.

    Class for parsing ``systemctl show <Service_Name>`` command output.
    Empty properties are suppressed.

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
    """
    def __init__(self, *args, **kwargs):
        deprecated(SystemctlShow, "Deprecated. Use 'SystemctlShowServiceAll' instead.")
        super(SystemctlShow, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        data = split_kv_pairs(content, use_partition=False)
        """Remove empty key"""
        self.update(dict((k, v) for k, v in data.items() if not v == ''))

    @property
    def data(self):
        return self


@parser(Specs.systemctl_cinder_volume)
class SystemctlShowCinderVolume(SystemctlShow):
    """
    .. warning::
        This parser is deprecated, please use :py:class:`SystemctlShowServiceAll` instead.

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
    .. warning::
        This parser is deprecated, please use :py:class:`SystemctlShowServiceAll` instead.

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
    .. warning::
        This parser is deprecated, please use :py:class:`SystemctlShowServiceAll` instead.

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
    .. warning::
        This parser is deprecated, please use :py:class:`SystemctlShowServiceAll` instead.

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
    .. warning::
        This parser is deprecated, please use :py:class:`SystemctlShowServiceAll` instead.

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
    .. warning::
        This parser is deprecated, please use :py:class:`SystemctlShowServiceAll` instead.

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


@parser(Specs.systemctl_nginx)
class SystemctlShowNginx(SystemctlShow):
    """
    .. warning::
        This parser is deprecated, please use :py:class:`SystemctlShowServiceAll` instead.

    Class for ``systemctl show nginx``.

    Typical output of ``/bin/systemctl show nginx`` command is::

        Type=forking
        Restart=no
        PIDFile=/run/nginx.pid
        NotifyAccess=none
        RestartUSec=100ms
        TimeoutStartUSec=1min 30s
        TimeoutStopUSec=5s
        RuntimeMaxUSec=infinity
        WatchdogUSec=0
        WatchdogTimestampMonotonic=0
        PermissionsStartOnly=no
        RootDirectoryStartOnly=no
        RemainAfterExit=no
        GuessMainPID=yes
        MainPID=0
        ControlPID=0
        FileDescriptorStoreMax=0
        NFileDescriptorStore=0
        StatusErrno=0
        Result=success
        UID=[not set]
        GID=[not set]
        NRestarts=0
        ExecMainStartTimestampMonotonic=0
        ExecMainExitTimestampMonotonic=0
        ExecMainPID=0
        ExecMainCode=0
        ExecMainStatus=0
        ExecStartPre={ path=/usr/bin/rm ; argv[]=/usr/bin/rm -f /run/nginx.pid ; ignore_errors=no ; start_time=[n/a] ; stop_time=[n/a] ; pid=0 ; code=(null) ; status=0/0 }
        ExecStartPre={ path=/usr/sbin/nginx ; argv[]=/usr/sbin/nginx -t ; ignore_errors=no ; start_time=[n/a] ; stop_time=[n/a] ; pid=0 ; code=(null) ; status=0/0 }
        ExecStart={ path=/usr/sbin/nginx ; argv[]=/usr/sbin/nginx ; ignore_errors=no ; start_time=[n/a] ; stop_time=[n/a] ; pid=0 ; code=(null) ; status=0/0 }
        ExecReload={ path=/bin/kill ; argv[]=/bin/kill -s HUP $MAINPID ; ignore_errors=no ; start_time=[n/a] ; stop_time=[n/a] ; pid=0 ; code=(null) ; status=0/0 }
        ...

    Examples:
        >>> systemctl_show_nginx["LimitNOFILE"]
        '4096'

    """
    pass


@parser(Specs.systemctl_qpidd)
class SystemctlShowQpidd(SystemctlShow):
    """
    .. warning::
        This parser is deprecated, please use :py:class:`SystemctlShowServiceAll` instead.

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
    .. warning::
        This parser is deprecated, please use :py:class:`SystemctlShowServiceAll` instead.

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
    .. warning::
        This parser is deprecated, please use :py:class:`SystemctlShowServiceAll` instead.

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
