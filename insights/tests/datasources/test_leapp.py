import json
import pytest

try:
    from unittest.mock import patch
    builtin_open = "builtins.open"
except Exception:
    from mock import patch
    builtin_open = "__builtin__.open"

from os import path

from insights.core.exceptions import SkipComponent, ContentException
from insights.specs.datasources.leapp import leapp_report


with open(path.join(path.dirname(__file__), 'leapp-report.json'), 'r') as fp:
    INPUT_OK = json.load(fp)

with open(path.join(path.dirname(__file__), 'leapp-report.ret'), 'r') as fp:
    RESULT = fp.readlines()

INPUT_NG_1 = json.loads("""
{ "entries":[
  {
    "a": "B"
  }
 ]
}
""".strip())

INPUT_NG_2 = json.loads("{}")


@patch("json.load", return_value=INPUT_OK)
@patch("os.path.isfile", return_value=True)
@patch(builtin_open)
def test_leapp_report_ok(m_open, m_isfile, m_load):
    result = leapp_report({})
    result_json = json.loads(''.join(result.content).strip())
    expected_json = json.loads(''.join(RESULT).strip())
    for ret in result_json:
        assert ret in expected_json


@patch("json.load", return_value=INPUT_NG_1)
@patch("os.path.isfile", return_value=True)
@patch(builtin_open)
def test_leapp_report_nothing(m_open, m_isfile, m_load):
    with pytest.raises(SkipComponent) as ce:
        leapp_report({})
    assert "Nothing" in str(ce)


@patch("json.load", return_value=INPUT_NG_2)
@patch("os.path.isfile", return_value=True)
@patch(builtin_open)
def test_leapp_report_ng_2(m_open, m_isfile, m_load):
    with pytest.raises(ContentException) as ce:
        leapp_report({})
    assert "Nothing" in str(ce)


@patch("os.path.isfile", return_value=False)
def test_leapp_report_no_file(isfile):
    with pytest.raises(SkipComponent):
        leapp_report({})
