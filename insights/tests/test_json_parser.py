import pytest

from insights.core import JSONParser
from insights.core.exceptions import ParseException, SkipComponent
from insights.tests import context_wrap


class MyJsonParser(JSONParser):
    pass


json_test_strings = {
    '{"a": "1", "b": "2"}': {'a': '1', 'b': '2'},
    '[{"a": "1", "b": "2"},{"a": "3", "b": "4"}]':
        [{'a': '1', 'b': '2'}, {'a': '3', 'b': '4'}]
}


def test_json_parser_success():
    for jsonstr in json_test_strings:
        ctx = context_wrap(jsonstr)
        assert MyJsonParser(ctx).data == json_test_strings[jsonstr]


def test_json_parser_failure():
    ctx = context_wrap("boom")
    with pytest.raises(ParseException) as ex:
        MyJsonParser(ctx)

    assert "MyJsonParser" in ex.value.args[0]


def test_json_parser_null_value():
    ctx = context_wrap("null")
    with pytest.raises(SkipComponent) as ex:
        MyJsonParser(ctx)

    assert "Empty input" == ex.value.args[0]
