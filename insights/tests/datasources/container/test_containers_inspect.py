import json
import pytest

from mock.mock import Mock

from insights.core import dr, filters
from insights.core.exceptions import SkipComponent
from insights.core.spec_factory import DatasourceProvider
from insights.specs import Specs
from insights.specs.datasources.container import running_rhel_containers
from insights.specs.datasources.container.containers_inspect import (LocalSpecs, containers_inspect_data_datasource,
                                                                     running_rhel_containers_id)


INSPECT_1 = """
[
    {
        "Id": "aeaea3ead52724bb525bb2b5c619d67836250756920f0cb9884431ba53b476d8",
        "Created": "2022-10-21T23:47:24.506159696-04:00",
        "Path": "sleep",
        "Args": [
            "1000000"
        ],
        "State": {
            "OciVersion": "1.0.2-dev",
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": false,
            "Dead": false,
            "Pid": 27625,
            "ConmonPid": 27612,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2022-10-21T23:47:24.95366414-04:00",
            "FinishedAt": "0001-01-01T00:00:00Z",
            "Healthcheck": {
                "Status": "",
                "FailingStreak": 0,
                "Log": null
            }
        },
        "Image": "538460c14d75dee1504e56ad8ddb7fe039093b1530ef8f90442a454b9aa3dc8b",
        "ImageName": "registry.access.redhat.com/rhel:latest",
        "Rootfs": "",
        "Pod": "",
        "ResolvConfPath": "/var/run/containers/storage/overlay-containers/aeaea3ead52724bb525bb2b5c619d67836250756920f0cb9884431ba53b476d8/userdata/resolv.conf",
        "HostnamePath": "/var/run/containers/storage/overlay-containers/aeaea3ead52724bb525bb2b5c619d67836250756920f0cb9884431ba53b476d8/userdata/hostname",
        "HostsPath": "/var/run/containers/storage/overlay-containers/aeaea3ead52724bb525bb2b5c619d67836250756920f0cb9884431ba53b476d8/userdata/hosts",
        "StaticDir": "/var/lib/containers/storage/overlay-containers/aeaea3ead52724bb525bb2b5c619d67836250756920f0cb9884431ba53b476d8/userdata",
        "OCIConfigPath": "/var/lib/containers/storage/overlay-containers/aeaea3ead52724bb525bb2b5c619d67836250756920f0cb9884431ba53b476d8/userdata/config.json",
        "OCIRuntime": "runc",
        "ConmonPidFile": "/var/run/containers/storage/overlay-containers/aeaea3ead52724bb525bb2b5c619d67836250756920f0cb9884431ba53b476d8/userdata/conmon.pid",
        "PidFile": "/var/run/containers/storage/overlay-containers/aeaea3ead52724bb525bb2b5c619d67836250756920f0cb9884431ba53b476d8/userdata/pidfile",
        "Name": "eager_bell",
        "RestartCount": 0,
        "Driver": "overlay",
        "MountLabel": "system_u:object_r:container_file_t:s0:c163,c861",
        "ProcessLabel": "system_u:system_r:container_t:s0:c163,c861",
        "AppArmorProfile": "",
        "EffectiveCaps": [
            "CAP_CHOWN",
            "CAP_DAC_OVERRIDE",
            "CAP_FOWNER",
            "CAP_FSETID",
            "CAP_KILL",
            "CAP_NET_BIND_SERVICE",
            "CAP_NET_RAW",
            "CAP_SETFCAP",
            "CAP_SETGID",
            "CAP_SETPCAP",
            "CAP_SETUID",
            "CAP_SYS_CHROOT"
        ],
        "BoundingCaps": [
            "CAP_CHOWN",
            "CAP_DAC_OVERRIDE",
            "CAP_FOWNER",
            "CAP_FSETID",
            "CAP_KILL",
            "CAP_NET_BIND_SERVICE",
            "CAP_NET_RAW",
            "CAP_SETFCAP",
            "CAP_SETGID",
            "CAP_SETPCAP",
            "CAP_SETUID",
            "CAP_SYS_CHROOT"
        ],
        "ExecIDs": [],
        "GraphDriver": {
            "Name": "overlay",
            "Data": {
                "LowerDir": "/var/lib/containers/storage/overlay/37a6f5f155300a48480d92a4ecf01c8694e39c3f8a52f77a39f154e5e0a3598f/diff:/var/lib/containers/storage/overlay/a27a6e18a918e68cdc3db82956cd2c0bba42d34c1513f1a0ab841903762d72a2/diff",
                "MergedDir": "/var/lib/containers/storage/overlay/de84239ee747de645c453b3b81e10849ea3e957e4316bc84ed3d0c32d7de88ee/merged",
                "UpperDir": "/var/lib/containers/storage/overlay/de84239ee747de645c453b3b81e10849ea3e957e4316bc84ed3d0c32d7de88ee/diff",
                "WorkDir": "/var/lib/containers/storage/overlay/de84239ee747de645c453b3b81e10849ea3e957e4316bc84ed3d0c32d7de88ee/work"
            }
        },
        "Mounts": [],
        "Dependencies": [],
        "NetworkSettings": {
            "EndpointID": "",
            "Gateway": "10.88.0.1",
            "IPAddress": "10.88.0.9",
            "IPPrefixLen": 16,
            "IPv6Gateway": "",
            "GlobalIPv6Address": "",
            "GlobalIPv6PrefixLen": 0,
            "MacAddress": "d6:1b:73:04:81:03",
            "Bridge": "",
            "SandboxID": "",
            "HairpinMode": false,
            "LinkLocalIPv6Address": "",
            "LinkLocalIPv6PrefixLen": 0,
            "Ports": {},
            "SandboxKey": "/run/netns/cni-f925b703-b150-a170-20e9-b52030a89784",
            "Networks": {
                "podman": {
                    "EndpointID": "",
                    "Gateway": "10.88.0.1",
                    "IPAddress": "10.88.0.9",
                    "IPPrefixLen": 16,
                    "IPv6Gateway": "",
                    "GlobalIPv6Address": "",
                    "GlobalIPv6PrefixLen": 0,
                    "MacAddress": "d6:1b:73:04:81:03",
                    "NetworkID": "podman",
                    "DriverOpts": null,
                    "IPAMConfig": null,
                    "Links": null
                }
            }
        },
        "ExitCommand": [
            "/usr/bin/podman",
            "--root",
            "/var/lib/containers/storage",
            "--runroot",
            "/var/run/containers/storage",
            "--log-level",
            "warning",
            "--cgroup-manager",
            "systemd",
            "--tmpdir",
            "/var/run/libpod",
            "--runtime",
            "runc",
            "--storage-driver",
            "overlay",
            "--storage-opt",
            "overlay.mountopt=nodev,metacopy=on",
            "--events-backend",
            "file",
            "container",
            "cleanup",
            "aeaea3ead52724bb525bb2b5c619d67836250756920f0cb9884431ba53b476d8"
        ],
        "Namespace": "",
        "IsInfra": false,
        "Config": {
            "Hostname": "aeaea3ead527",
            "Domainname": "",
            "User": "",
            "AttachStdin": false,
            "AttachStdout": false,
            "AttachStderr": false,
            "Tty": false,
            "OpenStdin": false,
            "StdinOnce": false,
            "Env": [
                "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                "TERM=xterm",
                "container=oci",
                "HOME=/root",
                "HOSTNAME=aeaea3ead527"
            ],
            "Cmd": [
                "sleep",
                "1000000"
            ],
            "Image": "registry.access.redhat.com/rhel:latest",
            "Volumes": null,
            "WorkingDir": "/",
            "Entrypoint": "",
            "OnBuild": null,
            "Labels": {
                "architecture": "x86_64",
                "build-date": "2021-07-13T15:12:27.073772",
                "com.redhat.build-host": "cpt-1006.osbs.prod.upshift.rdu2.redhat.com",
                "com.redhat.component": "rhel-server-container",
                "com.redhat.license_terms": "https://www.redhat.com/agreements",
                "description": "The Red Hat Enterprise Linux Base image is designed to be a fully supported foundation for your containerized applications. This base image provides your operations and application teams with the packages, language runtimes and tools necessary to run, maintain, and troubleshoot all of your applications. This image is maintained by Red Hat and updated regularly. It is designed and engineered to be the base layer for all of your containerized applications, middleware and utilities. When used as the source for all of your containers, only one copy will ever be downloaded and cached in your production environment. Use this image just like you would a regular Red Hat Enterprise Linux distribution. Tools like yum, gzip, and bash are provided by default. For further information on how this image was built look at the /root/anacanda-ks.cfg file.",
                "distribution-scope": "public",
                "io.k8s.description": "The Red Hat Enterprise Linux Base image is designed to be a fully supported foundation for your containerized applications. This base image provides your operations and application teams with the packages, language runtimes and tools necessary to run, maintain, and troubleshoot all of your applications. This image is maintained by Red Hat and updated regularly. It is designed and engineered to be the base layer for all of your containerized applications, middleware and utilities. When used as the source for all of your containers, only one copy will ever be downloaded and cached in your production environment. Use this image just like you would a regular Red Hat Enterprise Linux distribution. Tools like yum, gzip, and bash are provided by default. For further information on how this image was built look at the /root/anacanda-ks.cfg file.",
                "io.k8s.display-name": "Red Hat Enterprise Linux 7",
                "io.openshift.tags": "base rhel7",
                "name": "rhel7",
                "release": "437",
                "summary": "Provides the latest release of Red Hat Enterprise Linux 7 in a fully featured and supported base image.",
                "url": "https://access.redhat.com/containers/#/registry.access.redhat.com/rhel7/images/7.9-437",
                "vcs-ref": "a4d1f0b8a9b923ca309da182943d17fe639d8c95",
                "vcs-type": "git",
                "vendor": "Red Hat, Inc.",
                "version": "7.9"
            },
            "Annotations": {
                "io.container.manager": "libpod",
                "io.kubernetes.cri-o.Created": "2022-10-21T23:47:24.506159696-04:00",
                "io.kubernetes.cri-o.TTY": "false",
                "io.podman.annotations.autoremove": "FALSE",
                "io.podman.annotations.init": "FALSE",
                "io.podman.annotations.privileged": "FALSE",
                "io.podman.annotations.publish-all": "FALSE",
                "org.opencontainers.image.stopSignal": "15"
            },
            "StopSignal": 15,
            "CreateCommand": [
                "podman",
                "run",
                "538460c14d75",
                "sleep",
                "1000000"
            ],
            "Umask": "0022",
            "Timeout": 0,
            "StopTimeout": 10
        },
        "HostConfig": {
            "Binds": [],
            "CgroupManager": "systemd",
            "CgroupMode": "host",
            "ContainerIDFile": "",
            "LogConfig": {
                "Type": "k8s-file",
                "Config": null,
                "Path": "/var/lib/containers/storage/overlay-containers/aeaea3ead52724bb525bb2b5c619d67836250756920f0cb9884431ba53b476d8/userdata/ctr.log",
                "Tag": "",
                "Size": "0B"
            },
            "NetworkMode": "bridge",
            "PortBindings": {},
            "RestartPolicy": {
                "Name": "",
                "MaximumRetryCount": 0
            },
            "AutoRemove": false,
            "VolumeDriver": "",
            "VolumesFrom": null,
            "CapAdd": [],
            "CapDrop": [
                "CAP_AUDIT_WRITE",
                "CAP_MKNOD"
            ],
            "Dns": [],
            "DnsOptions": [],
            "DnsSearch": [],
            "ExtraHosts": [],
            "GroupAdd": [],
            "IpcMode": "private",
            "Cgroup": "",
            "Cgroups": "default",
            "Links": null,
            "OomScoreAdj": 0,
            "PidMode": "private",
            "Privileged": false,
            "PublishAllPorts": false,
            "ReadonlyRootfs": false,
            "SecurityOpt": [],
            "Tmpfs": {},
            "UTSMode": "private",
            "UsernsMode": "",
            "ShmSize": 65536000,
            "Runtime": "oci",
            "ConsoleSize": [
                0,
                0
            ],
            "Isolation": "",
            "CpuShares": 0,
            "Memory": 0,
            "NanoCpus": 0,
            "CgroupParent": "",
            "BlkioWeight": 0,
            "BlkioWeightDevice": null,
            "BlkioDeviceReadBps": null,
            "BlkioDeviceWriteBps": null,
            "BlkioDeviceReadIOps": null,
            "BlkioDeviceWriteIOps": null,
            "CpuPeriod": 0,
            "CpuQuota": 0,
            "CpuRealtimePeriod": 0,
            "CpuRealtimeRuntime": 0,
            "CpusetCpus": "",
            "CpusetMems": "",
            "Devices": [],
            "DiskQuota": 0,
            "KernelMemory": 0,
            "MemoryReservation": 0,
            "MemorySwap": 0,
            "MemorySwappiness": 0,
            "OomKillDisable": false,
            "PidsLimit": 2048,
            "Ulimits": [
                {
                    "Name": "RLIMIT_NOFILE",
                    "Soft": 1048576,
                    "Hard": 1048576
                },
                {
                    "Name": "RLIMIT_NPROC",
                    "Soft": 32768,
                    "Hard": 32768
                }
            ],
            "CpuCount": 0,
            "CpuPercent": 0,
            "IOMaximumIOps": 0,
            "IOMaximumBandwidth": 0,
            "CgroupConf": null
        }
    }
]
""".strip()

