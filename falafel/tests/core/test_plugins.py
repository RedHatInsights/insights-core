import pytest
from falafel.core import plugins


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


def test_box_empty():
    assert plugins.box({}) == {}


def test_box_flat():
    assert plugins.box({"foo": "bar", "baz": 10}) == {"foo": ["bar"], "baz": 10}


def test_box_nested():
    assert plugins.box({"foo": {"inner": "bar"}, "baz": "stuff"}) == {
        "foo": [{"inner": "bar"}],
        "baz": ["stuff"]
    }


def test_box_key_only():
    assert plugins.box({"foo": None, "bar": {}}) == {
        "foo": [],
        "bar": []
    }


def test_inject_host_strings():
    assert plugins.inject_host("foo", "my_host") == {"foo": "my_host"}


def test_inject_host_mapping():
    assert plugins.inject_host({"error_key": "test"}, "my_host") == {
        "error_key": {
            "host": "my_host",
            "value": "test"
        }
    }


def test_inject_host_too_many_keys():
    with pytest.raises(Exception):
        plugins.inject_host(
            {"key1": True, "key2": False},
            "my_host"
        )
