import pytest

from insights import SkipComponent
from insights.components.cryptsetup import HasCryptsetupWithTokens, HasCryptsetupWithoutTokens
from insights.parsers.installed_rpms import InstalledRpms
from insights.tests import context_wrap

RPMS_TOKENS_SUPPORT = "cryptsetup-2.4.3-2.fc36.x86_64"
RPMS_NO_TOKENS_SUPPORT = "cryptsetup-2.0.3-6.el7.x86_64"
RPMS_CRYPTSETUP_NOT_INSTALLED = "cryptsetup-libs-2.0.3-6.el7.x86_64"


def test_has_cryptsetup_with_tokens():
    rpms = InstalledRpms(context_wrap(RPMS_TOKENS_SUPPORT))
    HasCryptsetupWithTokens(rpms)

    rpms = InstalledRpms(context_wrap(RPMS_NO_TOKENS_SUPPORT))
    with pytest.raises(SkipComponent):
        HasCryptsetupWithTokens(rpms)

    rpms = InstalledRpms(context_wrap(RPMS_CRYPTSETUP_NOT_INSTALLED))
    with pytest.raises(SkipComponent):
        HasCryptsetupWithTokens(rpms)


def test_has_cryptsetup_without_tokens():
    rpms = InstalledRpms(context_wrap(RPMS_NO_TOKENS_SUPPORT))
    HasCryptsetupWithoutTokens(rpms)

    rpms = InstalledRpms(context_wrap(RPMS_TOKENS_SUPPORT))
    with pytest.raises(SkipComponent):
        HasCryptsetupWithoutTokens(rpms)

    rpms = InstalledRpms(context_wrap(RPMS_CRYPTSETUP_NOT_INSTALLED))
    with pytest.raises(SkipComponent):
        HasCryptsetupWithoutTokens(rpms)
