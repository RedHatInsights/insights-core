import pytest

from insights.core.exceptions import SkipComponent
from insights.tests import context_wrap
from insights.parsers.crypto_policies import CryptoPoliciesOpensshserver

CPSSHD_1 = """
CRYPTO_POLICY='-oCiphers=aes256-gcm@openssh.com,3des-cbc -oMACs=umac-128-etm@openssh.com'
""".strip()

CPSSHD_2 = """

CRYPTO_POLICY='-oCiphers=aes256-gcm@openssh.com,3des-cbc -oMACs=umac-128-etm@openssh.com,hmac-sha1-etm@openssh.com -oGSSAPIKexAlgorithms=gss-gex-sha1-,gss-group14-sha1- -oKexAlgorithms=curve25519-sha256@libssh.org,ecdh-sha2-nistp256,ecdh-sha2-nistp384,ecdh-sha2-nistp521,diffie-hellman-group-exchange-sha256,diffie-hellman-group14-sha256,diffie-hellman-group16-sha512,diffie-hellman-group18-sha512,diffie-hellman-group-exchange-sha1,diffie-hellman-group14-sha1 -oHostKeyAlgorithms=ssh-rsa,ssh-rsa-cert-v01@openssh.com,ssh-dss,ssh-dss-cert-v01@openssh.com,rsa-sha2-256,ecdsa-sha2-nistp256,ecdsa-sha2-nistp256-cert-v01@openssh.com,ecdsa-sha2-nistp384,ecdsa-sha2-nistp384-cert-v01@openssh.com,rsa-sha2-512,ecdsa-sha2-nistp521,ecdsa-sha2-nistp521-cert-v01@openssh.com,ssh-ed25519,ssh-ed25519-cert-v01@openssh.com -oPubkeyAcceptedKeyTypes=ssh-rsa,ssh-rsa-cert-v01@openssh.com,ssh-dss,ssh-dss-cert-v01@openssh.com,rsa-sha2-256,ecdsa-sha2-nistp256,ecdsa-sha2-nistp256-cert-v01@openssh.com,ecdsa-sha2-nistp384,ecdsa-sha2-nistp384-cert-v01@openssh.com,rsa-sha2-512,ecdsa-sha2-nistp521,ecdsa-sha2-nistp521-cert-v01@openssh.com,ssh-ed25519,ssh-ed25519-cert-v01@openssh.com'
"""  # no strip on purpose

CPSSHD_3 = """
Ciphers aes256-gcm@openssh.com,chacha20-poly1305@openssh.com,aes256-ctr,aes128-gcm@openssh.com,aes128-ctr
MACs hmac-sha2-256-etm@openssh.com,hmac-sha1-etm@openssh.com,umac-128-etm@openssh.com,hmac-sha2-512-etm@openssh.com,hmac-sha2-256,hmac-sha1,umac-128@openssh.com,hmac-sha2-512
GSSAPIKexAlgorithms gss-curve25519-sha256-,gss-nistp256-sha256-,gss-group14-sha256-,gss-group16-sha512-
CASignatureAlgorithms ecdsa-sha2-nistp256,sk-ecdsa-sha2-nistp256@openssh.com,ecdsa-sha2-nistp384,ecdsa-sha2-nistp521,ssh-ed25519,sk-ssh-ed25519@openssh.com,rsa-sha2-256,rsa-sha2-512
RequiredRSASize 2048
""".strip()


def test_crypto_policies_opensshserver_1():
    result = CryptoPoliciesOpensshserver(context_wrap(CPSSHD_1))
    assert result["CRYPTO_POLICY"] == "-oCiphers=aes256-gcm@openssh.com,3des-cbc -oMACs=umac-128-etm@openssh.com"
    assert result.get("CRYPTO_POLICY") == "-oCiphers=aes256-gcm@openssh.com,3des-cbc -oMACs=umac-128-etm@openssh.com"
    assert result.get("OPTIONS1") is None
    assert "OPTIONS1" not in result
    assert "CRYPTO_POLICY" in result
    assert result.options == {"Ciphers": "aes256-gcm@openssh.com,3des-cbc", "MACs": "umac-128-etm@openssh.com"}


