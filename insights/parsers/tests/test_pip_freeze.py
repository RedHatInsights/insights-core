import pytest
from insights.parsers.pip_freeze import PipFreeze
from insights.tests import context_wrap

OKAY = """
psutil==7.14
python-memcached==8.11
scooby-dooby-doo==1.0.0
"""

OKAY_WARN = """
DEPRECATION: Python 2.7 will reach the end of its life on January 1st, 2020. Please upgrade your Python as Python 2.7 won't be maintained after that date. A future version of pip will drop support for Python 2.7.
psutil==7.14
python-memcached==8.11
scooby-dooby-doo==1.0.0
"""

EMPTY = """"""




@pytest.mark.parametrize('pip_freeze_output', [OKAY, OKAY_WARN])
def test_ok(pip_freeze_output):
    pf = PipFreeze(context_wrap(pip_freeze_output))
    assert 'psutil==7.14' == pf.pkgs[0]
    assert 'psutil' == pf.pkg_names[0]
    assert '7.14' == pf.pkg_versions[0]

    assert 'python-memcached==8.11' == pf.pkgs[1]
    assert 'python-memcached' == pf.pkg_names[1]
    assert '8.11' == pf.pkg_versions[1]

    assert 'scooby-dooby-doo==1.0.0' == pf.pkgs[2]
    assert 'scooby-dooby-doo' == pf.pkg_names[2]
    assert '1.0.0' == pf.pkg_versions[2]


def test_empty():
    pf = PipFreeze(context_wrap(EMPTY))
    assert 0 == len(pf.pkg_names)
    assert 0 == len(pf.pkg_versions)
    assert 0 == len(pf.pkgs)

