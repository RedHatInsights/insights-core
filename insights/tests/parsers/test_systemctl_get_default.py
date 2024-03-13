import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import systemctl_get_default
from insights.parsers.systemctl_get_default import SystemctlGetDefault
from insights.tests import context_wrap


SYSTEMCTL_GET_DEFAULT_CONTENT = """
graphical.target
""".strip()

SYSTEMCTL_GET_DEFAULT_EMPTY = """

""".strip()


def test_systemctl_get_default():
    result = SystemctlGetDefault(context_wrap(SYSTEMCTL_GET_DEFAULT_CONTENT))
    assert result.default_target == 'graphical.target'


def test_systemctl_get_default_empty():
    with pytest.raises(SkipComponent):
        SystemctlGetDefault(context_wrap(SYSTEMCTL_GET_DEFAULT_EMPTY))


def test_systemctl_get_default_doc():
    env = {
        'systemctl_get_default': SystemctlGetDefault(context_wrap(SYSTEMCTL_GET_DEFAULT_CONTENT))
    }
    failed, total = doctest.testmod(systemctl_get_default, globs=env)
    assert failed == 0
