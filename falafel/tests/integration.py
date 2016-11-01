from falafel import tests
from falafel.core import load_package
import pytest


def integration_test(module, test_func, input_data, expected):
    test_func(tests.integrate(input_data, module), expected)


def completed(test_func, package_name):
    if not hasattr(test_func, "parametrized"):
        test_func.parametrized = []
    return any(package_name.startswith(p) for p in test_func.parametrized)


def generate_tests(metafunc, test_func, package_name):
    """
    This function hooks in to pytest's test collection framework and provides a
    test for every (input_data, expected) tuple that is generated from all
    @archive_provider-decorated functions.
    """
    if metafunc.function == test_func and not completed(test_func, package_name):
        load_package(package_name)
        test_func.parametrized.append(package_name)
        args = []
        ids = []
        for f in tests.ARCHIVE_GENERATORS:
            if not f.slow or pytest.config.getoption("--runslow"):
                for t in f():
                    args.append(t)
                    input_data_name = t[2].name if not isinstance(t[2], list) else "multi-node"
                    fn_name = f.serializable_id.split(".")[-1]
                    ids.append("#".join([fn_name, input_data_name]))
        metafunc.parametrize("module,test_func,input_data,expected", args, ids=ids)
