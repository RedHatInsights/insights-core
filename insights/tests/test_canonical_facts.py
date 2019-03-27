from insights.util.canonical_facts import _filter_falsy


def test_identity():
    assert {"foo": "bar"} == _filter_falsy({"foo": "bar"})


def test_drops_none():
    assert {"foo": "bar"} == _filter_falsy({"foo": "bar", "baz": None})


def test_drops_empty_list():
    assert {"foo": "bar"} == _filter_falsy({"foo": "bar", "baz": []})
