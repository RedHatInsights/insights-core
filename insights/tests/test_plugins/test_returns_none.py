from insights.specs import Specs
from insights.tests import InputData, archive_provider, RHEL7, MAKE_NONE_RESULT
from insights.plugins import returns_none


@archive_provider(returns_none.report_make_none)
def integration_tests_1():
    input_data = InputData("test_return_make_none_1")
    input_data.add(Specs.redhat_release, RHEL7)
    yield input_data, None

    input_data = InputData("test_return_make_none_2")
    input_data.add(Specs.redhat_release, RHEL7)
    yield input_data, MAKE_NONE_RESULT


@archive_provider(returns_none.report_none)
def integration_tests_2():
    input_data = InputData("test_return_none_1")
    input_data.add(Specs.redhat_release, RHEL7)
    yield input_data, None

    input_data = InputData("test_return_none_2")
    input_data.add(Specs.redhat_release, RHEL7)
    yield input_data, MAKE_NONE_RESULT


@archive_provider(returns_none.report_skip_exception)
def integration_tests_3():
    input_data = InputData("test_return_skip_exception_1")
    input_data.add(Specs.redhat_release, RHEL7)
    yield input_data, None

    input_data = InputData("test_return_skip_exception_2")
    input_data.add(Specs.redhat_release, RHEL7)
    yield input_data, None


def test_integration_1(run_rule):
    input_data = InputData("test_return_make_none_1_1")
    input_data.add(Specs.redhat_release, RHEL7)
    result = run_rule(returns_none.report_make_none, input_data)
    assert result is None

    input_data = InputData("test_return_make_none_2_2")
    input_data.add(Specs.redhat_release, RHEL7)
    result = run_rule(returns_none.report_make_none, input_data, return_make_none=True)
    assert result == MAKE_NONE_RESULT


def test_integration_2(run_rule):
    input_data = InputData("test_return_none_2_1")
    input_data.add(Specs.redhat_release, RHEL7)
    result = run_rule(returns_none.report_none, input_data)
    assert result is None

    input_data = InputData("test_return_none_2_2")
    input_data.add(Specs.redhat_release, RHEL7)
    result = run_rule(returns_none.report_none, input_data, return_make_none=True)
    assert result == MAKE_NONE_RESULT


def test_integration_3(run_rule):
    input_data = InputData("test_return_skip_exception_2_1")
    input_data.add(Specs.redhat_release, RHEL7)
    result = run_rule(returns_none.report_skip_exception, input_data)
    assert result is None

    input_data = InputData("test_return_skip_exception_2_2")
    input_data.add(Specs.redhat_release, RHEL7)
    result = run_rule(returns_none.report_skip_exception, input_data, return_make_none=True)
    assert result is None
