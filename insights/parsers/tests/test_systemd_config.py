from insights.parsers.systemd import config
from insights.tests import context_wrap
import doctest


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


def test_systemd_docker():
    docker_service = config.SystemdDocker(context_wrap(SYSTEMD_DOCKER))
    assert docker_service.data["Unit"]["After"] == "network.target"
    assert docker_service.data["Service"]["NotifyAccess"] == "all"
    assert docker_service.data["Service"]["Environment"] == "GOTRACEBACK=crash"
    assert docker_service.data["Install"]["WantedBy"] == "multi-user.target"
    assert list(docker_service.data["Install"].keys()) == ["WantedBy"]
    assert docker_service.data["Service"]["ExecStart"] == "/bin/sh -c '/usr/bin/docker-current daemon --authorization-plugin=rhel-push-plugin --exec-opt native.cgroupdriver=systemd $OPTIONS $DOCKER_STORAGE_OPTIONS $DOCKER_NETWORK_OPTIONS $ADD_REGISTRY $BLOCK_REGISTRY $INSECURE_REGISTRY 2>&1 | /usr/bin/forward-journald -tag docker'"


def test_systemd_openshift_node():
    openshift_node_service = config.SystemdOpenshiftNode(context_wrap(SYSTEMD_OPENSHIFT_NODE))
    assert openshift_node_service.data["Unit"]["Wants"] == "docker.service"
    assert openshift_node_service.data["Unit"]["After"] == ['docker.service', 'openvswitch.service']


def test_systemd_system_conf():
    common_conf_info = config.SystemdSystemConf(context_wrap(SYSTEMD_SYSTEM_CONF))
    assert "Manager" in common_conf_info
    assert common_conf_info["Manager"]["RuntimeWatchdogSec"] == "0"
    assert common_conf_info["Manager"]["ShutdownWatchdogSec"] == "10min"


def test_systemd_logind_conf():
    logind_conf = config.SystemdLogindConf(context_wrap(SYSTEMD_LOGIND_CONF))
    assert "Login" in logind_conf
    assert logind_conf["Login"]["RemoveIPC"] == "False"
    assert logind_conf["Login"]["RuntimeDirectorySize"] == "10%"


def test_doc_examples():
    env = {
            'docker_service': config.SystemdDocker(context_wrap(SYSTEMD_DOCKER)),
            'system_conf': config.SystemdSystemConf(context_wrap(SYSTEMD_SYSTEM_CONF)),
            'openshift_node_service': config.SystemdOpenshiftNode(context_wrap(SYSTEMD_OPENSHIFT_NODE)),
            'logind_conf': config.SystemdLogindConf(context_wrap(SYSTEMD_LOGIND_CONF))
          }
    failed, total = doctest.testmod(config, globs=env)
    assert failed == 0
