import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import podman_inspect
from insights.tests import context_wrap


PODMAN_CONTAINER_INSPECT = """
[
    {
        "ID": "66db151828e9beede0cdd9c17fc9bd5ebb5d125dd036f7230bc6b6433e5c0dda",
        "Created": "2019-08-21T10:38:34.753548542Z",
        "Path": "dumb-init",
        "Args": [
            "--single-child",
            "--",
            "kolla_start"
        ],
        "State": {
            "OciVersion": "1.0.1-dev",
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": false,
            "Dead": false,
            "Pid": 6606,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2019-09-06T19:16:08.066138727Z",
            "FinishedAt": "0001-01-01T00:00:00Z"
        },
        "Image": "a6b8f27df9feb9d820527d413f24ec9b1fcfb12049dd91af5fc188636bebe504",
        "ImageName": "192.168.24.1:8787/rhosp15/openstack-gnocchi-metricd:20190819.1",
        "Rootfs": "",
        "ResolvConfPath": "/var/run/containers/storage/overlay-containers/66db151828e9beede0cdd9c17fc9bd5ebb5d125dd036f7230bc6b6433e5c0dda/userdata/resolv.conf",
        "HostnamePath": "/var/run/containers/storage/overlay-containers/66db151828e9beede0cdd9c17fc9bd5ebb5d125dd036f7230bc6b6433e5c0dda/userdata/hostname",
        "HostsPath": "/var/run/containers/storage/overlay-containers/66db151828e9beede0cdd9c17fc9bd5ebb5d125dd036f7230bc6b6433e5c0dda/userdata/hosts",
        "StaticDir": "/var/lib/containers/storage/overlay-containers/66db151828e9beede0cdd9c17fc9bd5ebb5d125dd036f7230bc6b6433e5c0dda/userdata",
        "LogPath": "/var/log/containers/stdouts/gnocchi_metricd.log",
        "Name": "gnocchi_metricd",
        "RestartCount": 0,
        "Driver": "overlay",
        "MountLabel": "system_u:object_r:container_file_t:s0:c514,c813",
        "ProcessLabel": "system_u:system_r:container_t:s0:c514,c813",
        "AppArmorProfile": "",
        "EffectiveCaps": null,
        "BoundingCaps": [
            "CAP_CHOWN",
            "CAP_DAC_OVERRIDE",
            "CAP_FSETID",
            "CAP_FOWNER",
            "CAP_MKNOD",
            "CAP_NET_RAW",
            "CAP_SETGID",
            "CAP_SETUID",
            "CAP_SETFCAP",
            "CAP_SETPCAP",
            "CAP_NET_BIND_SERVICE",
            "CAP_SYS_CHROOT",
            "CAP_KILL",
            "CAP_AUDIT_WRITE"
        ],
        "ExecIDs": [],
        "GraphDriver": {
            "Name": "overlay",
            "Data": {
                "LowerDir": "/var/lib/containers/storage/overlay/8cf325ff3583d7b6e10f170f85605e14797460f4ee0fa8d4eef2176c27627a26/diff:/var/lib/containers/storage/overlay/3fcda38b3b3199f8d0a1aa61a20d9561ba4ca4805e09ae18d6b50f2854cd5091/diff:/var/lib/containers/storage/overlay/1344d596d37069ebcdd447b67559396b6d046f2f98a63093f229621c544da013/diff:/var/lib/containers/storage/overlay/4faa8d5827f59db011a639ea73621234812291ff51d875f58e1e4197c6239429/diff:/var/lib/containers/storage/overlay/671441d9601355a777b2ce9afceef5a7d0d4890d11ef4f5744e534394ef7c447/diff:/var/lib/containers/storage/overlay/c7269138daa6b23e16efdcbf7ee323ba42fba93eb2406192ac22631bdd0cb4e3/diff",
                "MergedDir": "/var/lib/containers/storage/overlay/87b994364ae69db1d3d8ff1e19a5882f230514bce4a3362ee25bfe618f9fa5ee/merged",
                "UpperDir": "/var/lib/containers/storage/overlay/87b994364ae69db1d3d8ff1e19a5882f230514bce4a3362ee25bfe618f9fa5ee/diff",
                "WorkDir": "/var/lib/containers/storage/overlay/87b994364ae69db1d3d8ff1e19a5882f230514bce4a3362ee25bfe618f9fa5ee/work"
            }
        },
        "Mounts": [
            {
                "destination": "/sys",
                "type": "sysfs",
                "source": "sysfs",
                "options": [
                    "nosuid",
                    "noexec",
                    "nodev",
                    "ro"
                ]
            },
            {
                "destination": "/dev",
                "type": "tmpfs",
                "source": "tmpfs",
                "options": [
                    "nosuid",
                    "strictatime",
                    "mode=755",
                    "size=65536k"
                ]
            },
            {
                "destination": "/etc/pki/ca-trust/source/anchors",
                "type": "bind",
                "source": "/etc/pki/ca-trust/source/anchors",
                "options": [
                    "ro",
                    "rbind",
                    "rprivate"
                ]
            },
            {
                "destination": "/var/lib/kolla/config_files/src-ceph",
                "type": "bind",
                "source": "/etc/ceph",
                "options": [
                    "ro",
                    "rbind",
                    "rprivate"
                ]
            }
        ],
        "Dependencies": [],
        "NetworkSettings": {
            "Bridge": "",
            "SandboxID": "",
            "HairpinMode": false,
            "LinkLocalIPv6Address": "",
            "LinkLocalIPv6PrefixLen": 0,
            "Ports": [],
            "SandboxKey": "",
            "SecondaryIPAddresses": null,
            "SecondaryIPv6Addresses": null,
            "EndpointID": "",
            "Gateway": "",
            "GlobalIPv6Address": "",
            "GlobalIPv6PrefixLen": 0,
            "IPAddress": "",
            "IPPrefixLen": 0,
            "IPv6Gateway": "",
            "MacAddress": ""
        },
        "ExitCommand": [
            "/usr/bin/podman",
            "--root",
            "/var/lib/containers/storage",
            "--runroot",
            "/var/run/containers/storage",
            "--log-level",
            "error",
            "--cgroup-manager",
            "systemd",
            "--tmpdir",
            "/var/run/libpod",
            "--storage-driver",
            "overlay",
            "container",
            "cleanup",
            "66db151828e9beede0cdd9c17fc9bd5ebb5d125dd036f7230bc6b6433e5c0dda"
        ],
        "Namespace": "",
        "IsInfra": false,
        "HostConfig": {
            "ContainerIDFile": "",
            "LogConfig": null,
            "NetworkMode": "host",
            "PortBindings": null,
            "AutoRemove": false,
            "CapAdd": [],
            "CapDrop": [],
            "DNS": [],
            "DNSOptions": [],
            "DNSSearch": [],
            "ExtraHosts": null,
            "GroupAdd": null,
            "IpcMode": "",
            "Cgroup": "host",
            "OomScoreAdj": 0,
            "PidMode": "",
            "Privileged": false,
            "PublishAllPorts": false,
            "ReadonlyRootfs": false,
            "SecurityOpt": [],
            "UTSMode": "",
            "UsernsMode": "",
            "ShmSize": 65536000,
            "Runtime": "runc",
            "ConsoleSize": null,
            "CpuShares": null,
            "Memory": 0,
            "NanoCpus": 0,
            "CgroupParent": "",
            "BlkioWeight": null,
            "BlkioWeightDevice": null,
            "BlkioDeviceReadBps": null,
            "BlkioDeviceWriteBps": null,
            "BlkioDeviceReadIOps": null,
            "BlkioDeviceWriteIOps": null,
            "CpuPeriod": null,
            "CpuQuota": null,
            "CpuRealtimePeriod": null,
            "CpuRealtimeRuntime": null,
            "CpuSetCpus": "",
            "CpuSetMems": "",
            "Devices": null,
            "DiskQuota": 0,
            "KernelMemory": null,
            "MemoryReservation": null,
            "MemorySwap": null,
            "MemorySwappiness": null,
            "OomKillDisable": false,
            "PidsLimit": null,
            "Ulimits": [],
            "CpuCount": 0,
            "CpuPercent": 0,
            "IOMaximumIOps": 0,
            "IOMaximumBandwidth": 0,
            "Tmpfs": []
        },
        "Config": {
            "Hostname": "controller-0",
            "Domainname": "",
            "User": {
                "uid": 0,
                "gid": 0
            },
            "AttachStdin": false,
            "AttachStdout": false,
            "AttachStderr": false,
            "Tty": false,
            "OpenStdin": false,
            "StdinOnce": false,
            "Env": [
                "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                "TERM=xterm",
                "HOSTNAME=controller-0",
                "container=oci",
                "KOLLA_CONFIG_STRATEGY=COPY_ALWAYS",
                "TRIPLEO_CONFIG_HASH=3faca5d7029273bb994631cb4a075e0f",
                "KOLLA_INSTALL_TYPE=binary",
                "KOLLA_INSTALL_METATYPE=rhos",
                "KOLLA_DISTRO_PYTHON_VERSION=3.6",
                "KOLLA_BASE_DISTRO=rhel",
                "PS1=$(tput bold)($(printenv KOLLA_SERVICE_NAME))$(tput sgr0)[$(id -un)@$(hostname -s) $(pwd)]$ "
            ],
            "Cmd": [
                "dumb-init",
                "--single-child",
                "--",
                "kolla_start"
            ],
            "Image": "192.168.24.1:8787/rhosp15/openstack-gnocchi-metricd:20190819.1",
            "Volumes": null,
            "WorkingDir": "/",
            "Entrypoint": "dumb-init --single-child --",
            "Labels": {
                "architecture": "x86_64",
                "authoritative-source-url": "registry.access.redhat.com",
                "batch": "20190819.1",
                "build-date": "2019-08-19T20:42:03.096048",
                "com.redhat.build-host": "cpt-1004.osbs.prod.upshift.rdu2.redhat.com",
                "com.redhat.component": "openstack-gnocchi-metricd-container",
                "com.redhat.license_terms": "https://www.redhat.com/en/about/red-hat-end-user-license-agreements",
                "config_id": "tripleo_step5",
                "container_name": "gnocchi_metricd",
                "description": "Red Hat OpenStack Platform 15.0 gnocchi-metricd",
                "distribution-scope": "public",
                "io.k8s.description": "Red Hat OpenStack Platform 15.0 gnocchi-metricd",
                "io.k8s.display-name": "Red Hat OpenStack Platform 15.0 gnocchi-metricd",
                "io.openshift.expose-services": "",
                "io.openshift.tags": "rhosp osp openstack osp-15.0",
                "maintainer": "Red Hat, Inc.",
                "managed_by": "paunch",
                "name": "rhosp15/openstack-gnocchi-metricd",
                "release": "58",
                "summary": "Red Hat OpenStack Platform 15.0 gnocchi-metricd",
                "url": "https://access.redhat.com/containers/#/registry.access.redhat.com/rhosp15/openstack-gnocchi-metricd/images/15.0-58",
                "vcs-ref": "18e6ecd9e04f6590526657b85423347b7543391a",
                "vcs-type": "git",
                "vendor": "Red Hat, Inc.",
                "version": "15.0"
            },
            "Annotations": {
                "io.kubernetes.cri-o.ContainerType": "sandbox",
                "io.kubernetes.cri-o.TTY": "false"
            },
            "StopSignal": 15
        }
    }
]
""".splitlines()

