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
from insights.parsers.crypto_policies import CryptoPoliciesBind
from insights.parsers import SkipException
import pytest

CONFIG = """
disable-algorithms "." {
RSAMD5;
DSA;
};
disable-ds-digests "." {
GOST;
};
""".strip()

CONFIG_EMPTY_SECTIONS = """
disable-algorithms "." {
};
disable-ds-digests "." {
};
""".strip()


def test_crypto_policies_bind():
    result = CryptoPoliciesBind(context_wrap(CONFIG))
    assert "GOST" in result.disable_ds_digests
    assert "DSA" in result.disable_algorithms
    assert ["RSAMD5", "DSA"] == result.disable_algorithms
    assert ["GOST"] == result.disable_ds_digests


def test_crypto_policies_bind_empty():
    with pytest.raises(SkipException):
        CryptoPoliciesBind(context_wrap(""))
    result = CryptoPoliciesBind(context_wrap(CONFIG_EMPTY_SECTIONS))
    assert [] == result.disable_algorithms
    assert [] == result.disable_ds_digests
