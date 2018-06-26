"""
SmartpdcSettings - file ``/etc/smart_proxy_dynflow_core/settings.yml``
======================================================================

This module provides parsing for smart_proxy_dynflow_core settings file.
``SmartpdcSettings`` is a parser for ``/etc/smart_proxy_dynflow_core/settings.yml`` files.

Typical output is::

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

Examples:
    >>> smartpdc_settings.data[':foreman_url']
    'https://test.example.com'
    >>> "/etc/foreman-proxy/foreman_ssl_ca.pem" in smartpdc_settings.data[':foreman_ssl_ca']
    True
"""
from insights.specs import Specs

from .. import YAMLParser, parser


@parser(Specs.smartpdc_settings)
class SmartpdcSettings(YAMLParser):
    """ Class for parsing the content of ``/etc/smart_proxy_dynflow_core/settings.yml``."""
    pass
