import logging
import pytest
import warnings
from insights.tests import run_test
warnings.simplefilter('always', DeprecationWarning)


def pytest_addoption(parser):
    parser.addoption("--runslow", action="store_true", default=False, help="run slow tests")
    parser.addoption("--appdebug", action="store_true", default=False, help="debug logging")
    parser.addoption("--smokey", action="store_true", default=False, help="run tests fast")


def pytest_configure(config):
    level = logging.DEBUG if config.getoption("--appdebug") else logging.ERROR
    logging.basicConfig(level=level)


@pytest.fixture
def run_rule():
    """
    Pytest fixture to allow execution of integration tests without using
    ``archive_provider``.  See arguments to use in inner function below.

    This fixture still runs the complete dependency tree, but if you are
    creating content for the Insights production UI then it will not produce
    test data for the Content Preview app.  As such it should only be used for
    internal support rules that will not be used in the customer facing Insights
    product.
    """
    def _run_rule(rule, input_data):
        """
        Fixture for rule integration testing

        Use this fixture to create an integration test for your rule plugin.

        Sample code::

            def test_myrule(run_rule):
                input_data = InputData('my test name')
                input_data.add(Specs.installed_rpms, RPMS_DATA, path='optional_spec_path')
                expected = make_fail(ERROR_KEY, bad_data=data_expected)
                results = run_rule(my_rule, input_data)
                assert results == expected

        Arguments:
            rule (object): Your rule function object.
            data (InputData):  InputData obj containing all of the necessary data
                for the test.
        """
        result = run_test(rule, input_data)
        # Check result for skip to be compatible with archive_provider decorator
        # Return None instead of result indicating missing component(s)
        if result is not None and 'type' in result and result['type'] == 'skip':
            return None
        else:
            return result

    return _run_rule
