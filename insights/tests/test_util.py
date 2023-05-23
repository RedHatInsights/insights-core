import pytest
import warnings
from insights.tests import deep_compare
from insights.core.dr import split_requirements, stringify_requirements, get_missing_requirements
from insights.core import context
from insights.util import case_variants, deprecated


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
    assert get_missing_requirements(None, REQUIRES, missing_none) is None
    missing_partial_any = dummy_dict([t("a"), t("b"), t("c"), t("d"), t("g")])
    assert get_missing_requirements(None, REQUIRES, missing_partial_any) is None
    missing_any = dummy_dict([t("a"), t("b"), t("c"), t("f"), t("g")])
    result = get_missing_requirements(None, REQUIRES, missing_any)
    assert result == ([], [[t("d"), t("e")]])
    missing_all = dummy_dict([t("a"), t("c"), t("d"), t("e"), t("f"), t("g")])
    result = get_missing_requirements(None, REQUIRES, missing_all)
    assert result == ([t("b")], [])


@pytest.fixture
def ctx():
    return context.Context()


def test_sane_defaults(ctx):
    assert ctx.hostname is None
    assert ctx.version == ["-1", "-1"]


def test_non_product_member(ctx):
    with pytest.raises(AttributeError):
        ctx.invalid_product()


def test_str():
    deep_compare("foo", "foo")
    deep_compare(u"foo", u"foo")
    with pytest.raises(AssertionError):
        deep_compare("foo", "bar")


def test_num():
    deep_compare(1, 1)
    deep_compare(1.1, 1.1)
    with pytest.raises(AssertionError):
        deep_compare(1, 2)


def test_list():
    deep_compare([1, 2, 3], [1, 2, 3])
    with pytest.raises(AssertionError):
        deep_compare([2, 3, 4], [4, 3, 2])
        deep_compare([1, 2, 3], [2, 3, 4])


def test_dict():
    deep_compare({"foo": 1}, {"foo": 1})
    deep_compare({"foo": 1, "bar": 2}, {"bar": 2, "foo": 1})
    with pytest.raises(AssertionError):
        deep_compare({"foo": 1}, {"foo": 2})

    with pytest.raises(AssertionError):
        deep_compare({"foo": 1, "bar": [1, 2, 3]}, {"foo": 1, "bar": [0, 1, 2]})


def test_deep_nest():
    a = {"error_key": "test1", "stuff": {"abba": [{"foo": 2}]}}
    b = {"error_key": "test1", "stuff": {"abba": [{"foo": 2}]}}

    deep_compare(a, b)

    with pytest.raises(AssertionError):
        b["stuff"]["abba"][0]["foo"] = "cake"
        deep_compare(a, b)


def test_deep_nest_tuple_dict():
    a = ({2: 22}, {3: 33}, {4: 44})
    b = ({2: 22}, {3: 33}, {4: 44})
    deep_compare(a, b)
    with pytest.raises(AssertionError):
        b = ({2: 22}, {3: 30}, {4: 44})
        deep_compare(a, b)

    a = ({2: 22}, {3: [33, 333]}, {4: 44})
    b = ({2: 22}, {3: [33, 333]}, {4: 44})
    deep_compare(a, b)
    with pytest.raises(AssertionError):
        b = ({2: 22}, {3: [333, 33]}, {4: 44})
        deep_compare(a, b)

    a = ({2: 22, 5: '55'}, [33, 333, '3'], {6: [6], 4: 44})
    b = ({5: '55', 2: 22}, [33, 333, '3'], {4: 44, 6: [6]})
    deep_compare(a, b)
    with pytest.raises(AssertionError):
        b = ({5: '55', 2: 22}, [33, 333, 3], {4: 44, 6: [6]})
        deep_compare(a, b)


