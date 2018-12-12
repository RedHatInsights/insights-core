from insights.tests.integration import generate_tests, test_integration
import pytest
import os

__here__ = os.path.dirname(os.path.abspath(__file__))


def pytest_generate_tests(metafunc):
    pattern = pytest.config.getoption("-k")
    # "tests" is the path to the subdirectory containing the tests
    # Run py.test from the root dir of this rules project, meaning the dir
    # that contains the ``rules`` directory.
    generate_tests(metafunc, test_integration, "docs/examples/rules/tests", pattern=pattern)