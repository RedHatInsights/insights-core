import pytest
from itertools import islice

from insights import tests
from insights.core.dr import get_name, load_components


def test_integration(component, compare_func, input_data, expected):
    actual = tests.run_test(component, input_data)
    compare_func(actual, expected)


def pytest_generate_tests(metafunc):
    pattern = pytest.config.getoption("-k")
    generate_tests(metafunc, test_integration, "insights/tests", pattern=pattern)


def generate_tests(metafunc, test_func, package_names, pattern=None):
    """
    This function hooks in to pytest's test collection framework and provides a
    test for every (input_data, expected) tuple that is generated from all
    @archive_provider-decorated functions.
    """
    if metafunc.function is test_func:
        if type(package_names) not in (list, tuple):
            package_names = [package_names]
        for package_name in package_names:
            load_components(package_name, include=pattern or ".*", exclude=None)
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
                ids.append("#".join([get_name(f), input_data_name]))
        metafunc.parametrize("component,compare_func,input_data,expected", args, ids=ids)
