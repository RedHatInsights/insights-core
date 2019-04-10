from insights.parsers.ssh import SshDConfig
from insights.tests import context_wrap

SSHD_CONFIG_INPUT = """
#	$OpenBSD: sshd_config,v 1.93 2014/01/10 05:59:19 djm Exp $

Port 22
#AddressFamily any
ListenAddress 10.110.0.1
Port 22
ListenAddress 10.110.1.1
#ListenAddress ::
# AllowUsers
AllowUsers
# The default requires explicit activation of protocol 1
#Protocol 2
Protocol 1
""".strip()


def test_sshd_config():
    sshd_config = SshDConfig(context_wrap(SSHD_CONFIG_INPUT))
    assert sshd_config is not None
    assert 'Port' in sshd_config
    assert 'PORT' in sshd_config
    assert sshd_config['port'] == ['22', '22']
    assert 'ListenAddress' in sshd_config
    assert sshd_config['ListenAddress'] == ['10.110.0.1', '10.110.1.1']
    assert sshd_config.last('ListenAddress') == '10.110.1.1'
    assert sshd_config['Protocol'] == ['1']
    assert 'AddressFamily' not in sshd_config
    ports = [l for l in sshd_config if l.keyword == 'Port']
    assert len(ports) == 2
    assert ports[0].value == '22'
    assert sshd_config.last('ListenAddress') == '10.110.1.1'


SSHD_CONFIG_COMPLETE = """
# Standard /etc/ssh/sshd_config without comments and blank lines
HostKey /etc/ssh/ssh_host_rsa_key
HostKey /etc/ssh/ssh_host_ecdsa_key
HostKey /etc/ssh/ssh_host_ed25519_key
SyslogFacility AUTHPRIV
AuthorizedKeysFile	.ssh/authorized_keys
PasswordAuthentication=yes
ChallengeResponseAuthentication no
GSSAPIAuthentication yes
GSSAPICleanupCredentials no
UsePAM yes
X11Forwarding = "yes"
UsePrivilegeSeparation sandbox		# Default for new installations.
AcceptEnv LANG LC_CTYPE LC_NUMERIC LC_TIME LC_COLLATE LC_MONETARY LC_MESSAGES
AcceptEnv LC_PAPER LC_NAME LC_ADDRESS LC_TELEPHONE LC_MEASUREMENT
AcceptEnv LC_IDENTIFICATION LC_ALL LANGUAGE
AcceptEnv XMODIFIERS
Subsystem	sftp	/usr/libexec/openssh/sftp-server
APlusOption only,the,last,shall,be,taken,in,account,by,does_line_user_plus()
APlusOption +val1,val2,val3
"""


def test_sshd_config_complete():
    config = SshDConfig(context_wrap(SSHD_CONFIG_COMPLETE))
    assert config is not None
    assert 'HostKey' in config
    hostkeys = config.get('HostKey')
    assert len(hostkeys) == 3
    for hostkey in hostkeys:
        assert hostkey.keyword == 'HostKey'
        assert hostkey.kw_lower == 'hostkey'
    assert hostkeys[0].value == '/etc/ssh/ssh_host_rsa_key'
    assert hostkeys[1].value == '/etc/ssh/ssh_host_ecdsa_key'
    assert hostkeys[2].value == '/etc/ssh/ssh_host_ed25519_key'
    assert hostkeys[0].line == 'HostKey /etc/ssh/ssh_host_rsa_key'
    assert hostkeys[1].line == 'HostKey /etc/ssh/ssh_host_ecdsa_key'
    assert hostkeys[2].line == 'HostKey /etc/ssh/ssh_host_ed25519_key'
    assert config['HostKey'] == [
        '/etc/ssh/ssh_host_rsa_key',
        '/etc/ssh/ssh_host_ecdsa_key',
        '/etc/ssh/ssh_host_ed25519_key'
    ]
    assert config.last('UsePAM') == 'yes'
    assert config.last('ClientAliveInterval') is None
    assert config.last('ClientAliveCountMax', '0') == '0'
    assert config.get_line('UsePAM') == 'UsePAM yes'
    assert config['PasswordAuthentication'] == ['yes']
    assert config['X11Forwarding'] == ['yes']
    assert config.get_line('ClientAliveInterval') == 'ClientAliveInterval   # Implicit default'
    assert config.get_line('ClientAliveCountMax', '0') == 'ClientAliveCountMax 0  # Implicit default'
    assert config.get_values('SyslogFacility') == ['AUTHPRIV']
    assert config.get_values('SyslogFacility', join_with='') == 'AUTHPRIV'
    assert config.get_values('ClientAliveInterval', default='') == ['']
    assert config.get_values('HostKey', default='no_key', join_with=' ') == \
        '/etc/ssh/ssh_host_rsa_key /etc/ssh/ssh_host_ecdsa_key /etc/ssh/ssh_host_ed25519_key'
    # Splitting does not occur if joining has not occurred:
    assert config.get_values('HostKey', default='no_key', split_on='/') == [
        '/etc/ssh/ssh_host_rsa_key',
        '/etc/ssh/ssh_host_ecdsa_key',
        '/etc/ssh/ssh_host_ed25519_key'
    ]
    assert config.get_values('AcceptEnv', join_with=' ', split_on=' ') == [
        'LANG', 'LC_CTYPE', 'LC_NUMERIC', 'LC_TIME', 'LC_COLLATE',
        'LC_MONETARY', 'LC_MESSAGES', 'LC_PAPER', 'LC_NAME', 'LC_ADDRESS',
        'LC_TELEPHONE', 'LC_MEASUREMENT', 'LC_IDENTIFICATION', 'LC_ALL',
        'LANGUAGE', 'XMODIFIERS'
    ]
    assert config.line_uses_plus("APlusOption") is True
    assert config.line_uses_plus("Subsystem") is False
    assert config.line_uses_plus("AcceptEnv") is False
    assert config.line_uses_plus("NonExistingOption") is None
