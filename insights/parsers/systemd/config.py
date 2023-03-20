"""
SystemD service configuration
=============================

Service systemd files are in ``/usr/lib/systemd/system/`` or ``/etc/systemd/``,
and their content format is similar to a '.ini' file.

Parsers included in this module are:

SystemdDocker - file ``/usr/lib/systemd/system/docker.service``
---------------------------------------------------------------

SystemdLogindConf - file ``/etc/systemd/logind.conf``
-----------------------------------------------------

SystemdRpcbindSocketConf - unit file ``rpcbind.socket``
-------------------------------------------------------

SystemdDnsmasqServiceConf - unit file ``dnsmasq.service``
---------------------------------------------------------

SystemdOpenshiftNode - file ``/usr/lib/systemd/system/atomic-openshift-node.service``
-------------------------------------------------------------------------------------

SystemdSystemConf - file ``/etc/systemd/system.conf``
-----------------------------------------------------

SystemdOriginAccounting - file ``/etc/systemd/system.conf.d/origin-accounting.conf``
------------------------------------------------------------------------------------
"""

from insights.core import ConfigParser, LegacyItemAccess
from insights.core.plugins import parser
from insights.parsr import iniparser
from insights.specs import Specs
from insights import CommandParser


class SystemdConf(CommandParser, LegacyItemAccess, ConfigParser):
    """
    Base class for parsing systemd INI like configuration files

    """
    def parse_doc(self, content):
        return iniparser.parse_doc("\n".join(content), self)

    def parse_content(self, content):
        super(SystemdConf, self).parse_content(content)
        dict_all = {}
        for section in self.doc:
            section_dict = {}
            option_names = set(o.name for o in section)
            for name in option_names:
                options = [str(o.value) for o in section[name]]
                section_dict[name] = options[0] if len(options) == 1 else options
            dict_all[section.name] = section_dict
        self.data = dict_all


@parser(Specs.systemd_docker)
class SystemdDocker(SystemdConf):
    """
    Class for docker service systemd configuration.

    Typical content of ``/usr/lib/systemd/system/docker.service`` file is::

        [Service]
        Type=notify
        EnvironmentFile=-/etc/sysconfig/docker
        EnvironmentFile=-/etc/sysconfig/docker-storage
        EnvironmentFile=-/etc/sysconfig/docker-network
        Environment=GOTRACEBACK=crash
        ExecStart=/bin/sh -c '/usr/bin/docker-current daemon \\
            --authorization-plugin=rhel-push-plugin \\
            --exec-opt native.cgroupdriver=systemd \\
            $OPTIONS \\
            $DOCKER_STORAGE_OPTIONS \\
            $DOCKER_NETWORK_OPTIONS \\
            $ADD_REGISTRY \\
            $BLOCK_REGISTRY \\
            $INSECURE_REGISTRY \\
            2>&1 | /usr/bin/forward-journald -tag docker'
        LimitNOFILE=1048576

    Example:
        >>> docker_service["Service"]["ExecStart"].endswith("-tag docker'")
        True
        >>> len(docker_service["Service"]["EnvironmentFile"])
        3
    """
    pass


@parser(Specs.systemd_system_conf)
class SystemdSystemConf(SystemdConf):
    """
    Class for systemd master configuration in the ``/etc/systemd/system.conf``
    file.

    Typical content of the ``/etc/systemd/system.conf`` file is::

        [Manager]
        RuntimeWatchdogSec=0
        ShutdownWatchdogSec=10min

    Example:
        >>> system_conf["Manager"]["RuntimeWatchdogSec"]
        '0'
    """
    pass


@parser(Specs.systemd_system_origin_accounting)
class SystemdOriginAccounting(SystemdConf):
    """
    Class for systemd master configuration in the ``/etc/systemd/system.conf.d/origin-accounting.conf``
    file.

    Typical content of the ``/etc/systemd/system.conf.d/origin-accounting.conf`` file is::

        [Manager]
        DefaultCPUAccounting=yes
        DefaultMemoryAccounting=yes
        DefaultBlockIOAccounting=yes

    Example:
        >>> system_origin_accounting["Manager"]["DefaultCPUAccounting"]
        'True'
    """
    pass


@parser(Specs.systemd_openshift_node)
class SystemdOpenshiftNode(SystemdConf):
    """
    Class for atomic-openshift-node systemd configuration.

    Typical output of
    ``/usr/lib/systemd/system/atomic-openshift-node.service`` file is::

        [Service]
        Type=notify
        RestartSec=5s
        OOMScoreAdjust=-999
        ExecStartPost=/usr/bin/sleep 10
        ExecStartPost=/usr/sbin/sysctl --system

    Example:
        >>> openshift_node_service["Service"]["RestartSec"]
        '5s'
        >>> len(openshift_node_service["Service"]["ExecStartPost"])
        2
    """
    pass


@parser(Specs.systemd_logind_conf)
class SystemdLogindConf(SystemdConf):
    """
    Class for systemd logind configuration.

    Typical content of the ``/etc/systemd/logind.conf`` file is::

        [Login]
        ReserveVT=6
        KillUserProcesses=Yes
        RemoveIPC=no

    Example:
        >>> logind_conf["Login"]["ReserveVT"]
        '6'
        >>> logind_conf["Login"]["KillUserProcesses"]  # 'Yes' turns to 'True'
        'True'
        >>> logind_conf.get("Login").get("RemoveIPC")  # 'no' turns to 'False'
        'False'
    """
    pass


@parser(Specs.systemctl_cat_rpcbind_socket)
class SystemdRpcbindSocketConf(SystemdConf):
    """
    Class for systemd configuration for rpcbind.socket unit.

    Typical content of the ``rpcbind.socket`` unit file is::

        [Unit]
        Description=RPCbind Server Activation Socket
        DefaultDependencies=no
        Wants=rpcbind.target
        Before=rpcbind.target

        [Socket]
        ListenStream=/run/rpcbind.sock

        # RPC netconfig can't handle ipv6/ipv4 dual sockets
        BindIPv6Only=ipv6-only
        ListenStream=0.0.0.0:111
        ListenDatagram=0.0.0.0:111
        ListenStream=[::]:111
        ListenDatagram=[::]:111

        [Install]
        WantedBy=sockets.target

    Example:
        >>> rpcbind_socket["Socket"]["ListenStream"]
        ['/run/rpcbind.sock', '0.0.0.0:111', '[::]:111']
    """
    pass


@parser(Specs.systemctl_cat_dnsmasq_service)
class SystemdDnsmasqServiceConf(SystemdConf):
    """
    Class for systemd configuration for dnsmasq.service unit.

    Typical content of the ``dnsmasq.service`` unit file is::

        [Unit]
        Description=DNS caching server.
        After=network.target

        [Service]
        ExecStart=/usr/sbin/dnsmasq -k

        [Install]
        WantedBy=multi-user.target

    Example:
        >>> dnsmasq_service["Unit"]["After"]
        'network.target'
    """
    pass
