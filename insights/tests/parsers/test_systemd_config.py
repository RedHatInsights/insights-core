import doctest
import pytest

from insights.core.exceptions import ContentException, SkipComponent
from insights.parsers.systemd import config
from insights.tests import context_wrap


SYSTEMD_DOCKER = """
[Unit]
Description=Docker Application Container Engine
Documentation=http://docs.docker.com
After=network.target
Wants=docker-storage-setup.service
Requires=rhel-push-plugin.socket

[Service]
Type=notify
NotifyAccess=all
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
LimitNPROC=1048576
LimitCORE=infinity
TimeoutStartSec=0
MountFlags=slave
Restart=on-abnormal
StandardOutput=null
StandardError=null

[Install]
WantedBy=multi-user.target
""".strip()


SYSTEMD_DOCKER_EMPTY = """
Unit docker.service is not loaded: No such file or directory
""".strip()


SYSTEMD_OPENSHIFT_NODE = """
[Unit]
Description=Atomic OpenShift Node
After=docker.service
After=openvswitch.service
Wants=docker.service
Documentation=https://github.com/openshift/origin

[Service]
Type=notify
EnvironmentFile=/etc/sysconfig/atomic-openshift-node
Environment=GOTRACEBACK=crash
ExecStart=/usr/bin/openshift start node --config=${CONFIG_FILE} $OPTIONS
LimitNOFILE=65536
LimitCORE=infinity
WorkingDirectory=/var/lib/origin/
SyslogIdentifier=atomic-openshift-node
Restart=always
RestartSec=5s
OOMScoreAdjust=-999
ExecStartPost=/usr/bin/sleep 10
ExecStartPost=/usr/sbin/sysctl --system

[Install]
WantedBy=multi-user.target

""".strip()


SYSTEMD_LOGIND_CONF = """
#  This file is part of systemd.
#
#  systemd is free software; you can redistribute it and/or modify it
#  under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation; either version 2.1 of the License, or
#  (at your option) any later version.
#
# Entries in this file show the compile time defaults.
# You can change settings by editing this file.
# Defaults can be restored by simply deleting this file.
#
# See logind.conf(5) for details.

[Login]
#NAutoVTs=6
ReserveVT=6
KillUserProcesses=Yes
#KillOnlyUsers=
#KillExcludeUsers=root
#InhibitDelayMaxSec=5
#HandlePowerKey=poweroff
#HandleSuspendKey=suspend
#HandleHibernateKey=hibernate
#HandleLidSwitch=suspend
#HandleLidSwitchDocked=ignore
#PowerKeyIgnoreInhibited=no
#SuspendKeyIgnoreInhibited=no
#HibernateKeyIgnoreInhibited=no
#LidSwitchIgnoreInhibited=yes
#IdleAction=ignore
#IdleActionSec=30min
RuntimeDirectorySize=10%
RemoveIPC=no
#UserTasksMax=
""".strip()

SYSTEMD_RPCBIND_SOCKET = """
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
""".strip()

SYSTEMD_DNSMASQ_SERVICE = """
[Unit]
Description=DNS caching server.
After=network.target

[Service]
ExecStart=/usr/sbin/dnsmasq -k

[Install]
WantedBy=multi-user.target
""".strip()

SYSTEMD_SYSTEM_CONF = """
#  This file is part of systemd.
#
#  systemd is free software; you can redistribute it and/or modify it
#  under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation; either version 2.1 of the License, or
#  (at your option) any later version.
#
# Entries in this file show the compile time defaults.
# You can change settings by editing this file.
# Defaults can be restored by simply deleting this file.
#
# See systemd-system.conf(5) for details.

[Manager]
#LogLevel=info
#LogTarget=journal-or-kmsg
#LogColor=yes
#LogLocation=no
#DumpCore=yes
#CrashShell=no
#ShowStatus=yes
#CrashChVT=1
#CPUAffinity=1 2
#JoinControllers=cpu,cpuacct net_cls,net_prio
RuntimeWatchdogSec=0
ShutdownWatchdogSec=10min
#CapabilityBoundingSet=
#SystemCallArchitectures=
#TimerSlackNSec=
#DefaultTimerAccuracySec=1min
#DefaultStandardOutput=journal
#DefaultStandardError=inherit
#DefaultTimeoutStartSec=90s
#DefaultTimeoutStopSec=90s
#DefaultRestartSec=100ms
#DefaultStartLimitInterval=10s
#DefaultStartLimitBurst=5
#DefaultEnvironment=
#DefaultCPUAccounting=no
#DefaultBlockIOAccounting=no
#DefaultMemoryAccounting=no
#DefaultLimitCPU=
#DefaultLimitFSIZE=
#DefaultLimitDATA=
#DefaultLimitSTACK=
#DefaultLimitCORE=
#DefaultLimitRSS=
#DefaultLimitNOFILE=
#DefaultLimitAS=
#DefaultLimitNPROC=
#DefaultLimitMEMLOCK=
#DefaultLimitLOCKS=
#DefaultLimitSIGPENDING=
#DefaultLimitMSGQUEUE=
#DefaultLimitNICE=
#DefaultLimitRTPRIO=
#DefaultLimitRTTIME=
""".strip()

