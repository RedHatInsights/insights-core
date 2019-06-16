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

from insights.client.connection import InsightsConnection
from mock.mock import Mock, patch


@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
@patch("insights.client.connection.constants.cached_branch_info", "/tmp/insights-test-cached-branchinfo")
def test_request(get_proxies, init_session):
    """
    The request to get branch info is issued with correct timeout set.
    """
    config = Mock(base_url="www.example.com", branch_info_url="https://www.example.com/branch_info")

    connection = InsightsConnection(config)
    connection.get_branch_info()

    init_session.return_value.get.assert_called_once_with(config.branch_info_url, timeout=config.http_timeout)
