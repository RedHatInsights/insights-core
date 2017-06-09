from insights.parsers import ksmstate
from insights.tests import context_wrap

KSMSTATE0 = "0"
KSMSTATE1 = "1"


def test_is_running_0():
    ksm_info = ksmstate.is_running(context_wrap(KSMSTATE0))
    assert ksm_info.get('running') is False


def test_is_running_1():
    ksm_info = ksmstate.is_running(context_wrap(KSMSTATE1))
    assert ksm_info.get('running') is True
