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

CUSTOM_HIERA_CONFIG_2 = """
---
# This YAML file lets you set your own custom configuration in Hiera for the
# installer puppet modules that might not be exposed to users directly through
# installer arguments.
#
# For example, to set 'TraceEnable Off' in Apache, a common requirement for
# security auditors, add this to this file:
#
#   apache::trace_enable: Off
#
# Consult the full module documentation on http://forge.puppetlabs.com,
# or the actual puppet classes themselves, to discover options to configure.
#
# Do note, setting some values may have unintended consequences that affect the
# performance or functionality of the application. Consider the impact of your
# changes before applying them, and test them in a non-production environment
# first.
#
# Here are some examples of how you tune the Apache options if needed:
#
# apache::mod::prefork::startservers: 8

"""


def test_custom_hiera():
    result = satellite_installer_configurations.CustomHiera(context_wrap(CUSTOM_HIERA_CONFIG))
    assert result.data['mongodb::server::config_data']['storage.wiredTiger.engineConfig.cacheSizeGB'] == 8
    assert result.data['apache::mod::prefork::startservers'] == 10
    assert result.data['apache::mod::prefork::maxclients'] == 582

    result = satellite_installer_configurations.CustomHiera(context_wrap(CUSTOM_HIERA_CONFIG_2))
    assert result.data is None


def test_doc():
    env = {
        'custom_hiera': satellite_installer_configurations.CustomHiera(context_wrap(CUSTOM_HIERA_CONFIG))
    }
    failed, total = doctest.testmod(satellite_installer_configurations, globs=env)
    assert failed == 0
