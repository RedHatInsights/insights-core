import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import sys_class
from insights.parsers.sys_class import TtyConsoleActive
from insights.tests import context_wrap


TTY_CONSOLE_ACTIVE = """
tty0 ttyS0
""".strip()

TTY_CONSOLE_ACTIVE_EMPTY = ""

TTY_CONSOLE_ACTIVE_MULTI_LINES = """
tty0 ttyS0
tty0 ttyS0
""".strip()


def test_doc():
    env = {
        'tty_console_active': TtyConsoleActive(context_wrap(TTY_CONSOLE_ACTIVE))
    }
    failed, total = doctest.testmod(sys_class, globs=env)
    assert failed == 0


def test_tty_console_active():
    tty_console_active = TtyConsoleActive(context_wrap(TTY_CONSOLE_ACTIVE))
    assert tty_console_active.devices == ['tty0', 'ttyS0']


def test_class_exceptions():
    with pytest.raises(SkipComponent) as e:
        TtyConsoleActive(context_wrap(TTY_CONSOLE_ACTIVE_MULTI_LINES))
    assert 'This should be an one line file' in str(e)

    with pytest.raises(SkipComponent) as e:
        TtyConsoleActive(context_wrap(TTY_CONSOLE_ACTIVE_EMPTY))
    assert 'Empty content' in str(e)
