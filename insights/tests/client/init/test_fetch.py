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

from insights.client import InsightsClient
from insights.client.config import InsightsConfig
from mock.mock import Mock
from pytest import fixture
from tempfile import NamedTemporaryFile


@fixture
def insights_client():
    config = InsightsConfig(http_timeout=123)
    client = InsightsClient(config)
    client.session = Mock(**{"get.return_value.headers.items.return_value": []})
    client.connection = Mock(base_url="http://www.example.com/")
    return client


def test_request_with_etag(insights_client):
    """
    An egg fetch request with Etag is issued with correct timeout set.
    """
    etag_file = NamedTemporaryFile('w+t')
    etag_value = 'some_etag'
    etag_file.write(etag_value)
    etag_file.seek(0)

    source_path = 'some-source-path'
    insights_client._fetch(source_path, etag_file.name, "", force=False)

    url = "{0}{1}".format(insights_client.connection.base_url, source_path)
    headers = {'If-None-Match': etag_value}
    timeout = insights_client.config.http_timeout
    insights_client.session.get.assert_called_once_with(url, headers=headers, timeout=timeout)


def test_request_forced(insights_client):
    """
    A forced egg fetch request is issued with correct timeout set.
    """
    source_path = 'some-source-path'
    insights_client._fetch(source_path, "", "", force=False)

    url = "{0}{1}".format(insights_client.connection.base_url, source_path)
    timeout = insights_client.config.http_timeout
    insights_client.session.get.assert_called_once_with(url, timeout=timeout)
