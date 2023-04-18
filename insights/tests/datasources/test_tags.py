import yaml
import json
import pytest

try:
    from unittest.mock import patch, mock_open
    builtin_open = "builtins.open"
except Exception:
    from mock import patch, mock_open
    builtin_open = "__builtin__.open"

from insights.core.exceptions import SkipComponent, ContentException
from insights.specs.datasources.tags import tags


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