INSPECT_2 = """
[
    {
        "Id": "28fb57be8bb204e652c472a406e0d99956c8d35d6e88abfc13253d101a00911e",
        "Created": "2022-10-21T23:49:20.02296977-04:00",
        "Path": "sleep",
        "Args": [
            "1000000"
        ],
        "State": {
            "OciVersion": "1.0.2-dev",
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": false,
            "Dead": false,
            "Pid": 27942,
            "ConmonPid": 27921,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2022-10-21T23:49:20.455664509-04:00",
            "FinishedAt": "0001-01-01T00:00:00Z",
            "Healthcheck": {
                "Status": "",
                "FailingStreak": 0,
                "Log": null
            }
        },
        "Image": "538460c14d75dee1504e56ad8ddb7fe039093b1530ef8f90442a454b9aa3dc8b",
        "ImageName": "registry.access.redhat.com/rhel:latest",
        "Rootfs": "",
        "Pod": "",
        "ResolvConfPath": "/var/run/containers/storage/overlay-containers/28fb57be8bb204e652c472a406e0d99956c8d35d6e88abfc13253d101a00911e/userdata/resolv.conf",
        "HostnamePath": "/var/run/containers/storage/overlay-containers/28fb57be8bb204e652c472a406e0d99956c8d35d6e88abfc13253d101a00911e/userdata/hostname",
        "HostsPath": "/var/run/containers/storage/overlay-containers/28fb57be8bb204e652c472a406e0d99956c8d35d6e88abfc13253d101a00911e/userdata/hosts",
        "StaticDir": "/var/lib/containers/storage/overlay-containers/28fb57be8bb204e652c472a406e0d99956c8d35d6e88abfc13253d101a00911e/userdata",
        "OCIConfigPath": "/var/lib/containers/storage/overlay-containers/28fb57be8bb204e652c472a406e0d99956c8d35d6e88abfc13253d101a00911e/userdata/config.json",
        "OCIRuntime": "runc",
        "ConmonPidFile": "/var/run/containers/storage/overlay-containers/28fb57be8bb204e652c472a406e0d99956c8d35d6e88abfc13253d101a00911e/userdata/conmon.pid",
        "PidFile": "/var/run/containers/storage/overlay-containers/28fb57be8bb204e652c472a406e0d99956c8d35d6e88abfc13253d101a00911e/userdata/pidfile",
        "Name": "youthful_goodall",
        "RestartCount": 0,
        "Driver": "overlay",
        "MountLabel": "system_u:object_r:container_file_t:s0:c1022,c1023",
        "ProcessLabel": "",
        "AppArmorProfile": "",
        "EffectiveCaps": [
            "CAP_AUDIT_CONTROL",
            "CAP_AUDIT_READ",
            "CAP_AUDIT_WRITE",
            "CAP_BLOCK_SUSPEND",
            "CAP_CHOWN",
            "CAP_DAC_OVERRIDE",
            "CAP_DAC_READ_SEARCH",
            "CAP_FOWNER",
            "CAP_FSETID",
            "CAP_IPC_LOCK",
            "CAP_IPC_OWNER",
            "CAP_KILL",
            "CAP_LEASE",
            "CAP_LINUX_IMMUTABLE",
            "CAP_MAC_ADMIN",
            "CAP_MAC_OVERRIDE",
            "CAP_MKNOD",
            "CAP_NET_ADMIN",
            "CAP_NET_BIND_SERVICE",
            "CAP_NET_BROADCAST",
            "CAP_NET_RAW",
            "CAP_SETFCAP",
            "CAP_SETGID",
            "CAP_SETPCAP",
            "CAP_SETUID",
            "CAP_SYSLOG",
            "CAP_SYS_ADMIN",
            "CAP_SYS_BOOT",
            "CAP_SYS_CHROOT",
            "CAP_SYS_MODULE",
            "CAP_SYS_NICE",
            "CAP_SYS_PACCT",
            "CAP_SYS_PTRACE",
            "CAP_SYS_RAWIO",
            "CAP_SYS_RESOURCE",
            "CAP_SYS_TIME",
            "CAP_SYS_TTY_CONFIG",
            "CAP_WAKE_ALARM"
        ],
        "BoundingCaps": [
            "CAP_AUDIT_CONTROL",
            "CAP_AUDIT_READ",
            "CAP_AUDIT_WRITE",
            "CAP_BLOCK_SUSPEND",
            "CAP_CHOWN",
            "CAP_DAC_OVERRIDE",
            "CAP_DAC_READ_SEARCH",
            "CAP_FOWNER",
            "CAP_FSETID",
            "CAP_IPC_LOCK",
            "CAP_IPC_OWNER",
            "CAP_KILL",
            "CAP_LEASE",
            "CAP_LINUX_IMMUTABLE",
            "CAP_MAC_ADMIN",
            "CAP_MAC_OVERRIDE",
            "CAP_MKNOD",
            "CAP_NET_ADMIN",
            "CAP_NET_BIND_SERVICE",
            "CAP_NET_BROADCAST",
            "CAP_NET_RAW",
            "CAP_SETFCAP",
            "CAP_SETGID",
            "CAP_SETPCAP",
            "CAP_SETUID",
            "CAP_SYSLOG",
            "CAP_SYS_ADMIN",
            "CAP_SYS_BOOT",
            "CAP_SYS_CHROOT",
            "CAP_SYS_MODULE",
            "CAP_SYS_NICE",
            "CAP_SYS_PACCT",
            "CAP_SYS_PTRACE",
            "CAP_SYS_RAWIO",
            "CAP_SYS_RESOURCE",
            "CAP_SYS_TIME",
            "CAP_SYS_TTY_CONFIG",
            "CAP_WAKE_ALARM"
        ],
        "ExecIDs": [],
        "GraphDriver": {
            "Name": "overlay",
            "Data": {
                "LowerDir": "/var/lib/containers/storage/overlay/37a6f5f155300a48480d92a4ecf01c8694e39c3f8a52f77a39f154e5e0a3598f/diff:/var/lib/containers/storage/overlay/a27a6e18a918e68cdc3db82956cd2c0bba42d34c1513f1a0ab841903762d72a2/diff",
                "MergedDir": "/var/lib/containers/storage/overlay/4be93ab17659c0d187211cd4ab4a49463b3d74f77aebc9e0c958479f9a0a3304/merged",
                "UpperDir": "/var/lib/containers/storage/overlay/4be93ab17659c0d187211cd4ab4a49463b3d74f77aebc9e0c958479f9a0a3304/diff",
                "WorkDir": "/var/lib/containers/storage/overlay/4be93ab17659c0d187211cd4ab4a49463b3d74f77aebc9e0c958479f9a0a3304/work"
            }
        },
        "Mounts": [],
        "Dependencies": [],
        "NetworkSettings": {
            "EndpointID": "",
            "Gateway": "10.88.0.1",
            "IPAddress": "10.88.0.10",
            "IPPrefixLen": 16,
            "IPv6Gateway": "",
            "GlobalIPv6Address": "",
            "GlobalIPv6PrefixLen": 0,
            "MacAddress": "5a:a0:3f:b3:1a:98",
            "Bridge": "",
            "SandboxID": "",
            "HairpinMode": false,
            "LinkLocalIPv6Address": "",
            "LinkLocalIPv6PrefixLen": 0,
            "Ports": {},
            "SandboxKey": "/run/netns/cni-d3dae08c-c0be-7a7d-c53c-c76f720c964c",
            "Networks": {
                "podman": {
                    "EndpointID": "",
                    "Gateway": "10.88.0.1",
                    "IPAddress": "10.88.0.10",
                    "IPPrefixLen": 16,
                    "IPv6Gateway": "",
                    "GlobalIPv6Address": "",
                    "GlobalIPv6PrefixLen": 0,
                    "MacAddress": "5a:a0:3f:b3:1a:98",
                    "NetworkID": "podman",
                    "DriverOpts": null,
                    "IPAMConfig": null,
                    "Links": null
                }
            }
        },
        "ExitCommand": [
            "/usr/bin/podman",
            "--root",
            "/var/lib/containers/storage",
            "--runroot",
            "/var/run/containers/storage",
            "--log-level",
            "warning",
            "--cgroup-manager",
            "systemd",
            "--tmpdir",
            "/var/run/libpod",
            "--runtime",
            "runc",
            "--storage-driver",
            "overlay",
            "--storage-opt",
            "overlay.mountopt=nodev,metacopy=on",
            "--events-backend",
            "file",
            "container",
            "cleanup",
            "28fb57be8bb204e652c472a406e0d99956c8d35d6e88abfc13253d101a00911e"
        ],
        "Namespace": "",
        "IsInfra": false,
        "Config": {
            "Hostname": "28fb57be8bb2",
            "Domainname": "",
            "User": "",
            "AttachStdin": false,
            "AttachStdout": false,
            "AttachStderr": false,
            "Tty": false,
            "OpenStdin": false,
            "StdinOnce": false,
            "Env": [
                "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                "TERM=xterm",
                "container=oci",
                "HOME=/root",
                "HOSTNAME=28fb57be8bb2"
            ],
            "Cmd": [
                "sleep",
                "1000000"
            ],
            "Image": "registry.access.redhat.com/rhel:latest",
            "Volumes": null,
            "WorkingDir": "/",
            "Entrypoint": "",
            "OnBuild": null,
            "Labels": {
                "architecture": "x86_64",
                "build-date": "2021-07-13T15:12:27.073772",
                "com.redhat.build-host": "cpt-1006.osbs.prod.upshift.rdu2.redhat.com",
                "com.redhat.component": "rhel-server-container",
                "com.redhat.license_terms": "https://www.redhat.com/agreements",
                "description": "The Red Hat Enterprise Linux Base image is designed to be a fully supported foundation for your containerized applications. This base image provides your operations and application teams with the packages, language runtimes and tools necessary to run, maintain, and troubleshoot all of your applications. This image is maintained by Red Hat and updated regularly. It is designed and engineered to be the base layer for all of your containerized applications, middleware and utilities. When used as the source for all of your containers, only one copy will ever be downloaded and cached in your production environment. Use this image just like you would a regular Red Hat Enterprise Linux distribution. Tools like yum, gzip, and bash are provided by default. For further information on how this image was built look at the /root/anacanda-ks.cfg file.",
                "distribution-scope": "public",
                "io.k8s.description": "The Red Hat Enterprise Linux Base image is designed to be a fully supported foundation for your containerized applications. This base image provides your operations and application teams with the packages, language runtimes and tools necessary to run, maintain, and troubleshoot all of your applications. This image is maintained by Red Hat and updated regularly. It is designed and engineered to be the base layer for all of your containerized applications, middleware and utilities. When used as the source for all of your containers, only one copy will ever be downloaded and cached in your production environment. Use this image just like you would a regular Red Hat Enterprise Linux distribution. Tools like yum, gzip, and bash are provided by default. For further information on how this image was built look at the /root/anacanda-ks.cfg file.",
                "io.k8s.display-name": "Red Hat Enterprise Linux 7",
                "io.openshift.tags": "base rhel7",
                "name": "rhel7",
                "release": "437",
                "summary": "Provides the latest release of Red Hat Enterprise Linux 7 in a fully featured and supported base image.",
                "url": "https://access.redhat.com/containers/#/registry.access.redhat.com/rhel7/images/7.9-437",
                "vcs-ref": "a4d1f0b8a9b923ca309da182943d17fe639d8c95",
                "vcs-type": "git",
                "vendor": "Red Hat, Inc.",
                "version": "7.9"
            },
            "Annotations": {
                "io.container.manager": "libpod",
                "io.kubernetes.cri-o.Created": "2022-10-21T23:49:20.02296977-04:00",
                "io.kubernetes.cri-o.TTY": "false",
                "io.podman.annotations.autoremove": "FALSE",
                "io.podman.annotations.init": "FALSE",
                "io.podman.annotations.privileged": "TRUE",
                "io.podman.annotations.publish-all": "FALSE",
                "org.opencontainers.image.stopSignal": "15"
            },
            "StopSignal": 15,
            "CreateCommand": [
                "podman",
                "run",
                "--privileged",
                "538460c14d75",
                "sleep",
                "1000000"
            ],
            "Umask": "0022",
            "Timeout": 0,
            "StopTimeout": 10
        },
        "HostConfig": {
            "Binds": [],
            "CgroupManager": "systemd",
            "CgroupMode": "host",
            "ContainerIDFile": "",
            "LogConfig": {
                "Type": "k8s-file",
                "Config": null,
                "Path": "/var/lib/containers/storage/overlay-containers/28fb57be8bb204e652c472a406e0d99956c8d35d6e88abfc13253d101a00911e/userdata/ctr.log",
                "Tag": "",
                "Size": "0B"
            },
            "NetworkMode": "bridge",
            "PortBindings": {},
            "RestartPolicy": {
                "Name": "",
                "MaximumRetryCount": 0
            },
            "AutoRemove": false,
            "VolumeDriver": "",
            "VolumesFrom": null,
            "CapAdd": [],
            "CapDrop": [
                "CAP_BPF",
                "CAP_CHECKPOINT_RESTORE",
                "CAP_PERFMON"
            ],
            "Dns": [],
            "DnsOptions": [],
            "DnsSearch": [],
            "ExtraHosts": [],
            "GroupAdd": [],
            "IpcMode": "private",
            "Cgroup": "",
            "Cgroups": "default",
            "Links": null,
            "OomScoreAdj": 0,
            "PidMode": "private",
            "Privileged": true,
            "PublishAllPorts": false,
            "ReadonlyRootfs": false,
            "SecurityOpt": [],
            "Tmpfs": {},
            "UTSMode": "private",
            "UsernsMode": "",
            "ShmSize": 65536000,
            "Runtime": "oci",
            "ConsoleSize": [
                0,
                0
            ],
            "Isolation": "",
            "CpuShares": 0,
            "Memory": 0,
            "NanoCpus": 0,
            "CgroupParent": "",
            "BlkioWeight": 0,
            "BlkioWeightDevice": null,
            "BlkioDeviceReadBps": null,
            "BlkioDeviceWriteBps": null,
            "BlkioDeviceReadIOps": null,
            "BlkioDeviceWriteIOps": null,
            "CpuPeriod": 0,
            "CpuQuota": 0,
            "CpuRealtimePeriod": 0,
            "CpuRealtimeRuntime": 0,
            "CpusetCpus": "",
            "CpusetMems": "",
            "Devices": [],
            "DiskQuota": 0,
            "KernelMemory": 0,
            "MemoryReservation": 0,
            "MemorySwap": 0,
            "MemorySwappiness": 0,
            "OomKillDisable": false,
            "PidsLimit": 2048,
            "Ulimits": [
                {
                    "Name": "RLIMIT_NOFILE",
                    "Soft": 1048576,
                    "Hard": 1048576
                },
                {
                    "Name": "RLIMIT_NPROC",
                    "Soft": 32768,
                    "Hard": 32768
                }
            ],
            "CpuCount": 0,
            "CpuPercent": 0,
            "IOMaximumIOps": 0,
            "IOMaximumBandwidth": 0,
            "CgroupConf": null
        }
    }
]
""".strip()

