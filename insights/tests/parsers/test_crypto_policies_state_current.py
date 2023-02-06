import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers.crypto_policies import CryptoPoliciesStateCurrent
from insights.tests import context_wrap

CONFIG = """
DEFAULT
""".strip()


def test_crypto_policies_state_current():
    result = CryptoPoliciesStateCurrent(context_wrap(CONFIG))
    assert result.value == "DEFAULT"


def test_crypto_policies_state_current_empty():
    with pytest.raises(SkipComponent):
        CryptoPoliciesStateCurrent(context_wrap(""))
