# -*- coding: UTF-8 -*-

from insights.client.constants import InsightsConstants
from insights.client.phase.v1 import pre_update
from mock.mock import patch
from pytest import raises


def patch_insights_config(old_function):
    patcher = patch("insights.client.phase.v1.InsightsConfig",
                    **{"return_value.load_all.return_value.auto_config": False,
                       "return_value.load_all.return_value.version": False,
                       "return_value.load_all.return_value.validate": False,
                       "return_value.load_all.return_value.enable_schedule": False,
                       "return_value.load_all.return_value.disable_schedule": False,
                       "return_value.load_all.return_value.analyze_container": False,
                       "return_value.load_all.return_value.test_connection": False,
                       "return_value.load_all.return_value.support": False,
                       "return_value.load_all.return_value.diagnosis": False,
                       "return_value.load_all.return_value.checkin": True})
    return patcher(old_function)


@patch("insights.client.phase.v1.InsightsClient", **{"return_value.checkin.return_value": True})
@patch_insights_config
def test_checkin_success(insights_config, insights_client):
    """
    InsightsSupport is constructed with InsightsConfig and collect_support_info is called.
    """
    with raises(SystemExit) as exc_info:
        pre_update()

    insights_client.return_value.checkin.assert_called_once_with()
    assert exc_info.value.code == InsightsConstants.sig_kill_ok


@patch("insights.client.phase.v1.InsightsClient", **{"return_value.checkin.return_value": False})
@patch_insights_config
def test_checkin_failure(insights_config, insights_client):
    """
    Support collection replaces the normal client run.
    """
    with raises(SystemExit) as exc_info:
        pre_update()

    insights_client.return_value.checkin.assert_called_once_with()
    assert exc_info.value.code == InsightsConstants.sig_kill_bad