INSPECT_3 = """
[
    {
        "Id": "c7efee959ea8910d68eaa5038d3ebf62ae593bfe96757b456c06f16281394921",
        "Created": "2022-10-27T02:53:02.989997608Z",
        "Path": "sleep",
        "Args": [
            "1000000"
        ],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": false,
            "Dead": false,
            "Pid": 32688,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2022-10-27T02:53:03.380640461Z",
            "FinishedAt": "0001-01-01T00:00:00Z"
        },
        "Image": "sha256:acf3e09a39c95d354539b6591298be0b0814f5d74e95e722863241192b9a079b",
        "ResolvConfPath": "/var/lib/docker/containers/c7efee959ea8910d68eaa5038d3ebf62ae593bfe96757b456c06f16281394921/resolv.conf",
        "HostnamePath": "/var/lib/docker/containers/c7efee959ea8910d68eaa5038d3ebf62ae593bfe96757b456c06f16281394921/hostname",
        "HostsPath": "/var/lib/docker/containers/c7efee959ea8910d68eaa5038d3ebf62ae593bfe96757b456c06f16281394921/hosts",
        "LogPath": "",
        "Name": "/quizzical_yalow",
        "RestartCount": 0,
        "Driver": "overlay2",
        "MountLabel": "",
        "ProcessLabel": "",
        "AppArmorProfile": "",
        "ExecIDs": null,
        "HostConfig": {
            "Binds": null,
            "ContainerIDFile": "",
            "LogConfig": {
                "Type": "journald",
                "Config": {}
            },
            "NetworkMode": "default",
            "PortBindings": {},
            "RestartPolicy": {
                "Name": "no",
                "MaximumRetryCount": 0
            },
            "AutoRemove": false,
            "VolumeDriver": "",
            "VolumesFrom": null,
            "CapAdd": null,
            "CapDrop": null,
            "Dns": [],
            "DnsOptions": [],
            "DnsSearch": [],
            "ExtraHosts": null,
            "GroupAdd": null,
            "IpcMode": "",
            "Cgroup": "",
            "Links": null,
            "OomScoreAdj": 0,
            "PidMode": "",
            "Privileged": true,
            "PublishAllPorts": false,
            "ReadonlyRootfs": false,
            "SecurityOpt": [
                "label=disable"
            ],
            "UTSMode": "",
            "UsernsMode": "",
            "ShmSize": 67108864,
            "Runtime": "docker-runc",
            "ConsoleSize": [
                0,
                0
            ],
            "Isolation": "",
            "CpuShares": 0,
            "Memory": 0,
            "NanoCpus": 0,
            "CgroupParent": "",
            "BlkioWeight": 0,
            "BlkioWeightDevice": null,
            "BlkioDeviceReadBps": null,
            "BlkioDeviceWriteBps": null,
            "BlkioDeviceReadIOps": null,
            "BlkioDeviceWriteIOps": null,
            "CpuPeriod": 0,
            "CpuQuota": 0,
            "CpuRealtimePeriod": 0,
            "CpuRealtimeRuntime": 0,
            "CpusetCpus": "",
            "CpusetMems": "",
            "Devices": [],
            "DiskQuota": 0,
            "KernelMemory": 0,
            "MemoryReservation": 0,
            "MemorySwap": 0,
            "MemorySwappiness": -1,
            "OomKillDisable": false,
            "PidsLimit": 0,
            "Ulimits": null,
            "CpuCount": 0,
            "CpuPercent": 0,
            "IOMaximumIOps": 0,
            "IOMaximumBandwidth": 0
        },
        "GraphDriver": {
            "Name": "overlay2",
            "Data": {
                "LowerDir": "/var/lib/docker/overlay2/07b7d0c623c8ffe8951295328e3532f20f08e00922b77c7532c8e7afe0f05dc9-init/diff:/var/lib/docker/overlay2/64c2a13b1b7f27b198c9bb72cd61d766803d2d110646b536068e0021927f0682/diff:/var/lib/docker/overlay2/86b61c65ca8a7f18a48f15ee80e9d032adaee38835a0b0aceca8d02d50d78dd6/diff",
                "MergedDir": "/var/lib/docker/overlay2/07b7d0c623c8ffe8951295328e3532f20f08e00922b77c7532c8e7afe0f05dc9/merged",
                "UpperDir": "/var/lib/docker/overlay2/07b7d0c623c8ffe8951295328e3532f20f08e00922b77c7532c8e7afe0f05dc9/diff",
                "WorkDir": "/var/lib/docker/overlay2/07b7d0c623c8ffe8951295328e3532f20f08e00922b77c7532c8e7afe0f05dc9/work"
            }
        },
        "Mounts": [],
        "Config": {
            "Hostname": "c7efee959ea8",
            "Domainname": "",
            "User": "",
            "AttachStdin": false,
            "AttachStdout": true,
            "AttachStderr": true,
            "Tty": false,
            "OpenStdin": false,
            "StdinOnce": false,
            "Env": [
                "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                "container=oci"
            ],
            "Cmd": [
                "sleep",
                "1000000"
            ],
            "Image": "acf3e09a39c9",
            "Volumes": null,
            "WorkingDir": "",
            "Entrypoint": null,
            "OnBuild": null,
            "Labels": {
                "architecture": "x86_64",
                "build-date": "2022-05-12T23:59:24.895710",
                "com.redhat.build-host": "cpt-1003.osbs.prod.upshift.rdu2.redhat.com",
                "com.redhat.component": "rhel-server-container",
                "com.redhat.license_terms": "https://www.redhat.com/agreements",
                "description": "The Red Hat Enterprise Linux Base image is designed to be a fully supported foundation for your containerized applications. This base image provides your operations and application teams with the packages, language runtimes and tools necessary to run, maintain, and troubleshoot all of your applications. This image is maintained by Red Hat and updated regularly. It is designed and engineered to be the base layer for all of your containerized applications, middleware and utilities. When used as the source for all of your containers, only one copy will ever be downloaded and cached in your production environment. Use this image just like you would a regular Red Hat Enterprise Linux distribution. Tools like yum, gzip, and bash are provided by default. For further information on how this image was built look at the /root/anacanda-ks.cfg file.",
                "distribution-scope": "public",
                "io.k8s.description": "The Red Hat Enterprise Linux Base image is designed to be a fully supported foundation for your containerized applications. This base image provides your operations and application teams with the packages, language runtimes and tools necessary to run, maintain, and troubleshoot all of your applications. This image is maintained by Red Hat and updated regularly. It is designed and engineered to be the base layer for all of your containerized applications, middleware and utilities. When used as the source for all of your containers, only one copy will ever be downloaded and cached in your production environment. Use this image just like you would a regular Red Hat Enterprise Linux distribution. Tools like yum, gzip, and bash are provided by default. For further information on how this image was built look at the /root/anacanda-ks.cfg file.",
                "io.k8s.display-name": "Red Hat Enterprise Linux 7",
                "io.openshift.tags": "base rhel7",
                "name": "rhel7",
                "release": "702",
                "summary": "Provides the latest release of Red Hat Enterprise Linux 7 in a fully featured and supported base image.",
                "url": "https://access.redhat.com/containers/#/registry.access.redhat.com/rhel7/images/7.9-702",
                "vcs-ref": "a4d1f0b8a9b923ca309da182943d17fe639d8c95",
                "vcs-type": "git",
                "vendor": "Red Hat, Inc.",
                "version": "7.9"
            }
        },
        "NetworkSettings": {
            "Bridge": "",
            "SandboxID": "0a9908c68f05eac23b6ed79dce9843b6dda2469e1021671d58d882938bffc7b6",
            "HairpinMode": false,
            "LinkLocalIPv6Address": "",
            "LinkLocalIPv6PrefixLen": 0,
            "Ports": {},
            "SandboxKey": "/var/run/docker/netns/0a9908c68f05",
            "SecondaryIPAddresses": null,
            "SecondaryIPv6Addresses": null,
            "EndpointID": "49f752615a815c97996215e72378d7e049036eef44149e96ae26e9049641d4c1",
            "Gateway": "172.17.0.1",
            "GlobalIPv6Address": "",
            "GlobalIPv6PrefixLen": 0,
            "IPAddress": "172.17.0.3",
            "IPPrefixLen": 16,
            "IPv6Gateway": "",
            "MacAddress": "02:42:ac:11:00:03",
            "Networks": {
                "bridge": {
                    "IPAMConfig": null,
                    "Links": null,
                    "Aliases": null,
                    "NetworkID": "3c2f5c9a9a9c21994ddaee6252842b8a9fb45c24d6dabf00ee36ffb12b70f0b7",
                    "EndpointID": "49f752615a815c97996215e72378d7e049036eef44149e96ae26e9049641d4c1",
                    "Gateway": "172.17.0.1",
                    "IPAddress": "172.17.0.3",
                    "IPPrefixLen": 16,
                    "IPv6Gateway": "",
                    "GlobalIPv6Address": "",
                    "GlobalIPv6PrefixLen": 0,
                    "MacAddress": "02:42:ac:11:00:03"
                }
            }
        }
    }
]
""".strip()

