"""
HasCryptsetupWithTokens, HasCryptsetupWithoutTokens
===================================================

The ``HasCryptsetupWithTokens``/``HasCryptsetupWithoutTokens`` component uses
``InstalledRpms`` parser to determine if cryptsetup package is installed and if
it has tokens support (since version 2.4.0), if not it raises ``SkipComponent``
so that the dependent component will not fire. Can be added as a dependency of
a parser so that the parser only fires if the ``cryptsetup`` dependency and
token support is met.
"""
from insights.core.exceptions import SkipComponent
from insights.core.plugins import component
from insights.parsers.installed_rpms import InstalledRpms, InstalledRpm


@component(InstalledRpms)
class HasCryptsetupWithTokens(object):
    """The ``HasCryptsetupWithTokens`` component uses ``InstalledRpms`` parser
    to determine if cryptsetup package is installed and if it has tokens
    support (since version 2.4.0), if not it raises ``SkipComponent``

    Raises:
        SkipComponent: When ``cryptsetup`` package is strictly less than 2.4.0,
        or when cryptsetup package is not installed
    """
    def __init__(self, rpms):
        rpm = rpms.get_max("cryptsetup")

        if rpm is None:
            raise SkipComponent("cryptsetup package is not installed")

        if rpm < InstalledRpm("cryptsetup-2.4.0-0"):
            raise SkipComponent("cryptsetup package with token support is not installed")


@component(InstalledRpms)
class HasCryptsetupWithoutTokens(object):
    """The ``HasCryptsetupWithoutTokens`` component uses ``InstalledRpms``
    parser to determine if cryptsetup package is installed and if it does not
    have tokens support (below version 2.4.0), if not it raises
    ``SkipComponent``

    Raises:
        SkipComponent: When ``cryptsetup`` package is at least 2.4.0, or when
        cryptsetup package is not installed
    """
    def __init__(self, rpms):
        rpm = rpms.get_max("cryptsetup")

        if rpm is None:
            raise SkipComponent("cryptsetup package is not installed")

        if rpm >= InstalledRpm("cryptsetup-2.4.0-0"):
            raise SkipComponent("cryptsetup package with token support is installed")
