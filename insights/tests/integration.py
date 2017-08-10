from insights import tests
from insights.tests import integrate
from insights.core.plugins import load
from itertools import islice
import pytest


def generate_tests(metafunc, test_func, package_names, pattern=None):
    """
    This function hooks in to pytest's test collection framework and provides a
    test for every (input_data, expected) tuple that is generated from all
    @archive_provider-decorated functions.
    """
    if metafunc.function == test_func:
        if type(package_names) not in (list, tuple):
            package_names = [package_names]
        for package_name in package_names:
            load(package_name, pattern)
        args = []
        ids = []
        slow_mode = pytest.config.getoption("--runslow")
        fast_mode = pytest.config.getoption("--smokey")
        for f in tests.ARCHIVE_GENERATORS:
            ts = f(stride=1 if slow_mode else f.stride)
            if fast_mode:
                ts = islice(ts, 0, 1)
            for t in ts:
                args.append(t)
                input_data_name = t[2].name if not isinstance(t[2], list) else "multi-node"
                ids.append("#".join([f.serializable_id, input_data_name]))
        metafunc.parametrize("module,comparison_func,input_data,expected", args, ids=ids)


# The folowing two functions run any integration tests found in the insights directory
# to be run during py.test testing.
#
# The insights-core repo didn't have any plugins so no need for integration testing till
# the fava plugins got added, partly to test that integration testing worked for fava plugins.


def test_integration(module, comparison_func, input_data, expected):
    actual = integrate(input_data, module)
    comparison_func(actual, expected)


def pytest_generate_tests(metafunc):
    pattern = pytest.config.getoption("-k")
    generate_tests(metafunc, test_integration, "insights.tests", pattern=pattern)
