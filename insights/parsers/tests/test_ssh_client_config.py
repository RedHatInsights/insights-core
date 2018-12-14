import doctest

from insights.parsers import ssh_client_config
from insights.tests import context_wrap

SSH_CONFIG_INPUT = """
        #   ProxyCommand ssh -q -W %h:%p gateway.example.com
        #   RekeyLimit 1G 1h
        #
        # Uncomment this if you want to use .local domain
        # Host *.local
        #   CheckHostIP no
        ProxyCommand ssh -q -W %h:%p gateway.example.com

        Host *
            GSSAPIAuthentication yes
        # If this option is set to yes then remote X11 clients will have full access
        # to the original X11 display. As virtually no X11 client supports the untrusted
        # mode correctly we set this to yes.
            ForwardX11Trusted yes
        # Send locale-related environment variables
            SendEnv LANG LC_CTYPE LC_NUMERIC LC_TIME LC_COLLATE LC_MONETARY LC_MESSAGES
            SendEnv LC_PAPER LC_NAME LC_ADDRESS LC_TELEPHONE LC_MEASUREMENT
            SendEnv LC_IDENTIFICATION LC_ALL LANGUAGE
            SendEnv XMODIFIERS

        Host proxytest
            HostName 192.168.122.2
"""


def test_ssh_client_config():
    etcsshconfig = ssh_client_config.EtcSshConfig(context_wrap(SSH_CONFIG_INPUT))
    assert len(etcsshconfig.global_lines) == 1
    assert ('Host_*' in etcsshconfig.host_lines) is True
    assert etcsshconfig.host_lines['Host_*'][0].keyword == 'GSSAPIAuthentication'
    assert etcsshconfig.host_lines['Host_proxytest'][0].value == '192.168.122.2'
    foremansshconfig = ssh_client_config.ForemanSshConfig(context_wrap(SSH_CONFIG_INPUT))
    assert len(foremansshconfig.global_lines) == 1
    assert ('Host_*' in foremansshconfig.host_lines) is True
    assert foremansshconfig.host_lines['Host_*'][0].keyword == 'GSSAPIAuthentication'
    assert foremansshconfig.host_lines['Host_proxytest'][0].value == '192.168.122.2'


def test_ssh_client_config_docs():
    env = {
        'etcsshconfig': ssh_client_config.EtcSshConfig(context_wrap(SSH_CONFIG_INPUT)),
        'foremansshconfig': ssh_client_config.ForemanSshConfig(context_wrap(SSH_CONFIG_INPUT))
    }
    failed, total = doctest.testmod(ssh_client_config, globs=env)
    assert failed == 0
