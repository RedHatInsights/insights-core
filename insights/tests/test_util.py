import pytest
from insights.tests import unordered_compare
from insights.core.dr import split_requirements, stringify_requirements, get_missing_requirements
from insights.core import context


class t(object):

    def __init__(self, n):
        self.serializable_id = self.n = n

    def __eq__(self, item):
        return hasattr(item, "n") and item.n == self.n

    def __lt__(self, item):
        return self.n < item.n

    def __hash__(self):
        return self.n.__hash__()

    def __repr__(self):
        return self.n


def dummy_dict(l):
    return dict((k, 1) for k in l)


REQUIRES = [t("a"), t("b"), [t("d"), t("e")], t("c"), [t("f"), t("g")]]


def test_split():
    expected = ([t("a"), t("b"), t("c")], [[t("d"), t("e")], [t("f"), t("g")]])
    result = split_requirements(REQUIRES)
    assert expected == result


def test_stringify():
    expected = "All: ['a', 'b', 'c'] Any: ['d', 'e'] Any: ['f', 'g']"
    result = stringify_requirements(REQUIRES)
    assert expected == result


def test_missing():
    missing_none = dummy_dict([t("a"), t("b"), t("c"), t("d"), t("e"), t("f"), t("g")])
    assert get_missing_requirements(REQUIRES, missing_none) is None
    missing_partial_any = dummy_dict([t("a"), t("b"), t("c"), t("d"), t("g")])
    assert get_missing_requirements(REQUIRES, missing_partial_any) is None
    missing_any = dummy_dict([t("a"), t("b"), t("c"), t("f"), t("g")])
    result = get_missing_requirements(REQUIRES, missing_any)
    assert result == ([], [[t("d"), t("e")]])
    missing_all = dummy_dict([t("a"), t("c"), t("d"), t("e"), t("f"), t("g")])
    result = get_missing_requirements(REQUIRES, missing_all)
    assert result == ([t("b")], [])


@pytest.fixture
def ctx():
    return context.Context()


def test_sane_defaults(ctx):
    assert ctx.hostname is None
    assert ctx.version == ["-1", "-1"]


def test_product_available(ctx):
    ctx.osp.role = "Controller"
    assert ctx.osp
    assert ctx.osp.role == "Controller"


def test_product_not_available(ctx):
    assert not ctx.osp
    assert ctx.osp.role is None


def test_non_product_member(ctx):
    with pytest.raises(AttributeError):
        ctx.invalid_product()


def test_str():
    unordered_compare("foo", "foo")
    unordered_compare(u"foo", "foo")
    with pytest.raises(AssertionError):
        unordered_compare("foo", "bar")


def test_num():
    unordered_compare(1, 1)
    unordered_compare(1.1, 1.1)
    with pytest.raises(AssertionError):
        unordered_compare(1, 2)


def test_list():
    unordered_compare([1, 2, 3], [1, 2, 3])
    unordered_compare([2, 3, 4], [4, 3, 2])
    with pytest.raises(AssertionError):
        unordered_compare([1, 2, 3], [2, 3, 4])


def test_dict():
    unordered_compare({"foo": 1}, {"foo": 1})
    unordered_compare({"foo": 1, "bar": 2}, {"bar": 2, "foo": 1})
    with pytest.raises(AssertionError):
        unordered_compare({"foo": 1}, {"foo": 2})

    with pytest.raises(AssertionError):
        unordered_compare({"foo": 1, "bar": [1, 2, 3]}, {"foo": 1, "bar": [0, 1, 2]})


def test_deep_nest():
    a = {"error_key": "test1", "stuff": {"abba": [{"foo": 2}]}}
    b = {"error_key": "test1", "stuff": {"abba": [{"foo": 2}]}}

    unordered_compare(a, b)

    with pytest.raises(AssertionError):
        b["stuff"]["abba"][0]["foo"] = "cake"
        unordered_compare(a, b)
