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

"""

from .. import LegacyItemAccess
from .. import Parser
from .. import parser
from ..parsers import split_kv_pairs


class SystemctlShow(LegacyItemAccess, Parser):
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
        self.data = {k: v for k, v in data.iteritems() if not v == ''}


@parser('systemctl_cinder-volume')
class SystemctlShowCinderVolume(SystemctlShow):

    """Class for ``systemctl show openstack-cinder-volume``

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
        ...

    Examples:
        >>> data = shared[SystemctlShowCinderVolume]
        >>> data["LimitNOFILE"]
        65536
    """
    pass


@parser('systemctl_mariadb')
class SystemctlShowMariaDB(SystemctlShow):

    """Class for ``systemctl show mariadb``

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
        ...

    Examples:
        >>> SrvMariaDB = shared[SystemctlShowMariaDB]
        >>> SrvMariaDB["After"]
        network.target -.mount systemd-journald.socket tmp.mount basic.target syslog.target system.slice
    """
    pass
