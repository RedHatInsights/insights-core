import pytest
from insights.core import marshalling


def mar_unmar(o, use_value_list=False):
    marshalled = marshalling.marshal(o, use_value_list)
    unmarshalled = marshalling.unmarshal(marshalled)
    return marshalled, unmarshalled


def test_string_marshal():
    flag = "TEST_FLAG"
    _, unmarshalled = mar_unmar(flag)
    assert unmarshalled == {flag: True}


def test_dict_marshal():
    doc = {"foo": "bar"}
    _, unmarshalled = mar_unmar(doc)
    assert unmarshalled == doc


def test_bad_returns():
    with pytest.raises(TypeError):
        marshalling.marshal(True)
    with pytest.raises(TypeError):
        marshalling.marshal(1)
    with pytest.raises(TypeError):
        marshalling.marshal(1.0)
    with pytest.raises(TypeError):
        marshalling.marshal([])
    with pytest.raises(TypeError):
        marshalling.marshal(())
    with pytest.raises(TypeError):
        marshalling.marshal(set())


def test_none_marshal():
    ma, um = mar_unmar(None)
    assert um is None


def test_value_list():
    ma, um = mar_unmar("test", use_value_list=True)
    assert um == {"test": [True]}
