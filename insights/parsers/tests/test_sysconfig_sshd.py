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