SYSTEMD_SYSTEM_ORIGIN_ACCOUNTING = """
[Manager]
DefaultCPUAccounting=yes
DefaultMemoryAccounting=yes
# systemd v230 or newer
DefaultIOAccounting=yes
# Deprecated, remove in future
DefaultBlockIOAccounting=no
""".strip()


def test_systemd_docker():
    docker_service = config.SystemdDocker(context_wrap(SYSTEMD_DOCKER))
    assert docker_service.data["Unit"]["After"] == "network.target"
    assert docker_service.data["Service"]["NotifyAccess"] == "all"
    assert docker_service.data["Service"]["Environment"] == "GOTRACEBACK=crash"
    assert docker_service.data["Install"]["WantedBy"] == "multi-user.target"
    assert list(docker_service.data["Install"].keys()) == ["WantedBy"]
    assert docker_service.data["Service"]["ExecStart"] == "/bin/sh -c '/usr/bin/docker-current daemon --authorization-plugin=rhel-push-plugin --exec-opt native.cgroupdriver=systemd $OPTIONS $DOCKER_STORAGE_OPTIONS $DOCKER_NETWORK_OPTIONS $ADD_REGISTRY $BLOCK_REGISTRY $INSECURE_REGISTRY 2>&1 | /usr/bin/forward-journald -tag docker'"


def test_systemd_docker_empty():
    with pytest.raises(ContentException):
        config.SystemdDocker(context_wrap(SYSTEMD_DOCKER_EMPTY))


def test_systemd_openshift_node():
    openshift_node_service = config.SystemdOpenshiftNode(context_wrap(SYSTEMD_OPENSHIFT_NODE))
    assert openshift_node_service.data["Unit"]["Wants"] == "docker.service"
    assert openshift_node_service.data["Unit"]["After"] == ['docker.service', 'openvswitch.service']


def test_systemd_system_conf():
    common_conf_info = config.SystemdSystemConf(context_wrap(SYSTEMD_SYSTEM_CONF))
    assert "Manager" in common_conf_info
    print(common_conf_info.doc)
    assert common_conf_info["Manager"]["RuntimeWatchdogSec"] == "0"
    assert common_conf_info["Manager"]["ShutdownWatchdogSec"] == "10min"


def test_systemd_system_origin_accounting():
    common_system_origin_accounting = config.SystemdOriginAccounting(context_wrap(SYSTEMD_SYSTEM_ORIGIN_ACCOUNTING))
    assert "Manager" in common_system_origin_accounting
    assert common_system_origin_accounting["Manager"]["DefaultCPUAccounting"] == 'True'
    assert common_system_origin_accounting["Manager"]["DefaultBlockIOAccounting"] == 'False'


def test_systemd_logind_conf():
    logind_conf = config.SystemdLogindConf(context_wrap(SYSTEMD_LOGIND_CONF))
    assert "Login" in logind_conf
    assert logind_conf["Login"]["RemoveIPC"] == "False"
    assert logind_conf["Login"]["RuntimeDirectorySize"] == "10%"


def test_systemd_rpcbind_socket_conf():
    rpcbind_socket = config.SystemdRpcbindSocketConf(context_wrap(SYSTEMD_RPCBIND_SOCKET))
    assert "Socket" in rpcbind_socket
    assert rpcbind_socket["Socket"]["ListenStream"] == ['/run/rpcbind.sock', '0.0.0.0:111', '[::]:111']
    assert rpcbind_socket["Socket"]["ListenDatagram"] == ['0.0.0.0:111', '[::]:111']


def test_systemd_dnsmasq_conf():
    dnsmasq_service_conf = config.SystemdDnsmasqServiceConf(context_wrap(SYSTEMD_DNSMASQ_SERVICE))
    assert dnsmasq_service_conf["Unit"]["After"] == "network.target"


def test_systemd_empty():
    with pytest.raises(SkipComponent):
        assert config.SystemdLogindConf(context_wrap('')) is None


def test_doc_examples():
    env = {
            'docker_service': config.SystemdDocker(context_wrap(SYSTEMD_DOCKER)),
            'system_conf': config.SystemdSystemConf(context_wrap(SYSTEMD_SYSTEM_CONF)),
            'system_origin_accounting': config.SystemdOriginAccounting(context_wrap(SYSTEMD_SYSTEM_ORIGIN_ACCOUNTING)),
            'openshift_node_service': config.SystemdOpenshiftNode(context_wrap(SYSTEMD_OPENSHIFT_NODE)),
            'logind_conf': config.SystemdLogindConf(context_wrap(SYSTEMD_LOGIND_CONF)),
            'rpcbind_socket': config.SystemdRpcbindSocketConf(context_wrap(SYSTEMD_RPCBIND_SOCKET)),
            'dnsmasq_service': config.SystemdDnsmasqServiceConf(context_wrap(SYSTEMD_DNSMASQ_SERVICE))
          }
    failed, total = doctest.testmod(config, globs=env)
    assert failed == 0
