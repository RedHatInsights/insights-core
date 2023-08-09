import json
import os

from tempfile import mkdtemp

from insights.core import dr
from insights.core.exceptions import ContentException
from insights.core.plugins import component, datasource, make_info, rule
from insights.core.serde import Hydration, deserializer, marshal, serializer, unmarshal
from insights.core.spec_factory import RegistryPoint, SpecSet
from insights.util import fs


class Foo(object):
    def __init__(self):
        self.a = 1
        self.b = 2


class Doo(object):
    def __init__(self, c):
        if c > 5:
            self.a = 1
            self.b = 2
        else:
            self.a = c
            self.b = 2


@component()
def thing():
    return Foo()


@serializer(Foo)
def serialize_foo(obj, root=None):
    return {"a": obj.a, "b": obj.b}


@serializer(Doo)
def serialize_doo(obj, root=None):
    if obj.a > 1:
        raise Exception('errors' + str(obj.a))
    return {"a": obj.a, "b": obj.b}


@deserializer(Foo)
def deserialize_foo(_type, data, root=None):
    foo = _type.__new__(_type)
    foo.a = data.get("a")
    foo.b = data.get("b")
    return foo


class Specs(SpecSet):
    the_data = RegistryPoint()


class TestSpecs(Specs):
    @datasource()
    def the_data(broker):
        raise ContentException('Fake Datasource')


@rule(Specs.the_data)
def report(dt):
    return make_info('INFO_1')


def test_marshal():
    broker = dr.Broker()
    foo = Foo()
    broker[thing] = foo
    data, errors = marshal(thing, broker)
    assert data
    assert not errors
    d = data["object"]
    assert d["a"] == 1
    assert d["b"] == 2


def test_marshal_with_errors():
    broker = dr.Broker()
    doo = Doo(2)
    broker[thing] = doo
    data, errors = marshal(thing, broker)
    assert not data
    assert isinstance(errors, str)

    # one raises error, one has result
    broker = dr.Broker()
    objs = [Doo(4), Doo(6)]
    broker[thing] = objs
    data, errors = marshal(thing, broker)
    assert data
    assert errors
    assert len(data) == 1
    assert len(errors) == 1
    d = data[0]["object"]
    assert d["a"] == 1
    assert d["b"] == 2

    # all raises error, no results
    broker = dr.Broker()
    objs = [Doo(4), Doo(3)]
    broker[thing] = objs
    data, errors = marshal(thing, broker)
    assert not data
    assert errors
    assert len(errors) == 2

    # all have resutls, no errors
    broker = dr.Broker()
    objs = [Doo(8), Doo(6)]
    broker[thing] = objs
    data, errors = marshal(thing, broker)
    assert data
    assert not errors
    assert len(data) == 2
    for item in data:
        d = item["object"]
        assert d["a"] == 1
        assert d["b"] == 2


def test_marshal_with_errors_with_pool():
    try:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(thread_name_prefix="insights-collector-pool", max_workers=5) as pool:
            # one raises error, one has result
            broker = dr.Broker()
            objs = [Doo(4), Doo(6)]
            broker[thing] = objs
            data, errors = marshal(thing, broker, pool=pool)
            assert data
            assert errors
            assert len(data) == 1
            assert len(errors) == 1
            d = data[0]["object"]
            assert d["a"] == 1
            assert d["b"] == 2

            # all raises error, no results
            broker = dr.Broker()
            objs = [Doo(4), Doo(3)]
            broker[thing] = objs
            data, errors = marshal(thing, broker, pool=pool)
            assert not data
            assert errors
            assert len(errors) == 2

            # all have resutls, no errors
            broker = dr.Broker()
            objs = [Doo(8), Doo(6)]
            broker[thing] = objs
            data, errors = marshal(thing, broker, pool=pool)
            assert data
            assert not errors
            assert len(data) == 2
            for item in data:
                d = item["object"]
                assert d["a"] == 1
                assert d["b"] == 2
    except ImportError:
        pass


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


def test_dehydrate():
    broker = dr.run(report)
    exc = next(iter(broker.tracebacks))
    tb = broker.tracebacks[exc]

    tmp_path = mkdtemp()
    spec_the_data = Specs.the_data
    try:
        h = Hydration(tmp_path)
        h.dehydrate(spec_the_data, broker)
        fn = ".".join([dr.get_name(spec_the_data), h.ser_name])
        meta_data_json = os.path.join(h.meta_data, fn)
        assert os.path.exists(meta_data_json)
        with open(meta_data_json, 'r') as fp:
            ret = json.load(fp)
            assert "errors" in ret
            assert ret["errors"][0] == tb
            assert "Traceback" in tb
            assert "Fake Datasource" in tb
    finally:
        fs.remove(tmp_path)