INSPECT_4 = """
[
    {
        "Id": "aeaea3ead52724bb525bb2b5c619d67836250756920f0cb9884431ba53b476d8"
    }
]
""".strip()

INSPECT_5 = """
Error: error inspecting object: no such object: "testnoid"
""".strip()

RELATIVE_PATH = 'insights_containers/containers_inspect'

CONTAINERS_ID_EXPECTED_RESULT = [
    ('podman', 'aeaea3ead52724bb525bb2b5c619d67836250756920f0cb9884431ba53b476d8'),
    ('podman', '28fb57be8bb204e652c472a406e0d99956c8d35d6e88abfc13253d101a00911e'),
    ('podman', '528890e93bf71736e00a87c7a1fa33e5bb03a9a196e5b10faaa9e545e749aa54'),
    ('docker', '38fb57be8bb204e652c472a406e0d99956c8d35d6e88abfc13253d101a00911e'),
    ('docker', '538890e93bf71736e00a87c7a1fa33e5bb03a9a196e5b10faaa9e545e749aa54')
]

EXPECTED_RESULT = [{'Id': 'aeaea3ead527', 'engine': 'podman', 'Image': '538460c14d75dee1504e56ad8ddb7fe039093b1530ef8f90442a454b9aa3dc8b', 'Config|Cmd': ["sleep", "1000000"], 'HostConfig|Privileged': False}, {'Id': '28fb57be8bb2', 'engine': 'podman', 'Image': '538460c14d75dee1504e56ad8ddb7fe039093b1530ef8f90442a454b9aa3dc8b', 'Config|Cmd': ["sleep", "1000000"], 'HostConfig|Privileged': True}, {'Id': 'c7efee959ea8', 'engine': 'docker', 'Image': 'acf3e09a39c95d354539b6591298be0b0814f5d74e95e722863241192b9a079b', 'Config|Cmd': ["sleep", "1000000"], 'HostConfig|Privileged': True}]

