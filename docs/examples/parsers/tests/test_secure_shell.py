from insights.parsers.secure_shell import SshDConfig
from insights.parsers import secure_shell
from insights.tests import context_wrap
import doctest

SSHD_CONFIG_INPUT = """
#    $OpenBSD: sshd_config,v 1.93 2014/01/10 05:59:19 djm Exp $

Port 22
#AddressFamily any
ListenAddress 10.110.0.1
Port 22
ListenAddress 10.110.1.1
#ListenAddress ::

# The default requires explicit activation of protocol 1
#Protocol 2
Protocol 1
"""


def test_sshd_config():
    sshd_config = SshDConfig(context_wrap(SSHD_CONFIG_INPUT))
    assert sshd_config is not None
    assert 'Port' in sshd_config
    assert 'PORT' in sshd_config
    assert sshd_config['port'] == ['22', '22']
    assert 'ListenAddress' in sshd_config
    assert sshd_config['ListenAddress'] == ['10.110.0.1', '10.110.1.1']
    assert sshd_config['Protocol'] == ['1']
    assert 'AddressFamily' not in sshd_config
    ports = [l for l in sshd_config if l.keyword == 'Port']
    assert len(ports) == 2
    assert ports[0].value == '22'


def test_sshd_documentation():
    """
    Here we test the examples in the documentation automatically using
    doctest.  We set up an environment which is similar to what a
    rule writer might see - a 'sshd_config' variable that has been
    passed in as a parameter to the rule declaration.  This saves doing
    this setup in the example code.
    """
    env = {
        'sshd_config': SshDConfig(context_wrap(SSHD_CONFIG_INPUT)),
    }
    failed, total = doctest.testmod(secure_shell, globs=env)
    assert failed == 0


SSHD_DOCS_EXAMPLE = '''
Port 22
Port 22
'''


def test_sshd_corner_cases():
    """
    Here we test any corner cases for behaviour we expect to deal with
    in the parser but doesn't make a good example.
    """
    config = SshDConfig(context_wrap(SSHD_DOCS_EXAMPLE))
    assert config.last('AddressFamily') is None
    assert config['AddressFamily'] is None
    ports = [l for l in config if l.keyword == 'Port']
    assert len(ports) == 2
    assert ports[0].value == '22'
