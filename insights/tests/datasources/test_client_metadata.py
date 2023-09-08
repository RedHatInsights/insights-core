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
    ansible_host, blacklisted_specs, branch_info, display_name, egg_release,
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
    # TODO:
    # after #3679
    pass


@patch("insights.specs.datasources.client_metadata.BLACKLISTED_SPECS", [])
def test_blacklisted_specs_empty():
    with pytest.raises(SkipComponent):
        blacklisted_specs({})


@patch("insights.specs.datasources.client_metadata.BLACKLISTED_SPECS", ["date", "auditd_conf"])
def test_blacklisted_specs():
    result = blacklisted_specs({})
    assert result.content == ['{"specs": ["date", "auditd_conf"]}']


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
