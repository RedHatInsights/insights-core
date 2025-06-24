# -*- coding: UTF-8 -*-
try:
    from unittest.mock import patch
except Exception:
    from mock import patch

from insights.client.client import collect
from insights.client.config import InsightsConfig
from insights.client.utilities import determine_hostname


def patch_get_rm_conf():
    """
    Mocks InsightsUploadConf.get_rm_conf so it returns a fixed configuration.
    """

    def decorator(old_function):
        patcher = patch("insights.client.client.InsightsUploadConf.get_rm_conf")
        return patcher(old_function)

    return decorator


def patch_core_collector():
    """
    Replaces CoreCollector with a dummy mock.
    """

    def decorator(old_function):
        patcher = patch("insights.client.client.CoreCollector")
        return patcher(old_function)

    return decorator


@patch_core_collector()
@patch_get_rm_conf()
@patch('insights.client.client.logger')
def test_log_msgs_general(log, get_rm_conf, core_collector):
    config = InsightsConfig()
    collect(config)
    get_rm_conf.assert_called_once_with()
    log.info.assert_called_once_with(
        'Starting to collect Insights data for %s' % determine_hostname(config.display_name)
    )


@patch_core_collector()
@patch_get_rm_conf()
@patch('insights.client.client.logger')
def test_log_msgs_compliance(log, get_rm_conf, core_collector):
    config = InsightsConfig(compliance=True)
    collect(config)
    get_rm_conf.assert_called_once_with()
    log.info.assert_called_once_with(
        'Starting to collect Insights data for %s' % determine_hostname(config.display_name)
    )


@patch_core_collector()
@patch_get_rm_conf()
@patch('insights.client.client.logger')
def test_log_msgs_compliance_policies(log, get_rm_conf, core_collector):
    config = InsightsConfig(compliance_policies=True)
    collect(config)
    get_rm_conf.assert_not_called()
    log.info.assert_not_called()


@patch_core_collector()
@patch_get_rm_conf()
@patch('insights.client.client.logger')
def test_log_msgs_compliance_assign(log, get_rm_conf, core_collector):
    config = InsightsConfig(compliance_assign=['abc'])
    collect(config)
    get_rm_conf.assert_not_called()
    log.info.assert_not_called()


@patch_core_collector()
@patch_get_rm_conf()
@patch('insights.client.client.logger')
def test_log_msgs_compliance_unassign(log, get_rm_conf, core_collector):
    config = InsightsConfig(compliance_unassign=['abc'])
    collect(config)
    get_rm_conf.assert_not_called()
    log.info.assert_not_called()