def test_crypto_policies_opensshserver_2():
    result = CryptoPoliciesOpensshserver(context_wrap(CPSSHD_2))
    assert result["CRYPTO_POLICY"] == '-oCiphers=aes256-gcm@openssh.com,3des-cbc -oMACs=umac-128-etm@openssh.com,hmac-sha1-etm@openssh.com -oGSSAPIKexAlgorithms=gss-gex-sha1-,gss-group14-sha1- -oKexAlgorithms=curve25519-sha256@libssh.org,ecdh-sha2-nistp256,ecdh-sha2-nistp384,ecdh-sha2-nistp521,diffie-hellman-group-exchange-sha256,diffie-hellman-group14-sha256,diffie-hellman-group16-sha512,diffie-hellman-group18-sha512,diffie-hellman-group-exchange-sha1,diffie-hellman-group14-sha1 -oHostKeyAlgorithms=ssh-rsa,ssh-rsa-cert-v01@openssh.com,ssh-dss,ssh-dss-cert-v01@openssh.com,rsa-sha2-256,ecdsa-sha2-nistp256,ecdsa-sha2-nistp256-cert-v01@openssh.com,ecdsa-sha2-nistp384,ecdsa-sha2-nistp384-cert-v01@openssh.com,rsa-sha2-512,ecdsa-sha2-nistp521,ecdsa-sha2-nistp521-cert-v01@openssh.com,ssh-ed25519,ssh-ed25519-cert-v01@openssh.com -oPubkeyAcceptedKeyTypes=ssh-rsa,ssh-rsa-cert-v01@openssh.com,ssh-dss,ssh-dss-cert-v01@openssh.com,rsa-sha2-256,ecdsa-sha2-nistp256,ecdsa-sha2-nistp256-cert-v01@openssh.com,ecdsa-sha2-nistp384,ecdsa-sha2-nistp384-cert-v01@openssh.com,rsa-sha2-512,ecdsa-sha2-nistp521,ecdsa-sha2-nistp521-cert-v01@openssh.com,ssh-ed25519,ssh-ed25519-cert-v01@openssh.com'
    assert result.get("CRYPTO_POLICY") == '-oCiphers=aes256-gcm@openssh.com,3des-cbc -oMACs=umac-128-etm@openssh.com,hmac-sha1-etm@openssh.com -oGSSAPIKexAlgorithms=gss-gex-sha1-,gss-group14-sha1- -oKexAlgorithms=curve25519-sha256@libssh.org,ecdh-sha2-nistp256,ecdh-sha2-nistp384,ecdh-sha2-nistp521,diffie-hellman-group-exchange-sha256,diffie-hellman-group14-sha256,diffie-hellman-group16-sha512,diffie-hellman-group18-sha512,diffie-hellman-group-exchange-sha1,diffie-hellman-group14-sha1 -oHostKeyAlgorithms=ssh-rsa,ssh-rsa-cert-v01@openssh.com,ssh-dss,ssh-dss-cert-v01@openssh.com,rsa-sha2-256,ecdsa-sha2-nistp256,ecdsa-sha2-nistp256-cert-v01@openssh.com,ecdsa-sha2-nistp384,ecdsa-sha2-nistp384-cert-v01@openssh.com,rsa-sha2-512,ecdsa-sha2-nistp521,ecdsa-sha2-nistp521-cert-v01@openssh.com,ssh-ed25519,ssh-ed25519-cert-v01@openssh.com -oPubkeyAcceptedKeyTypes=ssh-rsa,ssh-rsa-cert-v01@openssh.com,ssh-dss,ssh-dss-cert-v01@openssh.com,rsa-sha2-256,ecdsa-sha2-nistp256,ecdsa-sha2-nistp256-cert-v01@openssh.com,ecdsa-sha2-nistp384,ecdsa-sha2-nistp384-cert-v01@openssh.com,rsa-sha2-512,ecdsa-sha2-nistp521,ecdsa-sha2-nistp521-cert-v01@openssh.com,ssh-ed25519,ssh-ed25519-cert-v01@openssh.com'
    assert result.get("OPTIONS1") is None
    assert "OPTIONS1" not in result
    assert "CRYPTO_POLICY" in result
    assert result.options == {"Ciphers": "aes256-gcm@openssh.com,3des-cbc",
                              "MACs": "umac-128-etm@openssh.com,hmac-sha1-etm@openssh.com",
                              "GSSAPIKexAlgorithms": "gss-gex-sha1-,gss-group14-sha1-",
                              "KexAlgorithms": "curve25519-sha256@libssh.org,ecdh-sha2-nistp256,ecdh-sha2-nistp384,ecdh-sha2-nistp521,diffie-hellman-group-exchange-sha256,diffie-hellman-group14-sha256,diffie-hellman-group16-sha512,diffie-hellman-group18-sha512,diffie-hellman-group-exchange-sha1,diffie-hellman-group14-sha1",
                              "HostKeyAlgorithms": "ssh-rsa,ssh-rsa-cert-v01@openssh.com,ssh-dss,ssh-dss-cert-v01@openssh.com,rsa-sha2-256,ecdsa-sha2-nistp256,ecdsa-sha2-nistp256-cert-v01@openssh.com,ecdsa-sha2-nistp384,ecdsa-sha2-nistp384-cert-v01@openssh.com,rsa-sha2-512,ecdsa-sha2-nistp521,ecdsa-sha2-nistp521-cert-v01@openssh.com,ssh-ed25519,ssh-ed25519-cert-v01@openssh.com",
                              "PubkeyAcceptedKeyTypes": "ssh-rsa,ssh-rsa-cert-v01@openssh.com,ssh-dss,ssh-dss-cert-v01@openssh.com,rsa-sha2-256,ecdsa-sha2-nistp256,ecdsa-sha2-nistp256-cert-v01@openssh.com,ecdsa-sha2-nistp384,ecdsa-sha2-nistp384-cert-v01@openssh.com,rsa-sha2-512,ecdsa-sha2-nistp521,ecdsa-sha2-nistp521-cert-v01@openssh.com,ssh-ed25519,ssh-ed25519-cert-v01@openssh.com"
                              }


