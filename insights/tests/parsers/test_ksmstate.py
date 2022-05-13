from insights.parsers import ksmstate, SkipException, ParseException
from insights.parsers.ksmstate import KSMState
from insights.tests import context_wrap
import pytest
import doctest

KSMSTATE0 = "0"
KSMSTATE1 = "1"
KSMSTATE2 = "2"
KSMSTATE_ab0 = ""
KSMSTATE_ab1 = "abc"
KSMSTATE_ab2 = """
abc
1
"""


def test_ksmstate():
    ksm = KSMState(context_wrap(KSMSTATE0))
    assert ksm.is_running is False
    assert ksm.value == '0'

    ksm = KSMState(context_wrap(KSMSTATE1))
    assert ksm.is_running is True
    assert ksm.value == '1'

    ksm = KSMState(context_wrap(KSMSTATE2))
    assert ksm.is_running is False
    assert ksm.value == '2'


def test_ksmstate_exp():
    with pytest.raises(SkipException):
        KSMState(context_wrap(KSMSTATE_ab0))

    with pytest.raises(ParseException):
        KSMState(context_wrap(KSMSTATE_ab1))

    with pytest.raises(ParseException):
        KSMState(context_wrap(KSMSTATE_ab2))


def test_ksmstate_doc():
    env = {'ksm': KSMState(context_wrap(KSMSTATE0))}
    failed, total = doctest.testmod(ksmstate, globs=env)
    assert failed == 0
