from insights.parsers import satellite_installer_configurations
from insights.tests import context_wrap
import doctest

CUSTOM_HIERA_CONFIG = """
mongodb::server::config_data:
  storage.wiredTiger.engineConfig.cacheSizeGB: 8
apache::mod::prefork::serverlimit: 582
apache::mod::prefork::maxclients: 582
apache::mod::prefork::startservers: 10
"""


def test_custom_hiera():
    result = satellite_installer_configurations.CustomHiera(context_wrap(CUSTOM_HIERA_CONFIG))
    assert result.data['mongodb::server::config_data']['storage.wiredTiger.engineConfig.cacheSizeGB'] == 8
    assert result.data['apache::mod::prefork::startservers'] == 10
    assert result.data['apache::mod::prefork::maxclients'] == 582


def test_doc():
    env = {
        'custom_hiera': satellite_installer_configurations.CustomHiera(context_wrap(CUSTOM_HIERA_CONFIG))
    }
    failed, total = doctest.testmod(satellite_installer_configurations, globs=env)
    assert failed == 0
