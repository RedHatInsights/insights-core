import logging
import pytest
import warnings
from insights.tests import InputData, run_test
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
    Pytest fixture to allows execution of integration tests without using
    ``archive_provider``.  See arguments to use in inner function below.

    This fixture still runs the same dependency tree as when testing with
    ``archive_provider``.
    """
    def _run_rule(name, rule, input_data):
        """
        Fixture for rule integration testing

        Use this fixture to create an integration test for your rule plugin.

        Sample code::

            def test_myrule(run_rule):
                input_data = {'spec': Specs.installed_rpms, 'data': RPMS_DATA}
                expected = make_fail(ERROR_KEY, bad_data=data_expected)
                results = run_rule('my test name', my_rule, input_data)
                assert results == expected

        Arguments:
            name (str): Name to identify this test in output.
            rule (object): Your rule function object.
            data (list or dict):  List of dict of each data spec your rule requires
                to trigger.  If a single input data spec then a dict can be passed instead.
                Each dict must include both ``spec`` and ``data`` keys, and may optionally
                include ``path`` if necessary for the spec.

        Return:
            results of call to make_pass, make_fail, etc., or None

        Raises:
            KeyError: Raises if either spec or data keywords are not present.
        """
        idata = InputData(name)
        input_data = input_data if isinstance(input_data, list) else [input_data]
        for d in input_data:
            if 'path' in d:
                idata.add(d['spec'], d['data'], path=d['path'])
            else:
                idata.add(d['spec'], d['data'])
        return run_test(rule, idata)

    return _run_rule
