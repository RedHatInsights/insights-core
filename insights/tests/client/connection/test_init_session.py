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


@patch("insights.client.connection.requests.Session")
@patch("insights.client.connection.InsightsConnection.__init__", return_value=None)
def test_proxy_request(init, session):
    """
    If proxy authentication is enabled, the failing hacky request is issued with correct timeout set.
    """
    config = Mock()

    # The constructor is bypassed, because it itself runs the _init_session method.
    connection = InsightsConnection(None)
    connection.config = config
    connection.user_agent = None
    connection.systemid = None
    connection.authmethod = "BASIC"
    connection.username = "some username"
    connection.password = "some password"
    connection.cert_verify = None
    connection.proxies = {"https": "some proxy"}
    connection.proxy_auth = True
    connection.base_url = 'https://cert-api.access.redhat.com/r/insights'

    connection._init_session()

    session.return_value.request.assert_called_once_with(
        "GET",
        "https://cert-api.access.redhat.com/r/insights",
        timeout=config.http_timeout
    )
