import doctest
import pytest
from insights import SkipComponent
from insights.parsers import client_metadata
from insights.parsers.client_metadata import (AnsibleHost, BlacklistedSpecs,
                                              BranchInfo, DisplayName,
                                              MachineID, Tags, VersionInfo)
from insights.tests import context_wrap
from insights.tests.parsers import skip_component_check

ANSIBLE_HOST = "host1"

TAGS_JSON_CONTENT = """
[{"key": "group", "value": "_group-name-value_", "namespace": "insights-client"}, {"key": "location", "value": "_location-name-value_", "namespace": "insights-client"}]
""".strip()

BLACKLISTED_SPECS = '{"specs": ["dmesg", "fstab"]}'

BRANCH_INFO = """{"remote_branch": -1, "remote_leaf": -1}"""

MACHINE_ID = """
176843d1-90fa-499b-9f94-111111111111
""".strip()

VER_INFO_1 = """
{"core_version": "3.0.8-dev", "client_version": "3.1.1"}
""".strip()

VER_INFO_2 = """
{"core_version": "3.0.203-1", "client_version": "3.1.1"}
""".strip()


def test_ansible_host():
    ret = AnsibleHost(context_wrap(ANSIBLE_HOST))
    assert ret.hostname == 'host1'


def test_blacklisted_specs():
    bs = BlacklistedSpecs(context_wrap(BLACKLISTED_SPECS))
    assert bs.specs[0] == "dmesg"
    assert bs.specs[1] == "fstab"


def test_blacklisted_spec_skip():
    with pytest.raises(SkipComponent) as ex:
        BlacklistedSpecs(context_wrap(""))
    assert "Empty output." in str(ex)


def test_branch_info():
    ret = BranchInfo(context_wrap(BRANCH_INFO))
    assert ret.data['remote_branch'] == -1
    assert ret.data['remote_leaf'] == -1


def test_display_name():
    ret = DisplayName(context_wrap(ANSIBLE_HOST))  # test with ANSIBLE_HOST
    assert ret.hostname == 'host1'
    assert ret.raw == 'host1'


def test_machine_id():
    ret = MachineID(context_wrap(MACHINE_ID))
    assert ret.id == '176843d1-90fa-499b-9f94-111111111111'

    with pytest.raises(SkipComponent):
        MachineID(context_wrap(""))


def test_tags_json():
    ret = Tags(context_wrap(TAGS_JSON_CONTENT))
    assert ret.data[0]['key'] == "group"
    assert ret.data[0]['value'] == "_group-name-value_"
    assert ret.data[0]['namespace'] == "insights-client"
    assert ret.data[1]['key'] == "location"
    assert ret.data[1]['value'] == "_location-name-value_"
    assert ret.data[1]['namespace'] == "insights-client"


def test_tags_json_bytes():
    ret = Tags(context_wrap(bytes(str(TAGS_JSON_CONTENT).encode("utf-8"))))
    assert ret.data[0]['key'] == "group"
    assert ret.data[0]['value'] == "_group-name-value_"
    assert ret.data[0]['namespace'] == "insights-client"
    assert ret.data[1]['key'] == "location"
    assert ret.data[1]['value'] == "_location-name-value_"
    assert ret.data[1]['namespace'] == "insights-client"


def test_tags_empty():
    assert 'Empty output.' in skip_component_check(Tags)


def test_version_info():
    ret = VersionInfo(context_wrap(VER_INFO_1))
    assert ret.core_version == '3.0.8-dev'
    assert ret.client_version == '3.1.1'

    ret = VersionInfo(context_wrap(VER_INFO_2))
    assert ret.core_version == '3.0.203-1'
    assert ret.client_version == '3.1.1'


def test_version_info_empty():
    assert 'Empty output.' in skip_component_check(VersionInfo)


def test_doc_examples():
    env = {
        "ansible_host": AnsibleHost(context_wrap(ANSIBLE_HOST)),
        "specs": BlacklistedSpecs(context_wrap(BLACKLISTED_SPECS)),
        "branch_info": BranchInfo(context_wrap(BRANCH_INFO)),
        "display_name": DisplayName(context_wrap(ANSIBLE_HOST)),  # test with ANSIBLE_HOST
        "machine_id": MachineID(context_wrap(MACHINE_ID)),
        "tags": Tags(context_wrap(TAGS_JSON_CONTENT)),
        'ver': VersionInfo(context_wrap(VER_INFO_2)),
    }
    failed, total = doctest.testmod(client_metadata, globs=env)
    assert failed == 0
