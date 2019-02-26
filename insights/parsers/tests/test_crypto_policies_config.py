from insights.tests import context_wrap
from insights.parsers.crypto_policies import CryptoPoliciesConfig
from insights.parsers import SkipException
import pytest

CONFIG = """
DEFAULT
""".strip()


def test_crypto_policies_config():
    result = CryptoPoliciesConfig(context_wrap(CONFIG))
    assert result.value == "DEFAULT"


def test_crypto_policies_config_empty():
    with pytest.raises(SkipException):
        CryptoPoliciesConfig(context_wrap(""))