EXPECTED_RESULT_NG = [{'Id': '28fb57be8bb2', 'engine': 'podman'}]


def setup_function(func):
    if Specs.container_inspect_keys in filters._CACHE:
        del filters._CACHE[Specs.container_inspect_keys]
    if Specs.container_inspect_keys in filters.FILTERS:
        del filters.FILTERS[Specs.container_inspect_keys]

    if func is test_containers_inspect_datasource or func is test_containers_inspect_datasource_NG_output_1 or func is test_containers_inspect_datasource_NG_output_2:
        filters.add_filter(Specs.container_inspect_keys, ["HostConfig|Privileged", "NoSuchKey|Privileged", "Config|Cmd", "Id", "Image"])
    if func is test_containers_inspect_datasource_no_filter:
        filters.add_filter(Specs.container_inspect_keys, [])


def test_running_rhel_containers_id():
    broker = dr.Broker()
    containers_info = [
        ("registry.access.redhat.com/rhel", "podman", "aeaea3ead52724bb525bb2b5c619d67836250756920f0cb9884431ba53b476d8"),
        ("registry.access.redhat.com/rhel", "podman", "28fb57be8bb204e652c472a406e0d99956c8d35d6e88abfc13253d101a00911e"),
        ("registry.access.redhat.com/rhel", "podman", "528890e93bf71736e00a87c7a1fa33e5bb03a9a196e5b10faaa9e545e749aa54"),
        ("registry.access.redhat.com/rhel", "docker", "38fb57be8bb204e652c472a406e0d99956c8d35d6e88abfc13253d101a00911e"),
        ("registry.access.redhat.com/rhel", "docker", "538890e93bf71736e00a87c7a1fa33e5bb03a9a196e5b10faaa9e545e749aa54")
    ]
    broker[running_rhel_containers] = containers_info
    result = running_rhel_containers_id(broker)
    assert result == CONTAINERS_ID_EXPECTED_RESULT


