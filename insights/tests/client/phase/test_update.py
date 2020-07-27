# -*- coding: UTF-8 -*-

from insights.client.phase.v1 import update
from mock.mock import patch
from pytest import raises


@patch("insights.client.phase.v1.InsightsClient")
@patch("insights.client.phase.v1.InsightsConfig")
def test_update_payload_on(insights_config, insights_client):
    """
    Rules are not updated when a payload is uploaded
    """
    insights_config.return_value.load_all.return_value.payload = True
    insights_config.return_value.load_all.return_value.core_collect = False
    try:
        update()
    except SystemExit:
        pass
    insights_client.return_value.update.assert_called_once()
    insights_client.return_value.update_rules.assert_not_called()


@patch("insights.client.phase.v1.InsightsClient")
@patch("insights.client.phase.v1.InsightsConfig")
def test_update_payload_off(insights_config, insights_client):
    """
    Rules are updated in normal operation (no payload)
    """
    insights_config.return_value.load_all.return_value.payload = False
    insights_config.return_value.load_all.return_value.core_collect = False
    try:
        update()
    except SystemExit:
        pass
    insights_client.return_value.update.assert_called_once()
    insights_client.return_value.update_rules.assert_called_once()


@patch("insights.client.phase.v1.InsightsClient")
@patch("insights.client.phase.v1.InsightsConfig")
def test_update_core_collect_on(insights_config, insights_client):
    """
    Rules are not updated when using core collection
    """
    insights_config.return_value.load_all.return_value.payload = False
    insights_config.return_value.load_all.return_value.core_collect = True
    try:
        update()
    except SystemExit:
        pass
    insights_client.return_value.update.assert_called_once()
    insights_client.return_value.update_rules.assert_not_called()


@patch("insights.client.phase.v1.InsightsClient")
@patch("insights.client.phase.v1.InsightsConfig")
def test_update_core_collect_off(insights_config, insights_client):
    """
    Rules are updated when using classic collection
    """
    insights_config.return_value.load_all.return_value.payload = False
    insights_config.return_value.load_all.return_value.core_collect = False
    try:
        update()
    except SystemExit:
        pass
    insights_client.return_value.update.assert_called_once()
    insights_client.return_value.update_rules.assert_called_once()


@patch("insights.client.phase.v1.InsightsClient")
@patch("insights.client.phase.v1.InsightsConfig")
def test_exit_ok(insights_config, insights_client):
    """
    Support collection replaces the normal client run.
    """
    with raises(SystemExit) as exc_info:
        update()
    assert exc_info.value.code == 0
