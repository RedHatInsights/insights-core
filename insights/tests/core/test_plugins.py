import json
import pytest

from insights.core import plugins
from insights.core.exceptions import ValidationException


def test_validate_good_response():
    assert plugins.make_response("a_test", foo="bar") == {
        "type": "rule",
        "error_key": "a_test",
        "foo": "bar"
    }
    assert plugins.make_fail("a_test", foo="bar") == {
        "type": "rule",
        "error_key": "a_test",
        "foo": "bar"
    }
    assert plugins.make_pass("a_test", foo="bar") == {
        "type": "pass",
        "pass_key": "a_test",
        "foo": "bar"
    }
    assert plugins.make_fingerprint("a_test", foo="bar") == {
        "type": "fingerprint",
        "fingerprint_key": "a_test",
        "foo": "bar"
    }
    assert plugins.make_metadata(foo="bar") == {
        "type": "metadata",
        "foo": "bar"
    }
    assert plugins.make_metadata_key("foo", "bar") == {
        "type": "metadata_key",
        "key": "foo",
        "value": "bar"
    }


def test_disallow_invalid_keys():
    for bad in [[], None, set(), "", 1, lambda x: x]:
        with pytest.raises(ValidationException):
            plugins.make_response(bad)
        with pytest.raises(ValidationException):
            plugins.make_metadata_key(bad, "foo")


def test_disallow_type_key():
    with pytest.raises(ValidationException):
        plugins.make_response("foo", type="dance off")


def test_missing_error_key():
    with pytest.raises(ValidationException):
        plugins.make_response(None, foo="bar")
    with pytest.raises(ValidationException):
        plugins.make_metadata_key(None, "foo")


def test_response_too_big():
    content = "foo" * 50000
    assert plugins.make_response("TESTING", big=content) == {
        "type": "rule",
        "error_key": "TESTING",
        "max_detail_length_error": len(json.dumps({"error_key": "TESTING", "type": "rule", "big": content}))
    }


def test_str_without_type():
    d = plugins.make_response("TESTING", foo="bar")
    del d["type"]
    str(d)
    assert True
