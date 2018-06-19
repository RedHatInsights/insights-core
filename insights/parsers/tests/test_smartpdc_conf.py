import doctest

from insights.parsers import smartpdc_conf
from insights.parsers.smartpdc_conf import SmartpdcConf
from insights.tests import context_wrap

SMARTPDC_CONF = """
# Path to dynflow database, leave blank for in-memory non-persistent database
:database:
:console_auth: true

# URL of the foreman, used for reporting back
:foreman_url: https://test.example.com

# SSL settings for client authentication against foreman.
:foreman_ssl_ca: /etc/foreman-proxy/foreman_ssl_ca.pem
:foreman_ssl_cert: /etc/foreman-proxy/foreman_ssl_cert.pem
:foreman_ssl_key: /etc/foreman-proxy/foreman_ssl_key.pem

# Listen on address
:listen: 0.0.0.0

# Listen on port
:port: 8008

:use_https: true
:ssl_ca_file: /etc/foreman-proxy/ssl_ca.pem
"""


def test_smartpdc_conf():
    smartpdc_conf = SmartpdcConf(context_wrap(SMARTPDC_CONF))
    assert smartpdc_conf.data[':listen'] == '0.0.0.0'
    print "/etc/foreman-proxy/foreman_ssl_ca.pem" in smartpdc_conf.data[':foreman_ssl_ca']
    assert ("/etc/foreman-proxy/foreman_ssl_ca.pem" in smartpdc_conf.data[':foreman_ssl_ca']) is True


def test_ls_smartpdc_conf_doc_examples():
    env = {
        'smartpdc_conf': SmartpdcConf(context_wrap(SMARTPDC_CONF)),
    }
    failed, total = doctest.testmod(smartpdc_conf, globs=env)
    assert failed == 0
