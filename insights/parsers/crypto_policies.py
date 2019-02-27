"""
crypto-policies - files in ``/etc/crypto-policies/back-ends/``
==============================================================

This is a collection of parsers that all deal with the generated configuration
files under the ``/etc/crypto-policies/back-ends/`` folder.  Parsers included
in this module are:

CryptoPoliciesConfig - file ``/etc/crypto-policies/config``
-----------------------------------------------------------

CryptoPoliciesStateCurrent - file ``/etc/crypto-policies/state/current``
------------------------------------------------------------------------

CryptoPoliciesOpensshserver - file ``/etc/crypto-policies/back-ends/opensshserver.config``
------------------------------------------------------------------------------------------
"""

from insights import Parser, parser, SysconfigOptions
from insights.specs import Specs
from insights.parsers import SkipException


@parser(Specs.crypto_policies_config)
class CryptoPoliciesConfig(Parser):
    """
    This parser reads the ``/etc/crypto-policies/config`` file.
    The contents of the file is a single-line value, available
    in the ``value`` property.

    Sample Input::

        LEGACY

    Examples:
        >>> cp_c.value
        'LEGACY'
    """
    def parse_content(self, content):
        if not content:
            raise SkipException("/etc/crypto-policies/config is empty")
        self.value = content[0]


@parser(Specs.crypto_policies_state_current)
class CryptoPoliciesStateCurrent(Parser):
    """
    This parser reads the ``/etc/crypto-policies/state/current`` file.
    The contents of the file is a single-line value, available
    in the ``value`` property.

    Sample Input::

        LEGACY

    Examples:
        >>> cp_sc.value
        'LEGACY'
    """
    def parse_content(self, content):
        if not content:
            raise SkipException("/etc/crypto-policies/state/current is empty")
        self.value = content[0]


@parser(Specs.crypto_policies_opensshserver)
class CryptoPoliciesOpensshserver(SysconfigOptions):
    """
    This parser reads the ``/etc/crypto-policies/back-ends/opensshserver.config``
    file.  It uses the ``SysconfigOptions`` parser class to convert the file into
    a dictionary of options. It also provides the ``options`` property as a helper
    to retrieve the ``CRYPTO_POLICY`` variable.

    Sample Input::

        CRYPTO_POLICY='-oCiphers=aes256-gcm@openssh.com,3des-cbc -oMACs=umac-128-etm@openssh.com'

    Examples:
        >>> 'CRYPTO_POLICY' in cp_os
        True
        >>> cp_os.options
        '-oCiphers=aes256-gcm@openssh.com,3des-cbc -oMACs=umac-128-etm@openssh.com'
    """
    @property
    def options(self):
        """ (union[str, None]): The value of the ``CRYPTO_POLICY`` variable if it exists, else None."""
        return self.data.get('CRYPTO_POLICY', None)
