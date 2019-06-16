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
def test_url_guess_legacy(get_proxies, init_session):
    """
    Connection should guess the right URLs if there's nothing in the config (the default)
    """
    config = Mock(base_url=None, upload_url=None, legacy_upload=True, insecure_connection=False, analyze_container=False)

    connection = InsightsConnection(config)
    assert connection.base_url == 'https://cert-api.access.redhat.com/r/insights'
    assert connection.upload_url == 'https://cert-api.access.redhat.com/r/insights/uploads'


@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_url_guess_platform(get_proxies, init_session):
    """
    Connection should guess the right URLs if there's nothing in the config (the default)
    """
    config = Mock(base_url=None, upload_url=None, legacy_upload=False, insecure_connection=False)

    connection = InsightsConnection(config)
    # assert connection.base_url == 'https://cloud.redhat.com/api'
    assert connection.base_url == 'https://cert-api.access.redhat.com/r/insights/platform'
    # assert connection.upload_url == 'https://cloud.redhat.com/api/ingress/v1/upload'
    assert connection.upload_url == 'https://cert-api.access.redhat.com/r/insights/platform/ingress/v1/upload'


@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_branch_info_url_guess_legacy(get_proxies, init_session):
    """
    Satellite branch info URL should be set properly
    """
    config = Mock(base_url='sat.test.com:443/redhat_access/r/insights', upload_url=None, legacy_upload=True, insecure_connection=False, branch_info_url=None)

    connection = InsightsConnection(config)
    assert connection.branch_info_url == 'https://sat.test.com:443/redhat_access/r/insights/v1/branch_info'


@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_branch_info_url_guess_platform(get_proxies, init_session):
    """
    Satellite branch info URL should be the same on platform as on legacy
    """
    config = Mock(base_url='sat.test.com:443/redhat_access/r/insights', upload_url=None, legacy_upload=False, insecure_connection=False, branch_info_url=None)

    connection = InsightsConnection(config)
    assert connection.branch_info_url == 'https://sat.test.com:443/redhat_access/r/insights/v1/branch_info'
