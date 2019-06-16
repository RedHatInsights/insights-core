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

from insights.util.canonical_facts import _filter_falsy


def test_identity():
    assert {"foo": "bar"} == _filter_falsy({"foo": "bar"})


def test_drops_none():
    assert {"foo": "bar"} == _filter_falsy({"foo": "bar", "baz": None})


def test_drops_empty_list():
    assert {"foo": "bar"} == _filter_falsy({"foo": "bar", "baz": []})
