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
from insights.parsers.sysconfig import SshdSysconfig

SSHD_SYSCONFIG = """
# Configuration file for the sshd service.

# The server keys are automatically generated if they are missing.
# To change the automatic creation, adjust sshd.service options for
# example using  systemctl enable sshd-keygen@dsa.service  to allow creation
# of DSA key or  systemctl mask sshd-keygen@rsa.service  to disable RSA key
# creation.

# System-wide crypto policy:
# To opt-out, uncomment the following line
# CRYPTO_POLICY=
CRYPTO_POLICY=
""".strip()


def test_sysconfig_sshd():
    result = SshdSysconfig(context_wrap(SSHD_SYSCONFIG))
    assert result["CRYPTO_POLICY"] == ''
    assert result.get("CRYPTO_POLICY") == ''
    assert result.get("OPTIONS1") is None
    assert "OPTIONS1" not in result
    assert "CRYPTO_POLICY" in result
