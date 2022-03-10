from insights.parsers import ktimer_lockless
from insights.parsers.ktimer_lockless import KTimerLockless
from insights.parsers import SkipException
from insights.tests import context_wrap
import pytest
import doctest

KTIMER_LOCKLESS_OUTPUT = "0"

KTIMER_LOCKLESS_EMPTY = ""


def test_ktimer_lockless_parser():
    ktimer_lockless_obj = ktimer_lockless.KTimerLockless(context_wrap(KTIMER_LOCKLESS_OUTPUT))
    assert ktimer_lockless_obj.ktimer_lockless_val == 0


def test_empty():
    with pytest.raises(SkipException) as e:
        KTimerLockless(context_wrap(KTIMER_LOCKLESS_EMPTY))
    assert 'The file is empty' in str(e)


def test_ktimer_lockless_examples():
    env = {
        'ktimer_lockless': KTimerLockless(context_wrap(KTIMER_LOCKLESS_OUTPUT)),
    }
    failed, total = doctest.testmod(ktimer_lockless, globs=env)
    assert failed == 0