def test_crypto_policies_opensshserver_3():
    result = CryptoPoliciesOpensshserver(context_wrap(CPSSHD_3))
    assert result["Ciphers"] == "aes256-gcm@openssh.com,chacha20-poly1305@openssh.com,aes256-ctr,aes128-gcm@openssh.com,aes128-ctr"
    assert result.get("OPTIONS1") is None
    assert "OPTIONS1" not in result
    assert "MACs" in result
    assert result.options == {"Ciphers": "aes256-gcm@openssh.com,chacha20-poly1305@openssh.com,aes256-ctr,aes128-gcm@openssh.com,aes128-ctr",
                              "MACs": "hmac-sha2-256-etm@openssh.com,hmac-sha1-etm@openssh.com,umac-128-etm@openssh.com,hmac-sha2-512-etm@openssh.com,hmac-sha2-256,hmac-sha1,umac-128@openssh.com,hmac-sha2-512",
                              "GSSAPIKexAlgorithms": "gss-curve25519-sha256-,gss-nistp256-sha256-,gss-group14-sha256-,gss-group16-sha512-",
                              "CASignatureAlgorithms": "ecdsa-sha2-nistp256,sk-ecdsa-sha2-nistp256@openssh.com,ecdsa-sha2-nistp384,ecdsa-sha2-nistp521,ssh-ed25519,sk-ssh-ed25519@openssh.com,rsa-sha2-256,rsa-sha2-512",
                              "RequiredRSASize": "2048"
                              }


def test_crypto_policies_opensshserver_empty():
    with pytest.raises(SkipComponent):
        CryptoPoliciesOpensshserver(context_wrap(""))
