import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers.podman import PodmanPsAllJson, PodmanPsAllJsonRootless
from insights.combiners.podman_containers import PodmanContainers
from insights.tests import context_wrap

ROOTFUL = """
[
    {"Id": "r1", "Image": "quay.io/foreman/foreman:3.16", "Names": ["foreman"], "State": "running"}
]
""".strip()

ROOTLESS = """
[
    {"Id": "a1", "Image": "img:1", "Names": ["receptor"], "State": "running"},
    {"Id": "b1", "Image": "img:2", "Names": ["gateway"], "State": "exited"}
]
""".strip()


def _rootful(json_str):
    return PodmanPsAllJson(context_wrap(json_str))


def _rootless(json_str):
    return PodmanPsAllJsonRootless(context_wrap(json_str))


def test_podman_containers_both():
    comb = PodmanContainers(_rootful(ROOTFUL), _rootless(ROOTLESS))
    assert sorted(c["Id"] for c in comb.data) == ["a1", "b1", "r1"]
    # search spans both sources
    assert comb.search_by_name("foreman")[0]["Id"] == "r1"
    assert comb.search_by_name("receptor")[0]["Id"] == "a1"


def test_podman_containers_rootful_only():
    comb = PodmanContainers(_rootful(ROOTFUL), None)
    assert [c["Id"] for c in comb.data] == ["r1"]


def test_podman_containers_rootless_only():
    comb = PodmanContainers(None, _rootless(ROOTLESS))
    assert sorted(c["Id"] for c in comb.data) == ["a1", "b1"]


def test_podman_containers_skip_when_none():
    with pytest.raises(SkipComponent):
        PodmanContainers(None, None)
