import pytest
from insights.parsr import Char, Many


def test_many():
    a = Char("a")
    b = Char("b")
    x = Char("x")

    xs = Many(x)
    assert xs("") == []
    assert xs("a") == []
    assert xs("x") == ["x"]
    assert xs("xxxxx") == ["x", "x", "x", "x", "x"]
    assert xs("xxxxb") == ["x", "x", "x", "x"]

    ab = Many(a + b)
    assert ab("") == []
    assert ab("ba") == []
    assert ab("ab") == [["a", "b"]]
    assert ab("ababab") == [["a", "b"], ["a", "b"], ["a", "b"]]

    ab = Many(a | b)
    assert ab("aababb") == ["a", "a", "b", "a", "b", "b"]


def test_many1():
    a = Char("a")
    b = Char("b")
    x = Char("x")

    xs = Many(x, lower=1)
    with pytest.raises(Exception):
        xs("")

    with pytest.raises(Exception):
        xs("a")

    assert xs("x") == ["x"]
    assert xs("xxxxx") == ["x", "x", "x", "x", "x"]
    assert xs("xxxxb") == ["x", "x", "x", "x"]

    ab = Many(a + b, lower=1)
    with pytest.raises(Exception):
        ab("")

    with pytest.raises(Exception):
        ab("ba")

    assert ab("ab") == [["a", "b"]]
    assert ab("ababab") == [["a", "b"], ["a", "b"], ["a", "b"]]

    ab = Many(a | b, lower=1)
    assert ab("aababb") == ["a", "a", "b", "a", "b", "b"]
