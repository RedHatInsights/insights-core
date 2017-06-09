from insights.parsers.foreman_proxy_conf import ForemanProxyConf
from insights.tests import context_wrap

conf_content = """
---
### File managed with puppet ###
## Module:           'foreman_proxy'

:settings_directory: /etc/foreman-proxy/settings.d

# SSL Setup

# if enabled, all communication would be verfied via SSL
# NOTE that both certificates need to be signed by the same CA in order for this to work
# see http://theforeman.org/projects/smart-proxy/wiki/SSL for more information
:ssl_ca_file: /etc/foreman-proxy/ssl_ca.pem
:ssl_certificate: /etc/foreman-proxy/ssl_cert.pem
:ssl_private_key: /etc/foreman-proxy/ssl_key.pem

# the hosts which the proxy accepts connections from
# commenting the following lines would mean every verified SSL connection allowed
:trusted_hosts:
 - xxx-eopv.xxx.com
 - xxx-eopv.xxx.com

# Endpoint for reverse communication
:foreman_url: https://xxx-eopv.xxx.com
""".strip()


def test_settings_yml():
    result = ForemanProxyConf(context_wrap(conf_content))
    assert result.data[':settings_directory'] == '/etc/foreman-proxy/settings.d'
    assert result.data[':ssl_ca_file'] == '/etc/foreman-proxy/ssl_ca.pem'
    assert result.data[':ssl_private_key'] == '/etc/foreman-proxy/ssl_key.pem'
    assert result.data[':foreman_url'] == 'https://xxx-eopv.xxx.com'
    assert result.data[':trusted_hosts'] == ['xxx-eopv.xxx.com', 'xxx-eopv.xxx.com']
    assert "xxx-eopv.xxx.com" in result.data[':trusted_hosts']
