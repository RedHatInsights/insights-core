from insights.tests import context_wrap
from insights.parsers.crypto_policies import CryptoPoliciesStateCurrent
from insights.parsers import SkipException
import pytest

CONFIG = """
DEFAULT
""".strip()


def test_crypto_policies_state_current():
    result = CryptoPoliciesStateCurrent(context_wrap(CONFIG))
    assert result.value == "DEFAULT"


def test_crypto_policies_state_current_empty():
    with pytest.raises(SkipException):
        CryptoPoliciesStateCurrent(context_wrap(""))
