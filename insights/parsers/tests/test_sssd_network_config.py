from insights.tests import context_wrap
from insights.parsers.sssd_network_config import SSSDNetworkConfig
from insights.parsers import sssd_network_config, SkipException
import doctest
import pytest


SSSD_NETWORK_CONFIG = """
[Unit]
Before=systemd-user-sessions.service nss-user-lookup.target
After=network-online.target
Wants=nss-user-lookup.target
"""


def test_sssd_network_config():
    conf = sssd_network_config.SSSDNetworkConfig(context_wrap(SSSD_NETWORK_CONFIG))
    assert conf.has_option('Unit', 'Before') is True
    assert conf.get('Unit', 'Before') == 'systemd-user-sessions.service nss-user-lookup.target'
    assert conf.get('Unit', 'After') == 'network-online.target'
    assert conf.get('Unit', 'Wants') == 'nss-user-lookup.target'


def test_sssd_network_config_empty():
    with pytest.raises(SkipException):
        assert sssd_network_config.SSSDNetworkConfig(context_wrap('')) is None


def test_sssd_network_config_doc_examples():
    env = {
        'sssd_network_config_obj': SSSDNetworkConfig(context_wrap(SSSD_NETWORK_CONFIG)),
    }
    failed, total = doctest.testmod(sssd_network_config, globs=env)
    assert failed == 0
