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

CryptoPoliciesBind - file ``/etc/crypto-policies/back-ends/bind.config``
------------------------------------------------------------------------
"""

from insights import Parser, parser, SysconfigOptions
from insights.specs import Specs
from insights.parsers import SkipException, get_active_lines


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
        self.value = get_active_lines(content)[0]


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
        self.value = get_active_lines(content)[0]


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


@parser(Specs.crypto_policies_bind)
class CryptoPoliciesBind(Parser):
    """
    This parser reads the ``/etc/crypto-policies/back-ends/bind.config`` file.
    The sections ``disable-algorithms`` and ``disable-ds-digests`` are in the
    properties ``disable_algorithms`` and ``disable_ds_digests``.

    Sample Input::

        disable-algorithms "." {
        RSAMD5;
        DSA;
        };
        disable-ds-digests "." {
        GOST;
        };

    Examples:
        >>> 'GOST' in cp_bind.disable_ds_digests
        True
        >>> cp_bind.disable_algorithms
        ['RSAMD5', 'DSA']
    """
    def parse_content(self, content):
        if not content:
            raise SkipException("/etc/crypto-policies/back-ends/bind.config is empty")
        self.value = content
        in_da = False
        in_ddd = False
        da = []
        ddd = []
        for line in self.value:
            if line.strip().lower().startswith("disable-algorithms"):
                in_da = True
                continue
            if line.strip().lower().startswith("disable-ds-digests"):
                in_ddd = True
                continue
            if line.strip().startswith("}"):
                in_da = False
                in_ddd = False
                continue
            algo = line.strip().strip(''';'"''')
            if in_da:
                da.append(algo)
            if in_ddd:
                ddd.append(algo)
        self.disable_algorithms = da
        self.disable_ds_digests = ddd
