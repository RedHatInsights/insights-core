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
from insights.core import Parser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.parsers import get_active_lines
from insights.specs import Specs


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
            raise SkipComponent("/etc/crypto-policies/config is empty")
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
            raise SkipComponent("/etc/crypto-policies/state/current is empty")
        self.value = get_active_lines(content)[0]


@parser(Specs.crypto_policies_opensshserver)
class CryptoPoliciesOpensshserver(Parser, dict):
    """
    This parser reads the ``/etc/crypto-policies/back-ends/opensshserver.config`` file.

    Sample Input on RHEL8::

        CRYPTO_POLICY='-oCiphers=aes256-gcm@openssh.com,3des-cbc -oMACs=umac-128-etm@openssh.com'

    Sample Input on RHEL9::

        Ciphers aes256-gcm@openssh.com,chacha20-poly1305@openssh.com,aes256-ctr,aes128-gcm@openssh.com,aes128-ctr
        MACs hmac-sha2-256-etm@openssh.com,hmac-sha1-etm@openssh.com,umac-128-etm@openssh.com,hmac-sha2-512-etm@openssh.com,hmac-sha2-256,hmac-sha1,umac-128@openssh.com,hmac-sha2-512

    Examples:
        >>> 'CRYPTO_POLICY' in cp_os
        True
        >>> cp_os.options
        {'Ciphers': 'aes256-gcm@openssh.com,3des-cbc', 'MACs': 'umac-128-etm@openssh.com'}
    """
    def parse_content(self, content):
        if not content:
            raise SkipComponent("/etc/crypto-policies/back-ends/opensshserver.config is empty")

        result = {}
        for line in get_active_lines(content):
            if "=" in line:
                key, value = line.split('=', 1)
                result[key.strip()] = value.strip("' ")
            elif line[0].isupper():
                key, value = line.split(' ', 1)
                result[key.strip()] = value.strip()
        self.update(result)

    @property
    def options(self):
        """return the configuratios as dict format"""
        whole_configuration = self.get('CRYPTO_POLICY', None)
        if whole_configuration and whole_configuration.startswith("-o"):
            result = {}
            configurations = whole_configuration.split("-o")
            for item in configurations[1:]:
                key, value = item.split("=", 1)
                result[key.strip()] = value.strip()
            return result
        else:
            return self


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
            raise SkipComponent("/etc/crypto-policies/back-ends/bind.config is empty")
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
