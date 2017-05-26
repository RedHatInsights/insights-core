from insights import tests
from insights.core.plugins import load
from itertools import islice
import pytest


def integration_test(module, test_func, input_data, expected):
    test_func(tests.integrate(input_data, module), expected)


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
        metafunc.parametrize("module,test_func,input_data,expected", args, ids=ids)
