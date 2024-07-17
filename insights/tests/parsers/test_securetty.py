import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import securetty
from insights.parsers.securetty import Securetty
from insights.tests import context_wrap

SECURETTY = """
console
# tty0
tty1
tty2
tty3
""".strip()

SECURETTY_EMPTY = ""


def test_securetty():
    securetty = Securetty(context_wrap(SECURETTY))
    assert len(securetty.terminals) == 4
    assert securetty.terminals == ['console', 'tty1', 'tty2', 'tty3']


def test_class_exceptions():
    with pytest.raises(SkipComponent) as e:
        Securetty(context_wrap(SECURETTY_EMPTY))
    assert "No terminals found." in str(e)


def test_doc():
    env = {
        "securetty": Securetty(context_wrap(SECURETTY)),
    }
    failed_count, total = doctest.testmod(securetty, globs=env)
    assert failed_count == 0
