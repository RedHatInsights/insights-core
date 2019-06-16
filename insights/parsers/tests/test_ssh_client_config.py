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

import doctest
import pytest
from insights.parsers import ssh_client_config as scc, SkipException
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

SSH_CONFIG_INPUT_EMPTY = """
#   ProxyCommand ssh -q -W %h:%p gateway.example.com
#   RekeyLimit 1G 1h
#
# Uncomment this if you want to use .local domain
# Host *.local
#   CheckHostIP no
# If this option is set to yes then remote X11 clients will have full access
# to the original X11 display. As virtually no X11 client supports the untrusted
# mode correctly we set this to yes.
# Send locale-related environment variables
"""


def test_ssh_client_config():
    etcsshconfig = scc.EtcSshConfig(context_wrap(SSH_CONFIG_INPUT))
    assert len(etcsshconfig.global_lines) == 1
    assert ('Host_*' in etcsshconfig.host_lines) is True
    assert etcsshconfig.host_lines['Host_*'][0].keyword == 'GSSAPIAuthentication'
    assert etcsshconfig.host_lines['Host_proxytest'][0].value == '192.168.122.2'
    foremansshconfig = scc.ForemanSshConfig(context_wrap(SSH_CONFIG_INPUT))
    assert len(foremansshconfig.global_lines) == 1
    assert ('Host_*' in foremansshconfig.host_lines) is True
    assert foremansshconfig.host_lines['Host_*'][0].keyword == 'GSSAPIAuthentication'
    assert foremansshconfig.host_lines['Host_proxytest'][0].value == '192.168.122.2'


def test_ssh_config_AB():
    with pytest.raises(SkipException):
        scc.ForemanProxySshConfig(context_wrap(SSH_CONFIG_INPUT_EMPTY))


def test_ssh_client_config_docs():
    env = {
        'etcsshconfig': scc.EtcSshConfig(context_wrap(SSH_CONFIG_INPUT)),
        'foremansshconfig': scc.ForemanSshConfig(context_wrap(SSH_CONFIG_INPUT)),
        'foreman_proxy_ssh_config': scc.ForemanProxySshConfig(context_wrap(SSH_CONFIG_INPUT))
    }
    failed, total = doctest.testmod(scc, globs=env)
    assert failed == 0
