import doctest

from insights.parsers import containers_inspect
from insights.parsers.containers_inspect import ContainersInspect
from insights.tests import context_wrap


CONTAINERS_INSPECT = """
[{"Id": "aeaea3ead527", "engine": "podman", "Image": "538460c14d75dee1504e56ad8ddb7fe039093b1530ef8f90442a454b9aa3dc8b", "Config|Cmd": ["sleep", "1000000"], "HostConfig|Privileged": false}, {"Id": "28fb57be8bb2", "engine": "podman", "Image": "538460c14d75dee1504e56ad8ddb7fe039093b1530ef8f90442a454b9aa3dc8b", "Config|Cmd": ["sleep", "1000000"], "HostConfig|Privileged": true}, {"Id": "c7efee959ea8", "engine": "docker", "Image": "acf3e09a39c95d354539b6591298be0b0814f5d74e95e722863241192b9a079b", "Config|Cmd": ["sleep", "1000000"], "HostConfig|Privileged": true}]
""".strip()


def test_containers_inspect():
    containers_inspect_result = ContainersInspect(context_wrap(CONTAINERS_INSPECT))
    assert containers_inspect_result.data[0]["Id"] == "aeaea3ead527"
    assert containers_inspect_result.data[0]["HostConfig|Privileged"] is False
    assert containers_inspect_result.data[0]["Config|Cmd"] == ["sleep", "1000000"]


def test_doc_examples():
    env = {
        'inspect_containers': ContainersInspect(context_wrap(CONTAINERS_INSPECT))
    }
    failed, total = doctest.testmod(containers_inspect, globs=env)
    assert failed == 0
