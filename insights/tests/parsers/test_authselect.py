import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import authselect
from insights.parsers.authselect import AuthSelectCurrent
from insights.tests import context_wrap

AUTHSELECT_CURRENT_1 = """
Profile ID: sssd
Enabled features:
- with-sudo
- with-mkhomedir
- with-smartcard
""".strip()

AUTHSELECT_CURRENT_2 = """
Profile ID: custom/password-policy
Enabled features: None
""".strip()

AUTHSELECT_CURRENT_EMPTY = ""

AUTHSELECT_CURRENT_NG = """
No existing configuration detected.
""".strip()


def test_authselect_current():
    asc = AuthSelectCurrent(context_wrap(AUTHSELECT_CURRENT_1))
    assert asc.profile_id == 'sssd'
    assert asc.enabled_features == ['with-sudo', 'with-mkhomedir', 'with-smartcard']

    asc = AuthSelectCurrent(context_wrap(AUTHSELECT_CURRENT_2))
    assert asc.profile_id == 'custom/password-policy'
    assert asc.enabled_features == []


def test_authselect_current_exp():
    with pytest.raises(SkipComponent):
        AuthSelectCurrent(context_wrap(AUTHSELECT_CURRENT_EMPTY))

    with pytest.raises(SkipComponent):
        AuthSelectCurrent(context_wrap(AUTHSELECT_CURRENT_NG))


def test_doc_examples():
    env = {
        'asc': AuthSelectCurrent(context_wrap(AUTHSELECT_CURRENT_1))
    }
    failed, total = doctest.testmod(authselect, globs=env)
    assert failed == 0