PODMAN_IMAGE_INSPECT = """
[
    {
        "Id": "013125b8a088f45be8f85f88b5504f05c02463b10a6eea2b66809a262bb911ca",
        "Digest": "sha256:f9662cdd45e3db182372a4fa6bfff10e1c601cc785bac09ccae3b18f0bc429df",
        "RepoTags": [
            "192.168.24.1:8787/rhosp15/openstack-rabbitmq:20190819.1",
            "192.168.24.1:8787/rhosp15/openstack-rabbitmq:pcmklatest"
        ],
        "RepoDigests": [
            "192.168.24.1:8787/rhosp15/openstack-rabbitmq@sha256:f9662cdd45e3db182372a4fa6bfff10e1c601cc785bac09ccae3b18f0bc429df",
            "192.168.24.1:8787/rhosp15/openstack-rabbitmq@sha256:f9662cdd45e3db182372a4fa6bfff10e1c601cc785bac09ccae3b18f0bc429df"
        ],
        "Parent": "",
        "Comment": "",
        "Created": "2019-08-19T19:39:31.939714Z",
        "Config": {
            "User": "rabbitmq",
            "Env": [
                "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                "container=oci",
                "KOLLA_BASE_DISTRO=rhel",
                "KOLLA_INSTALL_TYPE=binary",
                "KOLLA_INSTALL_METATYPE=rhos",
                "KOLLA_DISTRO_PYTHON_VERSION=3.6",
                "PS1=$(tput bold)($(printenv KOLLA_SERVICE_NAME))$(tput sgr0)[$(id -un)@$(hostname -s) $(pwd)]$ "
            ],
            "Entrypoint": [
                "dumb-init",
                "--single-child",
                "--"
            ],
            "Cmd": [
                "kolla_start"
            ],
            "Labels": {
                "architecture": "x86_64",
                "authoritative-source-url": "registry.access.redhat.com",
                "batch": "20190819.1",
                "build-date": "2019-08-19T19:38:18.798307",
                "com.redhat.build-host": "cpt-1003.osbs.prod.upshift.rdu2.redhat.com",
                "com.redhat.component": "openstack-rabbitmq-container",
                "com.redhat.license_terms": "https://www.redhat.com/en/about/red-hat-end-user-license-agreements",
                "description": "Red Hat OpenStack Platform 15.0 rabbitmq",
                "distribution-scope": "public",
                "io.k8s.description": "Red Hat OpenStack Platform 15.0 rabbitmq",
                "io.k8s.display-name": "Red Hat OpenStack Platform 15.0 rabbitmq",
                "io.openshift.expose-services": "",
                "io.openshift.tags": "rhosp osp openstack osp-15.0",
                "maintainer": "Red Hat, Inc.",
                "name": "rhosp15/openstack-rabbitmq",
                "release": "64",
                "summary": "Red Hat OpenStack Platform 15.0 rabbitmq",
                "url": "https://access.redhat.com/containers/#/registry.access.redhat.com/rhosp15/openstack-rabbitmq/images/15.0-64",
                "vcs-ref": "292efe508dcdf588e92503273c5abcc89af574d6",
                "vcs-type": "git",
                "vendor": "Red Hat, Inc.",
                "version": "15.0"
            },
            "StopSignal": "SIGTERM"
        },
        "Version": "1.13.1",
        "Author": "",
        "Architecture": "amd64",
        "Os": "linux",
        "Size": 542316943,
        "VirtualSize": 542316943,
        "GraphDriver": {
            "Name": "overlay",
            "Data": {
                "LowerDir": "/var/lib/containers/storage/overlay/4faa8d5827f59db011a639ea73621234812291ff51d875f58e1e4197c6239429/diff:/var/lib/containers/storage/overlay/671441d9601355a777b2ce9afceef5a7d0d4890d11ef4f5744e534394ef7c447/diff:/var/lib/containers/storage/overlay/c7269138daa6b23e16efdcbf7ee323ba42fba93eb2406192ac22631bdd0cb4e3/diff",
                "MergedDir": "/var/lib/containers/storage/overlay/b25ec647038ff1d35285422ddbedb5b5c7d36d64e67fcbbd2a2f205dc2aa1eb5/merged",
                "UpperDir": "/var/lib/containers/storage/overlay/b25ec647038ff1d35285422ddbedb5b5c7d36d64e67fcbbd2a2f205dc2aa1eb5/diff",
                "WorkDir": "/var/lib/containers/storage/overlay/b25ec647038ff1d35285422ddbedb5b5c7d36d64e67fcbbd2a2f205dc2aa1eb5/work"
            }
        },
        "RootFS": {
            "Type": "layers",
            "Layers": [
                "sha256:c7269138daa6b23e16efdcbf7ee323ba42fba93eb2406192ac22631bdd0cb4e3",
                "sha256:786011f2f6269cc2512d58fd7d6c8feac1330754b12b4ffacfcaa8bd685ed898",
                "sha256:d74075ef7bbc7f840dec3cafc7bf8f82e900ee2f8b4a4d328448965bd8e398ce",
                "sha256:272314807b476c2c183edd6427bd450cea885976446afcdbd6b52ad47943a60f"
            ]
        },
        "Labels": {
            "architecture": "x86_64",
            "authoritative-source-url": "registry.access.redhat.com",
            "batch": "20190819.1",
            "build-date": "2019-08-19T19:38:18.798307",
            "com.redhat.build-host": "cpt-1003.osbs.prod.upshift.rdu2.redhat.com",
            "com.redhat.component": "openstack-rabbitmq-container",
            "com.redhat.license_terms": "https://www.redhat.com/en/about/red-hat-end-user-license-agreements",
            "description": "Red Hat OpenStack Platform 15.0 rabbitmq",
            "distribution-scope": "public",
            "io.k8s.description": "Red Hat OpenStack Platform 15.0 rabbitmq",
            "io.k8s.display-name": "Red Hat OpenStack Platform 15.0 rabbitmq",
            "io.openshift.expose-services": "",
            "io.openshift.tags": "rhosp osp openstack osp-15.0",
            "maintainer": "Red Hat, Inc.",
            "name": "rhosp15/openstack-rabbitmq",
            "release": "64",
            "summary": "Red Hat OpenStack Platform 15.0 rabbitmq",
            "url": "https://access.redhat.com/containers/#/registry.access.redhat.com/rhosp15/openstack-rabbitmq/images/15.0-64",
            "vcs-ref": "292efe508dcdf588e92503273c5abcc89af574d6",
            "vcs-type": "git",
            "vendor": "Red Hat, Inc.",
            "version": "15.0"
        },
        "Annotations": {},
        "ManifestType": "application/vnd.docker.distribution.manifest.v2+json",
        "User": "rabbitmq",
        "History": [
            {
                "created": "2019-07-15T05:10:57.589513378Z",
                "comment": "Imported from -"
            },
            {
                "created": "2019-07-15T05:11:04.220661Z"
            },
            {
                "created": "2019-08-19T19:24:22.99993Z"
            },
            {
                "created": "2019-08-19T19:39:31.939714Z"
            }
        ]
    }
]
""".splitlines()

