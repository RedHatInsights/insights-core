#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import json
import pytest
from insights.core import plugins


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
        with pytest.raises(plugins.ValidationException):
            plugins.make_response(bad)
        with pytest.raises(plugins.ValidationException):
            plugins.make_metadata_key(bad, "foo")


def test_disallow_type_key():
    with pytest.raises(plugins.ValidationException):
        plugins.make_response("foo", type="dance off")


def test_missing_error_key():
    with pytest.raises(plugins.ValidationException):
        plugins.make_response(None, foo="bar")
    with pytest.raises(plugins.ValidationException):
        plugins.make_metadata_key(None, "foo")


def test_response_too_big():
    content = "foo" * 50000
    assert plugins.make_response("TESTING", big=content) == {
        "type": "rule",
        "error_key": "TESTING",
        "max_detail_length_error": len(json.dumps({"error_key": "TESTING", "type": "rule", "big": content}))
    }