def test_containers_inspect_datasource():
    containers_inspect_data_1 = Mock()
    containers_inspect_data_2 = Mock()
    containers_inspect_data_3 = Mock()
    containers_inspect_data_1.content = INSPECT_1.splitlines()
    containers_inspect_data_1.cmd = "/usr/bin/podman inspect aeaea3ead527"
    containers_inspect_data_2.content = INSPECT_2.splitlines()
    containers_inspect_data_2.cmd = "/usr/bin/podman inspect 28fb57be8bb2"
    containers_inspect_data_3.content = INSPECT_3.splitlines()
    containers_inspect_data_3.cmd = "/usr/bin/docker inspect c7efee959ea8"
    broker = {LocalSpecs.containers_inspect_data_raw: [containers_inspect_data_1, containers_inspect_data_2, containers_inspect_data_3]}
    result = containers_inspect_data_datasource(broker)
    assert result is not None
    assert isinstance(result, DatasourceProvider)
    expected = DatasourceProvider(content=json.dumps(EXPECTED_RESULT), relative_path=RELATIVE_PATH)
    assert result.content[0] == expected.content[0]
    assert result.relative_path == expected.relative_path


def test_containers_inspect_datasource_no_filter():
    containers_inspect_data_1 = Mock()
    containers_inspect_data_2 = Mock()
    containers_inspect_data_1.content = INSPECT_1.splitlines()
    containers_inspect_data_1.cmd = "/usr/bin/docker inspect aeaea3ead527"
    containers_inspect_data_2.content = INSPECT_2.splitlines()
    containers_inspect_data_2.cmd = "/usr/bin/podman inspect 28fb57be8bb2"
    broker = {LocalSpecs.containers_inspect_data_raw: [containers_inspect_data_1, containers_inspect_data_2]}
    with pytest.raises(SkipComponent) as e:
        containers_inspect_data_datasource(broker)
    assert 'SkipComponent' in str(e)


def test_containers_inspect_datasource_NG_output_1():
    containers_inspect_data_3 = Mock()
    containers_inspect_data_3.content = INSPECT_4.splitlines()
    containers_inspect_data_3.cmd = "/usr/bin/podman inspect 28fb57be8bb2"
    broker = {LocalSpecs.containers_inspect_data_raw: [containers_inspect_data_3]}
    result = containers_inspect_data_datasource(broker)
    assert result is not None
    assert isinstance(result, DatasourceProvider)
    expected = DatasourceProvider(content=json.dumps(EXPECTED_RESULT_NG), relative_path=RELATIVE_PATH)
    assert result.content[0] == expected.content[0]
    assert result.relative_path == expected.relative_path


def test_containers_inspect_datasource_NG_output_2():
    containers_inspect_data_4 = Mock()
    containers_inspect_data_4.content = INSPECT_5.splitlines()
    containers_inspect_data_4.cmd = "/usr/bin/docker inspect aeaea3ead527"
    broker = {LocalSpecs.containers_inspect_data_raw: [containers_inspect_data_4]}
    with pytest.raises(SkipComponent) as e:
        containers_inspect_data_datasource(broker)
    assert 'Unexpected content exception' in str(e)
