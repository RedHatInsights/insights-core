import json
import pytest
from falafel.core import Mapper

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


class SimpleMapper(Mapper):

    def parse_content(self, content):
        self.data = json.loads(content)

    def __getitem__(self, i):
        return self.data[i]

    def ab(self):
        return self.data["a"] + self.data["b"]

    @property
    def bc(self):
        return self.data["b"] + self.data["c"]


class ComplexMapper(SimpleMapper):

    def cake(self):
        return SubMapper(self.data["cake"])

    def pie(self):
        return SubMapper(self.data["pie"])


class SubMapper(object):

    def sugar(self):
        return self.data["sugar"]


class Context(object):
    def __init__(self, content):
        self.content = content
        self.path = ""


def simple_mapper(context):
    return SimpleMapper(context)


def complex_mapper(context):
    return ComplexMapper(context)


def fake_mapper(context):
    return context.content


for f in [simple_mapper, complex_mapper, fake_mapper]:
    f.serializable_id = "#".join([f.__module__, f.__name__])


@pytest.fixture
def simple():
    return SimpleMapper(Context(SIMPLE_DATA))


@pytest.fixture
def complex_():
    return ComplexMapper(Context(COMPLEX_DATA))


def test_fn(simple):
    assert simple.ab() == 3


def test_computed(simple):
    assert simple.bc == 5


def test_getitem(complex_):
    assert complex_["food"] == "processor"
    assert complex_["mixing"] == "bowl"