def test_deep_nest_list_dict():
    a = [{2: 22}, {3: 33}, {4: 44}]
    b = [{2: 22}, {3: 33}, {4: 44}]
    deep_compare(a, b)
    with pytest.raises(AssertionError):
        b[1][3] = 30
        deep_compare(a, b)

    a = [{2: 22}, {3: [33, 333]}, {4: 44}]
    b = [{2: 22}, {3: [33, 333]}, {4: 44}]
    deep_compare(a, b)
    with pytest.raises(AssertionError):
        b[1][3] = [333, 33]
        deep_compare(a, b)

    a = [{2: 22, 5: '55'}, [33, 333, '3'], {6: [6], 4: 44}]
    b = [{5: '55', 2: 22}, [33, 333, '3'], {4: 44, 6: [6]}]
    deep_compare(a, b)
    with pytest.raises(AssertionError):
        b[1][2] = 3
        deep_compare(a, b)

    a = [
           {'ip_addr': '0.0.0.0', 'process_name': 'qpidd', 'port': '5672'},
           {'ip_addr': '127.0.0.1', 'process_name': 'mongod', 'port': '27017'},
           {'ip_addr': '127.0.0.1', 'process_name': 'Passenger Rac', 'port': '53644'},
           {'ip_addr': '0.0.0.0', 'process_name': 'qdrouterd', 'port': '5646'},
    ]
    b = [
           {'ip_addr': '0.0.0.0', 'port': '5672', 'process_name': 'qpidd'},
           {'ip_addr': '127.0.0.1', 'port': '27017', 'process_name': 'mongod'},
           {'ip_addr': '127.0.0.1', 'port': '53644', 'process_name': 'Passenger Rac'},
           {'ip_addr': '0.0.0.0', 'port': '5646', 'process_name': 'qdrouterd'},
    ]
    deep_compare(a, b)


def test_deep_nest_dict_list():
    a = {'2': [22, 222], 3: [33, 333]}
    b = {3: [33, 333], '2': [22, 222]}
    deep_compare(a, b)
    with pytest.raises(AssertionError):
        b['2'] = [222, 22]
        deep_compare(a, b)

    a = {3: [33, [3, '33', 333]], 2: (22, 222)}
    b = {2: (22, 222), 3: [33, [3, '33', 333]]}
    with pytest.raises(AssertionError):
        b[3] = [33, ['33', 333, 3]]
        deep_compare(a, b)

    a = {3: [33, [set([4, 3]), '33', 333]], 2: (22, 222)}
    b = {2: (22, 222), 3: [33, [set([4, 3]), '33', 333]]}
    with pytest.raises(AssertionError):
        b[3][1] = set([3, 4])
        deep_compare(a, b)


def test_deep_compare_special():
    """
    Test the special format of the `expected`
    """
    a = {'type': 'skip', 'reason': 'MISSING_REQUIREMENTS', 'details': 'test1'}
    b1 = (None, 'test1')
    b2 = [None, ['test1']]
    deep_compare(a, b1)
    deep_compare(a, b2)

    with pytest.raises(AssertionError):
        a = {'type': 'skip', 'reason': 'NO_MISSING', 'details': 'test1'}
        deep_compare(a, b1)

    with pytest.raises(AssertionError):
        a = {'type': 'skip', 'reason': 'MISSING_REQUIREMENTS', 'details': 'test0'}
        deep_compare(a, b1)


def test_case_variants():
    filter_list = ['Ciphers', 'MACs', 'UsePAM', 'MaxAuthTries', 'nt pipe support',
                   'A-Dash-SEPARATED-tESt-tEST-tesT-test-ExAMPle']
    expanded_list = ['Ciphers', 'ciphers', 'CIPHERS',
                     'MACs', 'Macs', 'macs', 'MACS',
                     'UsePAM', 'UsePam', 'usepam', 'USEPAM', 'Usepam',
                     'MaxAuthTries', 'maxauthtries', 'MAXAUTHTRIES', 'Maxauthtries',
                     'nt pipe support', 'NT PIPE SUPPORT', 'Nt Pipe Support',
                     'A-Dash-SEPARATED-tESt-tEST-tesT-test-ExAMPle',
                     'A-Dash-Separated-tEst-tEst-tesT-test-ExAmple',
                     'a-dash-separated-test-test-test-test-example',
                     'A-DASH-SEPARATED-TEST-TEST-TEST-TEST-EXAMPLE',
                     'A-Dash-Separated-Test-Test-Test-Test-Example']
    assert case_variants(*filter_list) == expanded_list

    assert case_variants('hosts:') == ['hosts:', 'HOSTS:', 'Hosts:']


def test_deprecated():
    def normal_fn():
        return 1

    def deprecated_fn():
        deprecated(deprecated_fn, "really don't use this")
        return 3

    assert normal_fn() == 1

    # For all remaining tests, cause the warnings to always be caught
    warnings.simplefilter('always')

    with warnings.catch_warnings(record=True) as w:
        assert deprecated_fn() == 3

        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "really don't use this" in str(w[0].message)
