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

JSON_CONTENT_WITH_EXTRA_HEADER_LINES_1 = """
INFO: The fwupdagent command is deprecated, use `fwupdmgr --json` instead
WARNING: UEFI firmware can not be updated in legacy BIOS mode
  See https://github.com/fwupd/fwupd/wiki/PluginFlag:legacy-bios for more information.
{"a": [{"b": "x"}, {"b": "y"}]}
""".strip()
JSON_CONTENT_WITH_EXTRA_HEADER_LINES_2 = """
INFO: The fwupdagent command is deprecated, use `fwupdmgr --json` instead
WARNING: UEFI firmware can not be updated in legacy BIOS mode
  See https://github.com/fwupd/fwupd/wiki/PluginFlag:legacy-bios for more information.
{}
""".strip()
JSON_CONTENT_WITH_EXTRA_HEADER_LINES_3 = """
INFO: Some info line from a command spec output
WARNING: Some warning line-1 from a command spec output
  Some warning line-2 from a command spec output.
""".strip()


def test_json_parser_success():
    for jsonstr in json_test_strings:
        ctx = context_wrap(jsonstr)
        my_json_parser = MyJsonParser(ctx)
        assert my_json_parser.data == json_test_strings[jsonstr]
        assert my_json_parser.unparsed_lines == []


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


def test_json_parser_with_extra_header_lines():
    ctx = context_wrap(JSON_CONTENT_WITH_EXTRA_HEADER_LINES_1)
    my_json_parser = MyJsonParser(ctx)
    assert my_json_parser.data == {'a': [{'b': 'x'}, {'b': 'y'}]}
    assert my_json_parser.unparsed_lines == [
        "INFO: The fwupdagent command is deprecated, use `fwupdmgr --json` instead",
        "WARNING: UEFI firmware can not be updated in legacy BIOS mode",
        "  See https://github.com/fwupd/fwupd/wiki/PluginFlag:legacy-bios for more information."]

    ctx = context_wrap(JSON_CONTENT_WITH_EXTRA_HEADER_LINES_2)
    my_json_parser = MyJsonParser(ctx)
    assert my_json_parser.data == {}
    assert len(my_json_parser.unparsed_lines) == 3

    ctx = context_wrap(JSON_CONTENT_WITH_EXTRA_HEADER_LINES_3)
    with pytest.raises(ParseException) as ex:
        MyJsonParser(ctx)

    assert "couldn't parse json" in ex.value.args[0]
