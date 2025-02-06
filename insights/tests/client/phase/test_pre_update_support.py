# -*- coding: UTF-8 -*-

from insights.client.constants import InsightsConstants
from insights.client.phase.v1 import pre_update
from mock.mock import patch
from pytest import raises, mark


def patch_insights_config(old_function):
    patcher = patch("insights.client.phase.v1.InsightsConfig",
                    **{"return_value.load_all.return_value.auto_config": False,
                       "return_value.load_all.return_value.version": False,
                       "return_value.load_all.return_value.validate": False,
                       "return_value.load_all.return_value.enable_schedule": False,
                       "return_value.load_all.return_value.disable_schedule": False,
                       "return_value.load_all.return_value.analyze_container": False,
                       "return_value.load_all.return_value.test_connection": False,
                       "return_value.load_all.return_value.support": True})
    return patcher(old_function)


def patch_insights_client(old_function):
    patcher = patch("insights.client.phase.v1.InsightsClient")
    return patcher(old_function)


def patch_insights_support(old_function):
    patcher = patch("insights.client.phase.v1.InsightsSupport")
    return patcher(old_function)


@mark.skip(reason="Mock errors in QE Jenkins")
@patch_insights_support
@patch_insights_client
@patch_insights_config
def test_support_called(insights_config, insights_client, insights_support):
    """
    InsightsSupport is constructed with InsightsConfig and collect_support_info is called.
    """
    try:
        pre_update()
    except SystemExit:
        pass

    insights_support.assert_called_once_with(insights_config.return_value.load_all.return_value)
    insights_support.return_value.collect_support_info.assert_called_once_with()


@mark.skip(reason="Mock errors in QE Jenkins")
@patch_insights_support
@patch_insights_client
@patch_insights_config
def test_exit_ok(insights_config, insights_client, insights_support):
    """
    Support collection replaces the normal client run.
    """
    with raises(SystemExit) as exc_info:
        pre_update()

    assert exc_info.value.code == InsightsConstants.sig_kill_ok


@patch("insights.client.phase.v1.logger")
@patch("insights.client.utilities._get_rhsm_identity", return_value=None)
@patch_insights_client
@patch_insights_config
def test_no_rhsm(insights_config, insights_client, _get_rhsm_identity, logger):
    """
    Exit with an error if the host is not registered with RHSM.
    """
    with raises(SystemExit) as exc_info:
        pre_update()

    logger.error.assert_called_once_with('This host has not yet been registered, please ensure '
                                         'that the system is registered with subscription-manager '
                                         'and then with insights-client.\n'
                                         '\n1. Register with subscription-manager'
                                         '\n# subscription-manager register\n'
                                         '\n2. Register with insights-client'
                                         '\n# insights-client --register')
    assert exc_info.value.code == InsightsConstants.sig_kill_bad
