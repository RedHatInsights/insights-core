from six import StringIO
from insights import dr, make_fail, rule
from insights.formats.text import HumanReadableFormat
from insights.formats._yaml import YamlFormat
from insights.formats._json import JsonFormat
from insights.formats._syslog import SysLogFormat


SL_MSG = "Running insights.tests.test_formats.report"


@rule()
def report():
    return make_fail("ERROR", foo="bar")


def test_human_readable():
    broker = dr.Broker()
    output = StringIO()
    with HumanReadableFormat(broker, stream=output):
        dr.run(report, broker=broker)
    output.seek(0)
    data = output.read()
    assert "foo" in data
    assert "bar" in data


def test_json_format():
    broker = dr.Broker()
    output = StringIO()
    with JsonFormat(broker, stream=output):
        dr.run(report, broker=broker)
    output.seek(0)
    data = output.read()
    assert "foo" in data
    assert "bar" in data


def test_syslog_format():
    broker = dr.Broker()
    output = StringIO()
    with SysLogFormat(broker, stream=output):
        dr.run(report, broker=broker)
    output.seek(0)
    data = output.read()
    assert SL_MSG in data


def test_yaml_format():
    broker = dr.Broker()
    output = StringIO()
    with YamlFormat(broker, stream=output):
        dr.run(report, broker=broker)
    output.seek(0)
    data = output.read()
    assert "foo" in data
    assert "bar" in data
