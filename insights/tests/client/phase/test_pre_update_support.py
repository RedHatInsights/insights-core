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
                       "return_value.load_all.return_value.support": True})
    return patcher(old_function)


def patch_insights_client(old_function):
    patcher = patch("insights.client.phase.v1.InsightsClient")
    return patcher(old_function)


def patch_insights_support(old_function):
    patcher = patch("insights.client.phase.v1.InsightsSupport")
    return patcher(old_function)


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
