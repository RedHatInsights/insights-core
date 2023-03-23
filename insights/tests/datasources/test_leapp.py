import json
import pytest

from mock.mock import Mock
from os import path

from insights.core.exceptions import SkipComponent
from insights.specs.datasources.leapp import leapp_report, LocalSpecs


with open(path.join(path.dirname(__file__), 'leapp-report.json'), 'r') as fp:
    INPUT_OK = fp.readlines()

with open(path.join(path.dirname(__file__), 'leapp-report.ret'), 'r') as fp:
    RESULT = fp.readlines()

INPUT_NG_1 = """
{ "entries":[
  {
    "a": "B",
  }
 ]
}
""".strip()

INPUT_NG_2 = ""


def test_leapp_report():
    report_file = Mock()
    report_file.content = INPUT_OK
    broker = {LocalSpecs.leapp_report_raw: report_file}

    result = leapp_report(broker)

    result_json = json.loads(''.join(result.content).strip())
    expected_json = json.loads(''.join(RESULT).strip())
    for ret in result_json:
        assert ret in expected_json

    report_file = Mock()
    report_file.content = INPUT_NG_1
    broker = {LocalSpecs.leapp_report_raw: report_file}
    with pytest.raises(SkipComponent):
        leapp_report(broker)

    report_file = Mock()
    report_file.content = INPUT_NG_2
    broker = {LocalSpecs.leapp_report_raw: report_file}
    with pytest.raises(SkipComponent):
        leapp_report(broker)
