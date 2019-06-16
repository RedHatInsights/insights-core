#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from insights.tests import context_wrap
from insights.parsers import crypto_policies
from insights.parsers.crypto_policies import CryptoPoliciesOpensshserver, CryptoPoliciesConfig, \
    CryptoPoliciesStateCurrent, CryptoPoliciesBind
import doctest


OPENSSHSERVER = """
CRYPTO_POLICY='-oCiphers=aes256-gcm@openssh.com,3des-cbc -oMACs=umac-128-etm@openssh.com'
""".strip()

CONFIG = """
LEGACY
""".strip()

STATECURRENT = """
LEGACY
""".strip()

BIND = """
disable-algorithms "." {
RSAMD5;
DSA;
};
disable-ds-digests "." {
GOST;
};
""".strip()


def test_crypto_policies_doc():
    env = {
        'cp_os': CryptoPoliciesOpensshserver(context_wrap(OPENSSHSERVER)),
        'cp_c': CryptoPoliciesConfig(context_wrap(CONFIG, path="/etc/crypto-policies/config")),
        'cp_sc': CryptoPoliciesStateCurrent(context_wrap(STATECURRENT, path="/etc/crypto-policies/state/current")),
        'cp_bind': CryptoPoliciesBind(context_wrap(BIND)),
    }
    failed, total = doctest.testmod(crypto_policies, globs=env)
    assert failed == 0
