import doctest

from insights.parsers import smartpdc_settings
from insights.parsers.smartpdc_settings import SmartpdcSettings
from insights.tests import context_wrap

SMARTPDC_SETTINGS = """
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


def test_smartpdc_settings():
    smartpdc_settings = SmartpdcSettings(context_wrap(SMARTPDC_SETTINGS))
    assert smartpdc_settings.data[':listen'] == '0.0.0.0'
    assert ("/etc/foreman-proxy/foreman_ssl_ca.pem" in smartpdc_settings.data[':foreman_ssl_ca']) is True


def test_ls_smartpdc_settings_doc_examples():
    env = {
        'smartpdc_settings': SmartpdcSettings(context_wrap(SMARTPDC_SETTINGS)),
    }
    failed, total = doctest.testmod(smartpdc_settings, globs=env)
    assert failed == 0
