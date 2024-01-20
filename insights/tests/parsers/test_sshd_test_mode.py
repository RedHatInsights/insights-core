import doctest

from insights.parsers import sshd_test_mode
from insights.tests import context_wrap

SSHD_TEST_MODE = """
port 22
addressfamily any
listenaddress [::]:22
listenaddress 0.0.0.0:22
usepam yes
logingracetime 120
x11displayoffset 10
x11maxdisplays 1000
maxauthtries 6
ciphers aes256-gcm@openssh.com,chacha20-poly1305@openssh.com,aes256-ctr,aes128-gcm@openssh.com,aes128-ctr
macs hmac-sha2-256-etm@openssh.com,hmac-sha1-etm@openssh.com,umac-128-etm@openssh.com,hmac-sha2-512-etm@openssh.com,hmac-sha2-256,hmac-sha1,umac-128@openssh.com,hmac-sha2-512
""".strip()


def test_sshd_test_mode():
    sshd_mode = sshd_test_mode.SshdTestMode(context_wrap(SSHD_TEST_MODE))
    assert len(sshd_mode) == 10
    assert sshd_mode.get("listenaddress") == ["[::]:22", "0.0.0.0:22"]
    assert sshd_mode.get("ciphers") == "aes256-gcm@openssh.com,chacha20-poly1305@openssh.com,aes256-ctr,aes128-gcm@openssh.com,aes128-ctr"
    assert ('addressfamily' in sshd_mode) is True
    assert ('test' in sshd_mode) is False


def test_sshd_test_mode_docs():
    env = {
        'sshd_test_mode': sshd_test_mode.SshdTestMode(context_wrap(SSHD_TEST_MODE)),
    }
    failed, total = doctest.testmod(sshd_test_mode, globs=env)
    assert failed == 0