PODMAN_CONTAINER_INSPECT_TRUNCATED = """
[
    {
        "ID": "66db151828e9beede0cdd9c17fc9bd5ebb5d125dd036f7230bc6b6433e5c0dda",
        "Created": "2019-08-21T10:38:34.753548542Z",
        "Path": "dumb-init",
"""


def test_podman_object_container_inspect():
    result = podman_inspect.PodmanInspect(context_wrap(PODMAN_CONTAINER_INSPECT))
    assert result.get('ID') == "66db151828e9beede0cdd9c17fc9bd5ebb5d125dd036f7230bc6b6433e5c0dda"
    assert result.get('NetworkSettings').get('HairpinMode') is False
    assert result.get('Config').get('Env') == [
                "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                "TERM=xterm",
                "HOSTNAME=controller-0",
                "container=oci",
                "KOLLA_CONFIG_STRATEGY=COPY_ALWAYS",
                "TRIPLEO_CONFIG_HASH=3faca5d7029273bb994631cb4a075e0f",
                "KOLLA_INSTALL_TYPE=binary",
                "KOLLA_INSTALL_METATYPE=rhos",
                "KOLLA_DISTRO_PYTHON_VERSION=3.6",
                "KOLLA_BASE_DISTRO=rhel",
                "PS1=$(tput bold)($(printenv KOLLA_SERVICE_NAME))$(tput sgr0)[$(id -un)@$(hostname -s) $(pwd)]$ "
            ]
    assert result.get('GraphDriver').get('Name') == 'overlay'


def test_podman_object_image_inspect():
    result = podman_inspect.PodmanInspect(context_wrap(PODMAN_IMAGE_INSPECT))
    assert result.get('Id') == "013125b8a088f45be8f85f88b5504f05c02463b10a6eea2b66809a262bb911ca"
    assert result.get('Size') == 542316943
    assert result.get('Digest') == "sha256:f9662cdd45e3db182372a4fa6bfff10e1c601cc785bac09ccae3b18f0bc429df"


def test_podman_container_inspect_truncated_input():
    with pytest.raises(SkipComponent):
        podman_inspect.PodmanInspectContainer(context_wrap(PODMAN_CONTAINER_INSPECT_TRUNCATED))


def test_doc_test():
    dic = podman_inspect.PodmanInspectContainer(context_wrap(PODMAN_CONTAINER_INSPECT))
    dii = podman_inspect.PodmanInspectImage(context_wrap(PODMAN_IMAGE_INSPECT))
    env = {
            'container': dic,
            'image': dii,
    }
    failed, total = doctest.testmod(podman_inspect, globs=env)
    assert failed == 0
