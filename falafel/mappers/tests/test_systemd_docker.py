from falafel.mappers.systemd_docker import systemd_docker_service_parser
from falafel.tests import context_wrap

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
ExecStart=/bin/sh -c '/usr/bin/docker-current daemon
          --authorization-plugin=rhel-push-plugin
          --exec-opt native.cgroupdriver=systemd
          $OPTIONS
          $DOCKER_STORAGE_OPTIONS
          $DOCKER_NETWORK_OPTIONS
          $ADD_REGISTRY
          $BLOCK_REGISTRY
          $INSECURE_REGISTRY
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


def test_systemd_docker_service():
    systemd_docker_service = systemd_docker_service_parser(context_wrap(SYSTEMD_DOCKER))
    assert systemd_docker_service["Unit"]["After"] == "network.target"
    assert systemd_docker_service["Service"]["NotifyAccess"] == "all"
    assert systemd_docker_service["Service"]["Environment"] == "GOTRACEBACK=crash"
    assert systemd_docker_service["Install"]["WantedBy"] == "multi-user.target"
