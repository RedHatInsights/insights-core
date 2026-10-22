import doctest
import types

import pytest

from insights.tests.doctest_support import (
    DOCTEST_ALLOW_TYPE_CLASS,
    INSIGHTS_DOCTEST_OPTIONFLAGS,
    InsightsDoctestChecker,
    InsightsDocTestRunner,
)


@pytest.fixture
def insights_checker():
    return InsightsDoctestChecker()


TYPE_CLASS_TEST_CASES = [
    ("<class 'list'>\n", "<class 'list'>\n", True, INSIGHTS_DOCTEST_OPTIONFLAGS),
    ("<class 'list'>\n", "<type 'list'>\n", True, DOCTEST_ALLOW_TYPE_CLASS),
    ("<type 'list'>\n", "<class 'list'>\n", True, INSIGHTS_DOCTEST_OPTIONFLAGS),
    ("<class 'dict'>\n", "<type 'list'>\n", False, INSIGHTS_DOCTEST_OPTIONFLAGS),
    ("<class 'list'>\n", "<type 'list'>\n", False, 0),
]


@pytest.mark.parametrize(
    "want,got,expected_result,insights_optionflags",
    TYPE_CLASS_TEST_CASES,
    ids=[
        "identical_class_repr",
        "class_want_type_got",
        "type_want_class_got",
        "mismatched_type_names",
        "insights_checker_without_flag",
    ],
)
def test_type_class_repr_comparison(
    insights_checker,
    want,
    got,
    expected_result,
    insights_optionflags,
):
    assert insights_checker.check_output(
        want, got, insights_optionflags
    ) == expected_result


def test_doctest_testmod_uses_insights_runner():
    assert doctest.DocTestRunner is InsightsDocTestRunner

    module = types.ModuleType('insights_doctest_support_example')
    module.__doc__ = """
    >>> type([])
    <class 'list'>
    >>> type([])
    <type 'list'>
    """
    failed, total = doctest.testmod(module)
    assert total == 2
    assert failed == 0
