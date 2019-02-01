# -*- coding: UTF-8 -*-

from insights.client.config import InsightsConfig
from insights.client.support import InsightsSupport
from mock.mock import Mock, patch


@patch("insights.client.support.subprocess")
@patch("insights.client.support.InsightsSupport._support_diag_dump")
def test_collect_support_info_support_diag_dump(support_diag_dump, subprocess):
    """
    collect_suppport_info_method callse _support_diag_dump method.
    """
    config = Mock()
    support = InsightsSupport(config)
    support.collect_support_info()

    support_diag_dump.assert_called_once_with()


@patch("insights.client.support.os.statvfs", **{"return_value.f_bavail": 1, "return_value.f_frsize": 1})
@patch("insights.client.support.Popen", **{"return_value.communicate.return_value": ("", "")})
@patch("insights.client.support.os.path.isfile", return_value=False)
@patch("insights.client.support.registration_check", return_value={})
@patch("insights.client.support.InsightsConnection")
def test_support_diag_dump_insights_connection(insights_connection, registration_check, isfile, popen, statvfs):
    """
    _support_diag_dump method instantiates InsightsConnection with InsightsConfig.
    """
    config = Mock(**{"return_value.auto_config": "", "proxy": ""})
    support = InsightsSupport(config)
    support._support_diag_dump()

    insights_connection.assert_called_once_with(config)


@patch('insights.client.support.InsightsConnection')
@patch('insights.client.support.registration_check')
def test_registration_check_legacy_upload_on(registration_check, InsightsConnection):
    '''
        Check registration when legacy_upload=True
    '''
    config = InsightsConfig(legacy_upload=True)
    support = InsightsSupport(config)
    support.collect_support_info()

    registration_check.assert_called_once()


@patch('insights.client.support.InsightsConnection')
@patch('insights.client.support.registration_check')
def test_skip_registration_check_legacy_upload_off(registration_check, InsightsConnection):
    '''
        Don't check registration when legacy_upload=False
    '''
    config = InsightsConfig(legacy_upload=False)
    support = InsightsSupport(config)
    support.collect_support_info()

    registration_check.assert_not_called()
