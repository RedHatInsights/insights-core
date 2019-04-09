from insights.tests import context_wrap
from insights.parsers.crypto_policies import CryptoPoliciesConfig
from insights.parsers import SkipException
import pytest

CONFIG = """
DEFAULT
""".strip()

CONFIG_COMMENTED = """
# This file should contain a single keyword, the crypto policy to
# be applied by default to applications. The available policies are 
# restricted to the following profiles.
#
# * LEGACY: Ensures maximum compatibility with legacy systems (64-bit
#   security)
#
# * DEFAULT: A reasonable default for today's standards (112-bit security).
#
# * FUTURE: A level that will provide security on a conservative level that is
#   believed to withstand any near-term future attacks (128-bit security).
#
# * FIPS: Policy that enables only FIPS 140-2 approved or allowed algorithms.
#
# After modifying this file, you need to run update-crypto-policies
# for the changes to propagate.
#
DEFAULT
""".strip()  # noqa


def test_crypto_policies_config():
    result = CryptoPoliciesConfig(context_wrap(CONFIG))
    assert result.value == "DEFAULT"


def test_crypto_policies_commented():
    result = CryptoPoliciesConfig(context_wrap(CONFIG_COMMENTED))
    assert result.value == "DEFAULT"


def test_crypto_policies_config_empty():
    with pytest.raises(SkipException):
        CryptoPoliciesConfig(context_wrap(""))
