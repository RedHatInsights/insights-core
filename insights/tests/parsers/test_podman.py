import doctest

from insights.parsers import podman
from insights.parsers.podman import PodmanPsAllJson
from insights.tests import context_wrap


PODMAN_PS_ALL_JSON = """
[
    {
        "AutoRemove": false,
        "Command": [
            "/usr/sbin/httpd",
            "-DFOREGROUND"
        ],
        "Created": "2024-01-15T10:30:45.123456789-05:00",
        "CreatedAt": "2024-01-15 10:30:45 -0500 EST",
        "Exited": false,
        "ExitedAt": -62135596800,
        "ExitCode": 0,
        "Id": "03e2861336a76e29155836113ff6560cb70780c32f95062642993b2b3d0fc216",
        "Image": "rhel7_httpd",
        "ImageID": "882ab98aae5394aebe91fe6d8a4297fa0387c3cfd421b2d892bddf218ac373b2",
        "IsInfra": false,
        "Labels": {
            "maintainer": "Red Hat"
        },
        "Mounts": [],
        "Names": [
            "angry_saha"
        ],
        "Namespaces": {},
        "Networks": [
            "podman"
        ],
        "Pid": 12345,
        "Pod": "",
        "PodName": "",
        "Ports": [
            {
                "host_ip": "0.0.0.0",
                "container_port": 80,
                "host_port": 8080,
                "range": 1,
                "protocol": "tcp"
            }
        ],
        "Size": null,
        "StartedAt": 1705330245,
        "State": "running",
        "Status": "Up 37 seconds"
    },
    {
        "AutoRemove": false,
        "Command": [
            "/bin/sh",
            "-c",
            "yum install -y vsftpd-2.2.2-6.el6"
        ],
        "Created": "2024-01-15T09:30:00.123456789-05:00",
        "CreatedAt": "2024-01-15 09:30:00 -0500 EST",
        "Exited": true,
        "ExitedAt": 1705326600,
        "ExitCode": 137,
        "Id": "95516ea08b565e37e2a4bca3333af40a240c368131b77276da8dec629b7fe102",
        "Image": "bd8638c869ea40a9269d87e9af6741574562af9ee013e03ac2745fb5f59e2478",
        "ImageID": "bd8638c869ea40a9269d87e9af6741574562af9ee013e03ac2745fb5f59e2478",
        "IsInfra": false,
        "Labels": null,
        "Mounts": [],
        "Names": [
            "tender_rosalind"
        ],
        "Namespaces": {},
        "Networks": [],
        "Pid": 0,
        "Pod": "",
        "PodName": "",
        "Ports": [],
        "Size": {
            "rootFsSize": 221554338,
            "rwSize": 0
        },
        "StartedAt": 1705326605,
        "State": "exited",
        "Status": "Exited (137) 18 hours ago"
    }
]
""".strip()

PODMAN_PS_JSON_EMPTY = """
[]
""".strip()


def test_podman_ps_json():
    result = PodmanPsAllJson(context_wrap(PODMAN_PS_ALL_JSON))
    assert isinstance(result.data, list)
    assert len(result.data) == 2

    # Test first container
    assert result.data[0]["Id"] == "03e2861336a76e29155836113ff6560cb70780c32f95062642993b2b3d0fc216"
    assert result.data[0]["State"] == "running"
    assert result.data[0]["Status"] == "Up 37 seconds"
    assert result.data[0]["Image"] == "rhel7_httpd"
    assert result.data[0]["Names"] == ["angry_saha"]
    assert result.data[0]["Command"] == ["/usr/sbin/httpd", "-DFOREGROUND"]
    assert result.data[0]["Pid"] == 12345
    assert result.data[0]["ExitCode"] == 0
    assert result.data[0]["Ports"][0]["host_port"] == 8080
    assert result.data[0]["Ports"][0]["container_port"] == 80

    # Test second container
    assert result.data[1]["Id"] == "95516ea08b565e37e2a4bca3333af40a240c368131b77276da8dec629b7fe102"
    assert result.data[1]["State"] == "exited"
    assert result.data[1]["Status"] == "Exited (137) 18 hours ago"
    assert result.data[1]["Names"] == ["tender_rosalind"]
    assert result.data[1]["ExitCode"] == 137
    assert result.data[1]["Pid"] == 0
    assert result.data[1]["Ports"] == []
    assert result.data[1]["Size"] == {
        "rootFsSize": 221554338,
        "rwSize": 0}


def test_podman_ps_json_empty():
    result = PodmanPsAllJson(context_wrap(PODMAN_PS_JSON_EMPTY))
    assert isinstance(result.data, list)
    assert len(result.data) == 0


def test_podman_ps_json_documentation():
    failed_count, _ = doctest.testmod(
        podman,
        globs={'podman_ps_json': PodmanPsAllJson(context_wrap(PODMAN_PS_ALL_JSON))}
    )
    assert failed_count == 0
