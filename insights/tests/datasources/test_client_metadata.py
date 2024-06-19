import yaml
import json
import pytest

try:
    from unittest.mock import patch, mock_open
    builtin_open = "builtins.open"
except Exception:
    from mock import patch, mock_open
    builtin_open = "__builtin__.open"

from insights import package_info
from insights.client.config import InsightsConfig
from insights.client.constants import InsightsConstants as constants
from insights.core.exceptions import SkipComponent, ContentException
from insights.specs.datasources.client_metadata import (
    ansible_host, basic_auth_insights_client, blacklist_report,
    blacklisted_specs, branch_info, display_name, egg_release,
    version_info, tags)


TAGS_YAML = """
---
group: _group-name-value_
location: _location-name-value_
description:
 - RHEL:
    - 8
    - 9
 - SAP
key 4: value
""".strip()


def test_ansible_host():
    ic = InsightsConfig(ansible_host='test_abc')
    result = ansible_host({'client_config': ic})
    assert result.content == ['test_abc']

    with pytest.raises(SkipComponent):
        ansible_host({})

    ic = InsightsConfig()
    with pytest.raises(SkipComponent):
        ansible_host({'client_config': ic})


def test_blacklist_report():
    ic = InsightsConfig(obfuscate=True, obfuscate_hostname=False)
    rm = {'patterns': {'regex': ['test', 'pwd', '12.*4', '^abcd']}}
    result = blacklist_report({'client_config': ic, 'redact_config': rm})
    assert json.loads(result.content[0]) == {
            "obfuscate": True, "obfuscate_hostname": False, "commands": 0,
            "files": 0, "components": 0, "patterns": 4, "keywords": 0,
            "using_new_format": True, "using_patterns_regex": True}

    ic = InsightsConfig(obfuscate=True, obfuscate_hostname=True)
    rm = {'patterns': ['test', 'pwd', '', '']}
    result = blacklist_report({'client_config': ic, 'redact_config': rm})
    assert json.loads(result.content[0]) == {
            "obfuscate": True, "obfuscate_hostname": True, "commands": 0,
            "files": 0, "components": 0, "patterns": 2, "keywords": 0,
            "using_new_format": True, "using_patterns_regex": False}

    result = blacklist_report({})
    assert json.loads(result.content[0]) == {
            "obfuscate": False, "obfuscate_hostname": False, "commands": 0,
            "files": 0, "components": 0, "patterns": 0, "keywords": 0,
            "using_new_format": True, "using_patterns_regex": False}


@patch("insights.specs.datasources.client_metadata.BLACKLISTED_SPECS", [])
def test_blacklisted_specs_empty():
    with pytest.raises(SkipComponent):
        blacklisted_specs({})


@patch("insights.specs.datasources.client_metadata.BLACKLISTED_SPECS", ["date", "auditd_conf"])
def test_blacklisted_specs():
    result = blacklisted_specs({})
    assert result.content == ['{"specs": ["date", "auditd_conf"]}']


def test_basic_auth_insights_client():
    ic = InsightsConfig(offline=False, username='test_username', password='test_password')
    result = basic_auth_insights_client({'client_config': ic})
    assert result.content == ['{"username_set": true, "pass_set": true}']
    assert result.path == '/basic_conf'


def test_branch_info():
    ic = InsightsConfig(offline=True)
    result = branch_info({'client_config': ic})
    assert result.content == [json.dumps(constants.default_branch_info)]

    b_info = {'test': 'v1', 'brach': 'v2'}
    ic = InsightsConfig(offline=False, branch_info=b_info)
    result = branch_info({'client_config': ic})
    assert result.content == [json.dumps(b_info)]


def test_display_name():
    ic = InsightsConfig(display_name='test_abc')
    result = display_name({'client_config': ic})
    assert result.content == ['test_abc']

    with pytest.raises(SkipComponent):
        display_name({})

    ic = InsightsConfig()
    with pytest.raises(SkipComponent):
        display_name({'client_config': ic})


@patch(builtin_open, mock_open(read_data='/testing'))
def test_egg_release():
    result = egg_release({})
    assert result.content == ['/testing']


@patch(builtin_open, mock_open(read_data=''))
def test_egg_release_empty():
    with pytest.raises(SkipComponent):
        egg_release({})


@patch("yaml.safe_load", return_value=yaml.load(TAGS_YAML, Loader=yaml.Loader))
@patch("os.path.isfile", return_value=True)
@patch(builtin_open)
def test_tags_ok(m_open, m_isfile, m_load):
    result = tags({})
    result_json = json.loads(''.join(result.content).strip())
    expected_item_1 = {'key': 'group', 'value': '_group-name-value_', 'namespace': 'insights-client'}
    expected_item_2 = {'key': 'description:RHEL', 'value': 8, 'namespace': 'insights-client'}
    expected_item_3 = {'key': 'key 4', 'value': 'value', 'namespace': 'insights-client'}
    assert expected_item_1 in result_json
    assert expected_item_2 in result_json
    assert expected_item_3 in result_json


@patch("os.path.isfile", return_value=True)
@patch(builtin_open, mock_open(read_data='---\ntest\n---'))
def test_invalid_yaml(m_isfile):
    with pytest.raises(ContentException) as ce:
        tags({})
    assert "Cannot parse" in str(ce)


@patch("yaml.safe_load", return_value=None)
@patch("os.path.isfile", return_value=True)
@patch(builtin_open)
def test_empty_yaml(m_open, m_isfile, m_load):
    with pytest.raises(ContentException) as ce:
        tags({})
    assert "Empty YAML" in str(ce)


@patch("os.path.isfile", return_value=False)
def test_tags_no_file(isfile):
    with pytest.raises(SkipComponent) as se:
        tags({})
    assert "No such file" in str(se)


def test_version_info():
    v_info = {}
    v_info['core_version'] = '{0}-{1}'.format(package_info['VERSION'],
                                              package_info['RELEASE'])
    v_info['client_version'] = None

    result = version_info({})
    assert result.content == [json.dumps(v_info)]
