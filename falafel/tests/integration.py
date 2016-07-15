from falafel import tests
from falafel.core import DEFAULT_PLUGIN_MODULE
import pytest


def integration_test(module, test_func, input_data, expected):
    test_func(tests.integrate(input_data, module), expected)


def generate_tests(metafunc, test_func):
    """
    This function hooks in to pytest's test collection framework and provides a
    test for every (input_data, expected) tuple that is generated from all
    @archive_provider-decorated functions.
    """
    if metafunc.function == test_func and not hasattr(test_func, "parametrized"):
        tests.ensure_tests_loaded(DEFAULT_PLUGIN_MODULE)
        test_func.parametrized = True  # Hack to ensure we don't generate tests twice
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
