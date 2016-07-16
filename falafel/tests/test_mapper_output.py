import pytest
from falafel.core import mapper, reducer, MapperOutput, computed

SIMPLE_DATA = {"a": 1, "b": 2, "c": 3}

SIMPLE_JSON = [
    "falafel.tests.test_mapper_output#SimpleMapperOutput",
    SIMPLE_DATA,
    {"bc": 5}
]

COMPLEX_DATA = {
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
}

COMPLEX_JSON = [
    "falafel.tests.test_mapper_output#ComplexMapperOutput",
    COMPLEX_DATA,
    {
        "cake": [
            "falafel.tests.test_mapper_output#SubMapperOutput",
            COMPLEX_DATA["cake"],
            {"sugar": 4}
        ],
        "pie": [
            "falafel.tests.test_mapper_output#SubMapperOutput",
            COMPLEX_DATA["pie"],
            {"sugar": 2}
        ]
    }
]

FAKE_DATA = "This is some fake data"


class SimpleMapperOutput(MapperOutput):

    def ab(self):
        return self.data["a"] + self.data["b"]

    @computed
    def bc(self):
        return self.data["b"] + self.data["c"]


class ComplexMapperOutput(MapperOutput):

    @computed
    def cake(self):
        return SubMapperOutput(self.data["cake"])

    @computed
    def pie(self):
        return SubMapperOutput(self.data["pie"])


class SubMapperOutput(MapperOutput):

    @computed
    def sugar(self):
        return self.data["sugar"]


class Context(object):
    def __init__(self, content):
        self.content = content


def simple_mapper(context):
    return SimpleMapperOutput(context.content)


def complex_mapper(context):
    return ComplexMapperOutput(context.content)


def fake_mapper(context):
    return context.content


for f in [simple_mapper, complex_mapper, fake_mapper]:
    f.serializable_id = "#".join([f.__module__, f.__name__])


@pytest.fixture
def simple():
    return SimpleMapperOutput(SIMPLE_DATA)


@pytest.fixture
def complex_():
    return ComplexMapperOutput(COMPLEX_DATA)


def test_fn(simple):
    assert simple.ab() == 3


def test_computed(simple):
    assert simple.bc == 5


def test_getitem(complex_):
    assert complex_["food"] == "processor"
    assert complex_["mixing"] == "bowl"


def test_name(simple):
    assert simple.get_name() == "falafel.tests.test_mapper_output#SimpleMapperOutput"


def test_serialization_simple(simple):
    assert simple.to_json() == SIMPLE_JSON


def test_to_json_complex(complex_):
    assert complex_.to_json() == COMPLEX_JSON


def test_serialization():
    mapper_output = {
        "some_host": {
            simple_mapper: [
                simple_mapper(Context(SIMPLE_DATA))
            ],
            complex_mapper: [
                complex_mapper(Context(COMPLEX_DATA))
            ],
            fake_mapper: [
                fake_mapper(Context(FAKE_DATA))
            ]
        }
    }

    serialized = mapper.serialize(mapper_output)
    deserialized = reducer.deserialize(serialized)

    assert deserialized == mapper_output
