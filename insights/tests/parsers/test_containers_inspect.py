import doctest

from insights.parsers import containers_inspect
from insights.parsers.containers_inspect import ContainersInspect
from insights.tests import context_wrap


CONTAINERS_INSPECT = """
[{"Id": "aeaea3ead52724bb525bb2b5c619d67836250756920f0cb9884431ba53b476d8", "Image": "538460c14d75dee1504e56ad8ddb7fe039093b1530ef8f90442a454b9aa3dc8b", "ImageName": "registry.access.redhat.com/rhel:latest", "engine": "podman", "Config": {"Annotations": {"io.podman.annotations.privileged": "FALSE"}}}]
""".strip()


def test_containers_inspect():
    containers_inspect_result = ContainersInspect(context_wrap(CONTAINERS_INSPECT))
    assert containers_inspect_result.data[0]["Id"] == "aeaea3ead52724bb525bb2b5c619d67836250756920f0cb9884431ba53b476d8"
    assert containers_inspect_result.data[0]["Config"]["Annotations"]["io.podman.annotations.privileged"] == "FALSE"


def test_doc_examples():
    env = {
        'inspect_containers': ContainersInspect(context_wrap(CONTAINERS_INSPECT))
    }
    failed, total = doctest.testmod(containers_inspect, globs=env)
    assert failed == 0
