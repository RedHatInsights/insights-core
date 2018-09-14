from six import StringIO
from insights import dr, make_response, rule
from insights.formats.text import HumanReadableFormat
from insights.formats._json import JsonFormat


@rule()
def report():
    return make_response("ERROR", foo="bar")


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
