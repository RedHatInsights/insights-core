import json
from insights.parsr.examples.json_parser import (TRUE, FALSE, NULL, JsonArray,
        JsonObject, JsonValue)

DATA0 = """
{
    "name": "Adventure Lookup"
}
""".strip()


DATA1 = """
{
    "name": "Adventure Lookup",
    "icons": [
        {
            "src": "/android-chrome-192x192.png",
            "sizes": "192x192",
            "type": "image/png"
        },
        {
            "src": "/android-chrome-512x512.png",
            "sizes": "512x512",
            "type": "image/png"
        }
    ],
    "theme_color": "#ffffff",
    "background_color": "#ffffff",
    "display": "standalone"
}
""".strip()

DATA2 = """
{
  "meta": {
    "version": "0.6.0"
  },
  "GROUPS": {
    "c-development": {
      "grp_types": 0,
      "ui_name": "C Development Tools and Libraries",
      "name": "C Development Tools and Libraries",
      "full_list": [
        "valgrind",
        "automake",
        "indent",
        "autoconf",
        "ltrace",
        "bison",
        "ccache",
        "gdb",
        "strace",
        "elfutils",
        "byacc",
        "oprofile",
        "gcc-c++",
        "pkgconfig",
        "binutils",
        "gcc",
        "libtool",
        "cscope",
        "ctags",
        "flex",
        "glibc-devel",
        "make"
      ],
      "pkg_exclude": [],
      "pkg_types": 6
    }
  },
  "ENVIRONMENTS": {}
}""".strip()


def test_true():
    assert TRUE("true") is True


def test_false():
    assert FALSE("false") is False


def test_null():
    assert NULL("null") is None


def test_json_value_number():
    assert JsonValue("123") == 123


def test_json_value_string():
    assert JsonValue('"key"') == "key"


def test_json_empty_array():
    assert JsonArray("[]") == []


def test_json_single_element_array():
    assert JsonArray("['key']") == ["key"]


def test_json_multi_element_array():
    assert JsonArray("[1, 2, 3]") == [1, 2, 3]
    assert JsonArray("['key', -3.4, 'thing']") == ["key", -3.4, "thing"]


def test_json_nested_array():
    assert JsonArray("[1, [4, 5], 3]") == [1, [4, 5], 3]
    assert JsonArray("['key', [-3.4], 'thing']") == ["key", [-3.4], "thing"]


def test_json_empty_object():
    assert JsonObject("{}") == {}


def test_json_single_object():
    assert JsonObject('{"key": "value"}') == {"key": "value"}


def test_json_multi_object():
    expected = {"key1": "value1", "key2": 15}
    assert JsonObject('{"key1": "value1", "key2": 15}') == expected


def test_json_nested_object():
    text = '{ "key1": ["value1", "value2"], "key2": {"num": 15, "num2": 17 }}'
    expected = {"key1": ["value1", "value2"], "key2": {"num": 15, "num2": 17}}
    assert JsonObject(text) == expected


def test_data0():
    expected = json.loads(DATA0)
    assert JsonValue(DATA0) == expected


def test_data1():
    expected = json.loads(DATA1)
    assert JsonValue(DATA1) == expected


def test_data2():
    expected = json.loads(DATA2)
    assert JsonValue(DATA2) == expected
