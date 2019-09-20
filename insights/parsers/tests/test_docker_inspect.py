from insights.parsers import docker_inspect
from insights.tests import context_wrap

DOCKER_CONTAINER_INSPECT = """
[
{
    "Id": "97d7cd1a5d8fd7730e83bb61ecbc993742438e966ac5c11910776b5d53f4ae07",
    "Created": "2016-06-23T05:12:25.433469799Z",
    "Path": "/bin/bash",
    "Args": [],
    "State": {
        "Status": "running",
        "Running": true,
        "Paused": false,
        "Restarting": false,
        "OOMKilled": false,
        "Dead": false,
        "Pid": 15096,
        "ExitCode": 0,
        "Error": "",
        "StartedAt": "2016-06-23T05:37:56.925378831Z",
        "FinishedAt": "2016-06-23T05:33:02.012653984Z"
    },
    "Image": "882ab98aae5394aebe91fe6d8a4297fa0387c3cfd421b2d892bddf218ac373b2",
    "ResolvConfPath": "/var/lib/docker/containers/97d7cd1a5d8fd7730e83bb61ecbc993742438e966ac5c11910776b5d53f4ae07/resolv.conf",
    "HostnamePath": "/var/lib/docker/containers/97d7cd1a5d8fd7730e83bb61ecbc993742438e966ac5c11910776b5d53f4ae07/hostname",
    "HostsPath": "/var/lib/docker/containers/97d7cd1a5d8fd7730e83bb61ecbc993742438e966ac5c11910776b5d53f4ae07/hosts",
    "LogPath": "/var/lib/docker/containers/97d7cd1a5d8fd7730e83bb61ecbc993742438e966ac5c11910776b5d53f4ae07/97d7cd1a5d8fd7730e83bb61ecbc993742438e966ac5c11910776b5d53f4ae07-json.log",
    "Name": "/hehe2",
    "RestartCount": 0,
    "Driver": "devicemapper",
    "ExecDriver": "native-0.2",
    "MountLabel": "system_u:object_r:svirt_sandbox_file_t:s0:c429,c690",
    "ProcessLabel": "system_u:system_r:svirt_lxc_net_t:s0:c429,c690",
    "AppArmorProfile": "",
    "ExecIDs": null,
    "HostConfig": {
        "Binds": null,
        "ContainerIDFile": "",
        "LxcConf": [],
        "Memory": 0,
        "MemoryReservation": 0,
        "MemorySwap": 0,
        "KernelMemory": 0,
        "CpuShares": 0,
        "CpuPeriod": 0,
        "CpusetCpus": "",
        "CpusetMems": "",
        "CpuQuota": 0,
        "BlkioWeight": 0,
        "OomKillDisable": false,
        "MemorySwappiness": -1,
        "Privileged": false,
        "PortBindings": {},
        "Links": null,
        "PublishAllPorts": false,
        "Dns": [],
        "DnsOptions": [],
        "DnsSearch": [],
        "ExtraHosts": null,
        "VolumesFrom": null,
        "Devices": [],
        "NetworkMode": "default",
        "IpcMode": "",
        "PidMode": "",
        "UTSMode": "",
        "CapAdd": null,
        "CapDrop": null,
        "GroupAdd": null,
        "RestartPolicy": {
            "Name": "no",
            "MaximumRetryCount": 0
        },
        "SecurityOpt": null,
        "ReadonlyRootfs": false,
        "Ulimits": null,
        "Sysctls": {},
        "LogConfig": {
            "Type": "json-file",
            "Config": {
                "max-file": "7",
                "max-size": "10m"
            }
        },
        "CgroupParent": "",
        "ConsoleSize": [
            0,
            0
        ],
        "VolumeDriver": "",
        "ShmSize": 67108864
    },
    "GraphDriver": {
        "Name": "devicemapper",
        "Data": {
            "DeviceId": "433",
            "DeviceName": "docker-253:0-71431059-97d7cd1a5d8fd7730e83bb61ecbc993742438e966ac5c11910776b5d53f4ae07",
            "DeviceSize": "107374182400"
        }
    },
    "Mounts": [],
    "Config": {
        "Hostname": "97d7cd1a5d8f",
        "Domainname": "",
        "User": "root",
        "AttachStdin": true,
        "AttachStdout": true,
        "AttachStderr": true,
        "Tty": true,
        "OpenStdin": true,
        "StdinOnce": true,
        "Env": [
            "container=docker",
            "PKGM=yum",
            "PATH=/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin"
        ],
        "Cmd": [
            "/bin/bash"
        ],
        "Image": "rhel7_imagemagick",
        "Volumes": null,
        "WorkingDir": "",
        "Entrypoint": null,
        "OnBuild": null,
        "Labels": {
            "Architecture": "x86_64",
            "Authoritative_Registry": "registry.access.redhat.com",
            "BZComponent": "rhel-server-docker",
            "Build_Host": "rcm-img03.build.eng.bos.redhat.com",
            "Name": "rhel7/rhel",
            "Release": "61",
            "Vendor": "Red Hat, Inc.",
            "Version": "7.2",
            "io.projectatomic.Temporary": "true"
        },
        "StopSignal": "SIGTERM"
    },
    "NetworkSettings": {
        "Bridge": "",
        "SandboxID": "f1cce5397340364aff043879ff5bd7e2ce2fcc5b81cfb7fe1833ce7b57eb6cf8",
        "HairpinMode": false,
        "LinkLocalIPv6Address": "",
        "LinkLocalIPv6PrefixLen": 0,
        "Ports": {},
        "SandboxKey": "/var/run/docker/netns/f1cce5397340",
        "SecondaryIPAddresses": null,
        "SecondaryIPv6Addresses": null,
        "EndpointID": "59be4c94b2a1346eb0ec16472bc132e071d18733fd956c34b3b1defff9bba389",
        "Gateway": "172.17.0.1",
        "GlobalIPv6Address": "",
        "GlobalIPv6PrefixLen": 0,
        "IPAddress": "172.17.0.2",
        "IPPrefixLen": 16,
        "IPv6Gateway": "",
        "MacAddress": "02:42:ac:11:00:02",
        "Networks": {
            "bridge": {
                "EndpointID": "59be4c94b2a1346eb0ec16472bc132e071d18733fd956c34b3b1defff9bba389",
                "Gateway": "172.17.0.1",
                "IPAddress": "172.17.0.2",
                "IPPrefixLen": 16,
                "IPv6Gateway": "",
                "GlobalIPv6Address": "",
                "GlobalIPv6PrefixLen": 0,
                "MacAddress": "02:42:ac:11:00:02"
            }
        }
    }
}
]
""".splitlines()

