import argparse
import os
import re
import sys

SETUP_CFG_CONTENT = """
[tool:pytest]
# Look for tests only in tests directories.
python_files = "%s/tests/*"
# Display summary info for (s)skipped, (X)xpassed, (x)xfailed, (f)failed and (e)errored tests
# On Jenkins pytest for some reason runs tests from ./build/ directory - ignore them.
addopts = "-rsxXfE --ignore=./build/"
testpaths = "%s"
"""

INTEGRATION_PY_CONTENT = """
from insights.tests import integration, integrate
import pytest


def test_integration(module, comparison_func, input_data, expected):
    actual = integrate(input_data, module)
    comparison_func(actual, expected)


def pytest_generate_tests(metafunc):
    pattern = pytest.config.getoption("-k")
    integration.generate_tests(metafunc, test_integration, "%s.tests", pattern=pattern)
"""

SETUP_PY_CONTENT = """
import os
from distutils.core import Command
from setuptools import setup, find_packages


class CustomCommand(Command):
    user_options = []

    def initialize_options(self):
        self.cwd = None

    def finalize_options(self):
        self.cwd = os.getcwd()


class CleanCommand(CustomCommand):
    description = "clean up the current environment"

    def run(self):
        assert os.getcwd() == self.cwd, 'Must be in package root: %%s' %% self.cwd
        os.system('rm -rf ./bin ./include ./lib ./lib64 ./*.egg-info ./man ./dist ./pip-selfcheck.json')


class BootstrapCommand(CustomCommand):
    description = "bootstrap for development"

    def run(self):
        assert os.getcwd() == self.cwd, 'Must be in package root: %%s' %% self.cwd
        os.system('virtualenv .')
        os.system('bin/pip install -e .[develop]')


if __name__ == "__main__":
    setup(
        name="%(name)s",
        version="0.0.1",
        description="%(name)s Plugin Repository",
        packages=find_packages(),
        install_requires=[
            'insights-core',
        ],
        extras_require={
            'develop': [
                'coverage',
                'pytest',
                'pytest-cov',
                'flake8',
            ],
            'optional': [
                'python-cjson'
            ]
        },
        cmdclass={
            'clean': CleanCommand,
            'bootstrap': BootstrapCommand,
        }
    )
"""

CONFTEST_PY_CONTENT = """
# This is configuration file for pytest.
# Pytest first searches this file before running unit tests.

# Enable logging output in stderr for failing tests.
import logging


def pytest_addoption(parser):
    parser.addoption("--runslow", action="store_true", default=False, help="run slow tests")
    parser.addoption("--appdebug", action="store_true", default=False, help="debug loggging")
    parser.addoption("--smokey", action="store_true", default=False, help="run tests fast")


def pytest_configure(config):
    level = logging.DEBUG if config.getoption("--appdebug") else logging.ERROR
    logging.basicConfig(level=level)
"""

README_MD_CONTENT = """
# %s

## Getting Started

Setup your initial environment:

```
$ python setup.py bootstrap
```
If `insights-core` fails to install then enable your virtual environment
and use the Optional step below to install a local
copy of insights-core, then run the command `pip install -e .[develop]`.

Enable the virtual environment:

```
$ source bin/activate
```

*Optional:*
If you are also developing mappers then you can install your local
insights environment:

```
$ pip install -e path_to_insights_dir
```

Create your first rule in the directory %s and create the test in
%s.  Then run your test:

```
$ py.test
```
"""
FLAKE8_CONTENT = """
[flake8]
ignore = E501,E126,E127,E128
exclude = bin,docs,include,lib,lib64
""".strip()


def create_module(name):
    if not os.path.exists(name):
        os.makedirs(name)
    init_py = os.path.join(name, "__init__.py")
    if not os.path.exists(init_py):
        with open(init_py, "a"):
            os.utime(init_py, None)


def write_out_file(path, content):
    if not os.path.exists(path):
        with open(path, "w") as fp:
            fp.write(content.lstrip())


def main():
    p = argparse.ArgumentParser("insights-scaffold")
    p.add_argument("module")
    args = p.parse_args()
    if re.search(r"[^a-zA-Z.]", args.module):
        print "Please provide valid module name"
        sys.exit(1)
    module_path = args.module.replace(".", "/")
    segment = ""
    for s in module_path.split("/"):
        segment = os.path.join(segment, s)
        create_module(segment)
    plugin_path = os.path.join(module_path, "plugins")
    create_module(plugin_path)
    test_path = os.path.join(module_path, "tests")
    create_module(test_path)
    write_out_file(os.path.join(test_path, "integration.py"), INTEGRATION_PY_CONTENT % args.module)
    write_out_file("setup.py", SETUP_PY_CONTENT % {"name": args.module.title()})
    write_out_file("setup.cfg", SETUP_CFG_CONTENT % (args.module, args.module))
    write_out_file("conftest.py", CONFTEST_PY_CONTENT)
    write_out_file("readme.md", README_MD_CONTENT % (args.module, plugin_path, test_path))
    write_out_file(".flake8", FLAKE8_CONTENT)
