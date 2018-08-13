# -*- coding: UTF-8 -*-

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