DOCKER_IMAGE_INSPECT = """
[
{
    "Id": "882ab98aae5394aebe91fe6d8a4297fa0387c3cfd421b2d892bddf218ac373b2",
    "RepoTags": [
        "rhel7_imagemagick:latest"
    ],
    "RepoDigests": [],
    "Parent": "34c167d900afb820ecab622a214ce3207af80ec755c0dcb6165b425087ddbc3a",
    "Comment": "",
    "Created": "2016-06-23T03:39:15.068803433Z",
    "Container": "65410bf8809af52d2074c882917ea0651b119a91f460c1037bc99d4d5976532a",
    "ContainerConfig": {
        "Hostname": "cf3092658f01",
        "Domainname": "",
        "User": "root",
        "AttachStdin": false,
        "AttachStdout": false,
        "AttachStderr": false,
        "Tty": false,
        "OpenStdin": false,
        "StdinOnce": false,
        "Env": [
            "container=docker",
            "PKGM=yum",
            "PATH=/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin"
        ],
        "Cmd": [
            "/bin/sh",
            "-c",
            "yum install -y ImageMagick-6.7.8.9-10.el7"
        ],
        "Image": "34c167d900afb820ecab622a214ce3207af80ec755c0dcb6165b425087ddbc3a",
        "Volumes": null,
        "WorkingDir": "",
        "Entrypoint": null,
        "OnBuild": [],
        "Labels": {
            "Architecture": "x86_64",
            "Authoritative_Registry": "registry.access.redhat.com",
            "BZComponent": "rhel-server-docker",
            "Build_Host": "rcm-img03.build.eng.bos.redhat.com",
            "Name": "rhel7/rhel",
            "Release": "61",
            "Vendor": "Red Hat, Inc.",
            "Version": "7.2"
        }
    },
    "DockerVersion": "1.9.1",
    "Author": "",
    "Config": {
        "Hostname": "cf3092658f01",
        "Domainname": "",
        "User": "root",
        "AttachStdin": false,
        "AttachStdout": false,
        "AttachStderr": false,
        "Tty": false,
        "OpenStdin": false,
        "StdinOnce": false,
        "Env": [
            "container=docker",
            "PKGM=yum",
            "PATH=/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin"
        ],
        "Cmd": [
            "/usr/bin/bash"
        ],
        "Image": "34c167d900afb820ecab622a214ce3207af80ec755c0dcb6165b425087ddbc3a",
        "Volumes": null,
        "WorkingDir": "",
        "Entrypoint": null,
        "OnBuild": [],
        "Labels": {
            "Architecture": "x86_64",
            "Authoritative_Registry": "registry.access.redhat.com",
            "BZComponent": "rhel-server-docker",
            "Build_Host": "rcm-img03.build.eng.bos.redhat.com",
            "Name": "rhel7/rhel",
            "Release": "61",
            "Vendor": "Red Hat, Inc.",
            "Version": "7.2"
        }
    },
    "Architecture": "amd64",
    "Os": "linux",
    "Size": 580094174,
    "VirtualSize": 785437820,
    "GraphDriver": {
        "Name": "devicemapper",
        "Data": {
            "DeviceId": "431",
            "DeviceName": "docker-253:0-71431059-882ab98aae5394aebe91fe6d8a4297fa0387c3cfd421b2d892bddf218ac373b2",
            "DeviceSize": "107374182400"
        }
    }
}
]
""".splitlines()


