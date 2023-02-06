import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import libssh_config
from insights.parsers.libssh_config import LibsshConfig
from insights.tests import context_wrap

CLIENT_CONFIG = """
# Parse system-wide crypto configuration file
Include /etc/crypto-policies/back-ends/libssh.config
# Parse OpenSSH configuration file for consistency
Include /etc/ssh/ssh_config
""".strip()

SERVER_CONFIG = """
# Parse system-wide crypto configuration file
Include /etc/crypto-policies/back-ends/libssh.config
# Parse OpenSSH configuration file for consistency
Include /etc/ssh/sshd_config
""".strip()


def test_config_no_data():
    with pytest.raises(SkipComponent):
        LibsshConfig(context_wrap(""))


def test_constructor():
    result = LibsshConfig(context_wrap(CLIENT_CONFIG))

    assert 'Include' in result
    assert len(result['Include']) == 2
    assert result['Include'][0] == '/etc/crypto-policies/back-ends/libssh.config'
    assert result['Include'][1] == '/etc/ssh/ssh_config'


def test_doc_examples():
    env = {
        "config": LibsshConfig(context_wrap(SERVER_CONFIG)),
    }
    failed, total = doctest.testmod(libssh_config, globs=env)
    assert failed == 0
