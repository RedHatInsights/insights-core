from insights.client import InsightsClient
from insights.client.config import InsightsConfig
from insights.client.constants import InsightsConstants as constants
from mock.mock import Mock, patch
from pytest import fixture
from tempfile import NamedTemporaryFile


@fixture
def insights_client():
    config = InsightsConfig(http_timeout=123)
    client = InsightsClient(config)
    client.connection = Mock(**{
        "base_url": "http://www.example.com/",
        "get.return_value.headers.items.return_value": [],
        "get.return_value.status_code": 200,
        "get.return_value.content": b"",
    })
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
    insights_client.connection.get.assert_called_once_with(url, headers=headers, log_response_text=False)


def test_request_forced(insights_client):
    """
    A forced egg fetch request is issued with correct timeout set.
    """
    source_path = 'some-source-path'
    insights_client._fetch(source_path, "", "", force=False)

    url = "{0}{1}".format(insights_client.connection.base_url, source_path)
    insights_client.connection.get.assert_called_once_with(url, log_response_text=False)


@patch('insights.client.InsightsClient._fetch', Mock())
@patch('insights.client.InsightsClient.get_egg_url', return_value='/testvalue')
@patch('insights.client.write_data_to_file')
def test_egg_release_written(write_data_to_file, get_egg_url, insights_client):
    '''
    Verify egg release file successfully written after request
    '''
    insights_client.fetch(force=False)
    write_data_to_file.assert_called_once_with('/testvalue', constants.egg_release_file)


@patch('insights.client.InsightsClient._fetch')
@patch('insights.client.InsightsClient.get_egg_url', return_value='/testvalue')
@patch('insights.client.write_data_to_file')
def test_egg_release_error(write_data_to_file, get_egg_url, _fetch, insights_client):
    '''
    Verify OSError and IOError are caught and process continues on
    '''
    write_data_to_file.side_effect = OSError('test')
    assert insights_client.fetch(force=False)
    write_data_to_file.assert_called_once_with('/testvalue', constants.egg_release_file)
    assert _fetch.call_count == 2

    write_data_to_file.side_effect = None
    write_data_to_file.reset_mock()
    _fetch.reset_mock()

    write_data_to_file.side_effect = IOError('test')
    assert insights_client.fetch(force=False)
    write_data_to_file.assert_called_once_with('/testvalue', constants.egg_release_file)
    assert _fetch.call_count == 2
