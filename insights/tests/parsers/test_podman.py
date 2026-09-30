import doctest

import pytest

from insights.parsers import podman
from insights.parsers.podman import PodmanPsAllJson, PodmanPsAllJsonRootless
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

PODMAN_PS_MULTI_JSON = """
[
    {
        "Id": "aaa",
        "Image": "quay.io/foreman/foreman:3.16",
        "Names": ["foreman"],
        "State": "running"
    },
    {
        "Id": "bbb",
        "Image": "quay.io/foreman/foreman:3.16",
        "Names": ["dynflow-sidekiq-worker"],
        "State": "running"
    },
    {
        "Id": "ccc",
        "Image": "quay.io/foreman/foreman-proxy:3.16",
        "Names": ["foreman-proxy"],
        "State": "exited"
    }
]
""".strip()


def test_podman_ps_json():
    result = PodmanPsAllJson(context_wrap(PODMAN_PS_ALL_JSON))
    assert isinstance(result.data, list)
    assert len(result.data) == 2

    # Test first container
    assert (
        result.data[0]["Id"] == "03e2861336a76e29155836113ff6560cb70780c32f95062642993b2b3d0fc216"
    )
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
    assert (
        result.data[1]["Id"] == "95516ea08b565e37e2a4bca3333af40a240c368131b77276da8dec629b7fe102"
    )
    assert result.data[1]["State"] == "exited"
    assert result.data[1]["Status"] == "Exited (137) 18 hours ago"
    assert result.data[1]["Names"] == ["tender_rosalind"]
    assert result.data[1]["ExitCode"] == 137
    assert result.data[1]["Pid"] == 0
    assert result.data[1]["Ports"] == []
    assert result.data[1]["Size"] == {"rootFsSize": 221554338, "rwSize": 0}


def test_podman_ps_json_empty():
    result = PodmanPsAllJson(context_wrap(PODMAN_PS_JSON_EMPTY))
    assert isinstance(result.data, list)
    assert len(result.data) == 0


def test_podman_ps_search_by_name():
    result = PodmanPsAllJson(context_wrap(PODMAN_PS_ALL_JSON))

    # exact match (default)
    exact = result.search_by_name("angry_saha")
    assert len(exact) == 1
    assert exact[0]["Names"] == ["angry_saha"]

    # exact match must not match a substring
    assert result.search_by_name("angry") == []

    # partial match
    partial = result.search_by_name("rosalind", partial=True)
    assert len(partial) == 1
    assert partial[0]["Names"] == ["tender_rosalind"]

    # no match
    assert result.search_by_name("does_not_exist") == []


def test_podman_ps_search_by_name_multiple():
    result = PodmanPsAllJson(context_wrap(PODMAN_PS_MULTI_JSON))

    # partial match returns multiple containers
    matches = result.search_by_name("foreman", partial=True)
    assert len(matches) == 2
    ids = sorted(c["Id"] for c in matches)
    assert ids == ["aaa", "ccc"]

    # exact match returns only the one named "foreman"
    exact = result.search_by_name("foreman")
    assert len(exact) == 1
    assert exact[0]["Id"] == "aaa"


def test_podman_ps_search_by_image():
    result = PodmanPsAllJson(context_wrap(PODMAN_PS_ALL_JSON))

    # exact match (default)
    exact = result.search_by_image("rhel7_httpd")
    assert len(exact) == 1
    assert exact[0]["Names"] == ["angry_saha"]

    # exact match must not match a substring
    assert result.search_by_image("httpd") == []

    # partial match
    partial = result.search_by_image("httpd", partial=True)
    assert len(partial) == 1
    assert partial[0]["Image"] == "rhel7_httpd"

    # no match
    assert result.search_by_image("nonexistent") == []


def test_podman_ps_search_by_image_multiple():
    result = PodmanPsAllJson(context_wrap(PODMAN_PS_MULTI_JSON))

    # exact match returns both containers sharing the same image
    exact = result.search_by_image("quay.io/foreman/foreman:3.16")
    assert len(exact) == 2
    ids = sorted(c["Id"] for c in exact)
    assert ids == ["aaa", "bbb"]

    # partial match on "foreman" returns all three
    partial = result.search_by_image("foreman", partial=True)
    assert len(partial) == 3


def test_podman_ps_search_invalid_argument():
    result = PodmanPsAllJson(context_wrap(PODMAN_PS_ALL_JSON))

    # non-string search terms raise TypeError
    for bad in (None, 123, ["angry_saha"]):
        with pytest.raises(TypeError):
            result.search_by_name(bad)
        with pytest.raises(TypeError):
            result.search_by_image(bad)

    # empty search terms raise ValueError
    with pytest.raises(ValueError):
        result.search_by_name("")
    with pytest.raises(ValueError):
        result.search_by_image("")


ROOTLESS_FLAT = """
[
    {"Id": "a1", "Image": "quay.io/foreman/foreman:3.16", "Names": ["foreman"], "State": "running"},
    {"Id": "a2", "Image": "quay.io/sclorg/postgresql-13-c9s:latest", "Names": ["postgresql"], "State": "running"},
    {"Id": "b1", "Image": "registry.redhat.io/ansible-automation-platform-27/receptor:latest", "Names": ["receptor"], "State": "exited"}
]
""".strip()


def test_podman_ps_all_json_rootless_parse():
    result = PodmanPsAllJsonRootless(context_wrap(ROOTLESS_FLAT))
    # flat data across all rootless users
    assert isinstance(result.data, list)
    assert len(result.data) == 3
    assert sorted(c["Id"] for c in result.data) == ["a1", "a2", "b1"]


def test_podman_ps_all_json_rootless_search():
    result = PodmanPsAllJsonRootless(context_wrap(ROOTLESS_FLAT))
    # inherited search works over the flat data
    foreman = result.search_by_name("foreman")
    assert len(foreman) == 1
    assert foreman[0]["Id"] == "a1"
    aap = result.search_by_image("ansible-automation-platform", partial=True)
    assert len(aap) == 1
    assert aap[0]["Id"] == "b1"


def test_podman_ps_json_documentation():
    failed_count, _ = doctest.testmod(
        podman,
        globs={
            'podman_ps_json': PodmanPsAllJson(context_wrap(PODMAN_PS_ALL_JSON)),
            'podman_ps_rootless': PodmanPsAllJsonRootless(context_wrap(ROOTLESS_FLAT)),
        },
    )
    assert failed_count == 0