DOCKER_CONTAINER_INSPECT_TRUNCATED = """
[
{
    "Id": "97d7cd1a5d8fd7730e83bb61ecbc993742438e966ac5c11910776b5d53f4ae07",
    "Created": "2016-06-23T05:12:25.433469799Z",
    "Path": "/bin/bash",
"""


def test_docker_object_container_inspect():
    result = docker_inspect.DockerInspect(context_wrap(DOCKER_CONTAINER_INSPECT))
    assert result.get('Id') == "97d7cd1a5d8fd7730e83bb61ecbc993742438e966ac5c11910776b5d53f4ae07"
    assert result.get('NetworkSettings').get('HairpinMode') is False
    assert result.get('Config').get('Env') == ['container=docker', 'PKGM=yum', 'PATH=/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin']
    assert result.get('GraphDriver').get('Data').get('DeviceSize') == '107374182400'


def test_docker_object_image_inspect():
    result = docker_inspect.DockerInspect(context_wrap(DOCKER_IMAGE_INSPECT))
    assert result.get('Id') == "882ab98aae5394aebe91fe6d8a4297fa0387c3cfd421b2d892bddf218ac373b2"
    assert result.get('Size') == 580094174
    assert result.get('Config').get('AttachStdin') is False
    assert result.get('RepoDigests') == []


def test_docker_container_inspect_truncated_input():
    result = docker_inspect.DockerInspectContainer(context_wrap(DOCKER_CONTAINER_INSPECT_TRUNCATED))
    assert result.data == {}
