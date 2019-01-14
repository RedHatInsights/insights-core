import os

from tempfile import mkdtemp
from insights import dr
from insights.core.plugins import component
from insights.core.serde import (serializer,
                                 deserializer,
                                 Hydration,
                                 marshal,
                                 unmarshal)
from insights.util import fs


class Foo(object):
    def __init__(self):
        self.a = 1
        self.b = 2


@component()
def thing():
    return Foo()


@serializer(Foo)
def serialize_foo(obj, root=None):
    return {"a": obj.a, "b": obj.b}


@deserializer(Foo)
def deserialize_foo(_type, data, root=None):
    foo = _type.__new__(_type)
    foo.a = data.get("a")
    foo.b = data.get("b")
    return foo


def test_marshal():
    foo = Foo()
    data = marshal(foo)
    assert data is not None
    d = data["object"]
    assert d["a"] == 1
    assert d["b"] == 2


def test_unmarshal():
    d = {
        "type": "insights.tests.test_serde.Foo",
        "object": {"a": 1, "b": 2}
    }
    foo = unmarshal(d)
    assert foo is not None
    assert foo.a == 1
    assert foo.b == 2


def test_hydrate_one():
    raw = {
        "name": dr.get_name(thing),
        "exec_time": 0.25,
        "ser_time": 0.05,
        "results": {
            "type": "insights.tests.test_serde.Foo",
            "object": {"a": 1, "b": 2}
        }
    }

    h = Hydration()
    key, result, exec_time, ser_time = h._hydrate_one(raw)
    assert key is thing
    assert isinstance(result, Foo)
    assert exec_time == 0.25
    assert ser_time == 0.05


def test_hydrate_one_multiple_results():
    raw = {
        "name": dr.get_name(thing),
        "exec_time": 0.5,
        "ser_time": 0.1,
        "results": [
            {
                "type": "insights.tests.test_serde.Foo",
                "object": {"a": 1, "b": 2}
            },
            {
                "type": "insights.tests.test_serde.Foo",
                "object": {"a": 3, "b": 4}
            },
        ]
    }

    h = Hydration()
    key, result, exec_time, ser_time = h._hydrate_one(raw)
    assert key is thing
    assert len(result) == 2
    assert exec_time == 0.5
    assert ser_time == 0.1
    assert result[0].a == 1
    assert result[0].b == 2
    assert result[1].a == 3
    assert result[1].b == 4


def test_round_trip():
    tmp_path = mkdtemp()
    try:
        h = Hydration(tmp_path)

        broker = dr.Broker()
        broker[thing] = Foo()
        broker.exec_times[thing] = 0.5
        h.dehydrate(thing, broker)
        fn = ".".join([dr.get_name(thing), h.ser_name])
        assert os.path.exists(os.path.join(h.meta_data, fn))

        broker = h.hydrate()
        assert thing in broker
        assert broker.exec_times[thing] >= 0.5
        foo = broker[thing]
        assert foo.a == 1
        assert foo.b == 2
    finally:
        pass
        if os.path.exists(tmp_path):
            fs.remove(tmp_path)
