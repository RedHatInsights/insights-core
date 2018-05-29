import json
import pytest
from insights.core import plugins


def test_make_metadata():
    assert plugins.make_metadata(foo="bar") == {
        "type": "metadata",
        "foo": "bar"
    }


def test_make_metadata_should_not_allow_type():
    with pytest.raises(Exception):
        plugins.make_metadata(type="not_allowed", foo="bar")


def test_validate_response_good():
    assert plugins.validate_response({
        "type": "rule",
        "error_key": "a_test",
        "foo": "bar"}) is None


def test_validate_response_invalid_types():
    for bad in [[], None, set(), "", 1, lambda x: x]:
        with pytest.raises(plugins.ValidationException):
            plugins.validate_response(bad)


def test_validate_response_missing_type():
    with pytest.raises(plugins.ValidationException):
        plugins.validate_response({"error_key": "an_error"})


def test_validate_response_invalid_type_key():
    with pytest.raises(plugins.ValidationException):
        plugins.validate_response({"type": "dance off"})


def test_validate_response_missing_error_key():
    with pytest.raises(plugins.ValidationException):
        plugins.validate_response({"type": "rule", "foo": "bar"})


def test_validate_response_invalid_error_key_type():
    for bad in [{}, None, 1, lambda x: x, set()]:
        with pytest.raises(plugins.ValidationException):
            plugins.validate_response({
                "type": "rule",
                "error_key": bad
            })


def test_make_response_too_big():
    content = "foo" * 50000
    assert plugins.make_response("TESTING", big=content) == {
        "type": "rule",
        "error_key": "TESTING",
        "max_detail_length_error": len(json.dumps({"error_key": "TESTING", "type": "rule", "big": content}))
    }


def test_validate_fingerprint_good():
    assert plugins.validate_response({
        "type": "fingerprint",
        "fingerprint_key": "FINGERPRINT",
        "foo": "bar"}) is None


def test_validate_response_missing_fingerprint_key():
    with pytest.raises(plugins.ValidationException):
        plugins.validate_response({"type": "fingerprint", "foo": "bar"})
