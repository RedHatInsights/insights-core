# -*- coding: UTF-8 -*-
#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

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
