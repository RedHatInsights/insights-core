import pytest

from insights.core import JSONParser, ParseException
from insights.tests import context_wrap


class MyJsonParser(JSONParser):
    pass


def test_json_parser_success():
    ctx = context_wrap('{"a": "2"}')
    assert MyJsonParser(ctx)


def test_json_parser_failure():
    ctx = context_wrap("boom")
    with pytest.raises(ParseException) as ex:
        MyJsonParser(ctx)

    assert "MyJsonParser" in ex.value.args[0]
