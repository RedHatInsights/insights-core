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
from insights.core import Parser

SIMPLE_DATA = json.dumps({"a": 1, "b": 2, "c": 3})

COMPLEX_DATA = json.dumps({
    "food": "processor",
    "mixing": "bowl",
    "cake": {
        "eggs": 2,
        "flour": 3,
        "sugar": 4,
        "chocolate": 10
    },
    "pie": {
        "peaches": 3,
        "sugar": 2,
        "dough": 1,
        "goo": 3
    }
})

FAKE_DATA = "This is some fake data"


class SimpleParser(Parser):

    def parse_content(self, content):
        self.data = json.loads(content)

    def __getitem__(self, i):
        return self.data[i]

    def ab(self):
        return self.data["a"] + self.data["b"]

    @property
    def bc(self):
        return self.data["b"] + self.data["c"]


class ComplexParser(SimpleParser):

    def cake(self):
        return SubParser(self.data["cake"])

    def pie(self):
        return SubParser(self.data["pie"])


class SubParser(object):

    def sugar(self):
        return self.data["sugar"]


class Context(object):
    def __init__(self, content):
        self.content = content
        self.path = ""
        self.relative_path = ""


def simple_parser(context):
    return SimpleParser(context)


def complex_parser(context):
    return ComplexParser(context)


def fake_parser(context):
    return context.content


for f in [simple_parser, complex_parser, fake_parser]:
    f.serializable_id = "#".join([f.__module__, f.__name__])


@pytest.fixture
def simple():
    return SimpleParser(Context(SIMPLE_DATA))


@pytest.fixture
def complex_():
    return ComplexParser(Context(COMPLEX_DATA))


def test_fn(simple):
    assert simple.ab() == 3


def test_computed(simple):
    assert simple.bc == 5


def test_getitem(complex_):
    assert complex_["food"] == "processor"
    assert complex_["mixing"] == "bowl"
