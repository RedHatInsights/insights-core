"""
Nox testing for Insights Core
=============================

To use this file install nox:

    $ pip install --user --upgrade nox

Then you can run all nox tests:

    $ nox

To run selected tests use `nox --list` to show the test names and then you can run
an individual test with:

    $ nox -s test-2.7

See the nox documentation for more info:

    https://nox.thea.codes/en/stable/index.html

If you need to install multiple Python versions and don't
want to install via RPM, check out Pyenv:

    https://github.com/pyenv/pyenv
"""
import nox


@nox.session(python=["2.7", "3.6", "3.8", "3.9", "3.10", "3.11"])
def testing(session):
    session.install('.[testing]')
    session.run('pytest')


@nox.session(python=["3.8"])
def linting(session):
    session.install('.[linting]')
    session.run('flake8')


@nox.session(python=["3.8"])
def docs(session):
    session.install('.[docs]')
    session.run('sphinx-build', '-W', '-b', 'html', '-qa', '-E', 'docs', 'docs/_build/html')
