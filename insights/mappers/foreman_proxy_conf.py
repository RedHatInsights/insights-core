"""
foreman_proxy_conf - Files /etc/foreman-proxy/settings.yml
==========================================================

This module provides parsing for FOREMAN-PROXY configuration files.
``ForemanProxyConf`` is a mapper for ``/etc/foreman-proxy/settings.yml`` files.

Typical output of the ``foreman_proxy_conf`` is::

    # Comment line
    :settings_directory: /etc/foreman-proxy/settings.d
    :ssl_ca_file: /etc/foreman-proxy/ssl_ca.pem
    :ssl_certificate: /etc/foreman-proxy/ssl_cert.pem
    :ssl_private_key: /etc/foreman-proxy/ssl_key.pem
    :trusted_hosts:
      - xxx.m2m.xxx
      - xxx.m2m.xxx
    :foreman_url: https://xxx.m2m.xxx

Note:
    The examples in this module may be executed with the following command:

    ``python -m insights.mappers.foreman_proxy_conf``

Examples:
    >>> settings_yml_input_data = '''
    ... # Comment line
    ... :settings_directory: /etc/foreman-proxy/settings.d
    ... :ssl_ca_file: /etc/foreman-proxy/ssl_ca.pem
    ... :ssl_certificate: /etc/foreman-proxy/ssl_cert.pem
    ... :ssl_private_key: /etc/foreman-proxy/ssl_key.pem
    ... :trusted_hosts:
    ...   - xxx.m2m.xxx
    ...   - xxx.m2m.xxx
    ... :foreman_url: https://xxx.m2m.xxx
    ... '''.strip()
    >>> from insights.tests import context_wrap
    >>> setting_dic = ForemanProxyConf(context_wrap(settings_yml_input_data, path='/etc/foreman-proxy/settings.yml'))
    >>> setting_dic.data[':settings_directory']
    '/etc/foreman-proxy/settings.d'
    >>> setting_dic.data[':ssl_ca_file']
    '/etc/foreman-proxy/ssl_ca.pem'
    >>> setting_dic.data[':ssl_private_key']
    '/etc/foreman-proxy/ssl_key.pem'
    >>> setting_dic.data[':foreman_url']
    'https://xxx.m2m.xxx'
    >>> setting_dic.data[':trusted_hosts']
    ['xxx.m2m.xxx', 'xxx.m2m.xxx']
    >>> "xxx.m2m.xxx" in setting_dic.data[':trusted_hosts']
    True
"""
from .. import YAMLMapper, mapper


@mapper('foreman_proxy_conf')
class ForemanProxyConf(YAMLMapper):
    """ Class for parsing the content of ``foreman_proxy_conf``."""
    pass
