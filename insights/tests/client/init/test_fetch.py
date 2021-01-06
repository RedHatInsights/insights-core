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


@patch('insights.client.InsightsClient._fetch', Mock())
@patch('insights.client.os.path', Mock())
@patch('insights.client.tempfile', Mock())
@patch('insights.client.InsightsClient.get_egg_url', return_value='/testvalue')
@patch('insights.client.write_to_disk')
def test_egg_release_written(write_to_disk, get_egg_url, insights_client):
    '''
    Verify egg release file successfully written after request
    '''
    insights_client.fetch(force=False)
    write_to_disk.assert_called_once_with(constants.egg_release_file, content='/testvalue')


@patch('insights.client.InsightsClient._fetch')
@patch('insights.client.os.path', Mock())
@patch('insights.client.tempfile', Mock())
@patch('insights.client.InsightsClient.get_egg_url', return_value='/testvalue')
@patch('insights.client.write_to_disk')
def test_egg_release_error(write_to_disk, get_egg_url, _fetch, insights_client):
    '''
    Verify OSError and IOError are caught and process continues on
    '''
    write_to_disk.side_effect = OSError('test')
    assert insights_client.fetch(force=False)
    write_to_disk.assert_called_once_with(constants.egg_release_file, content='/testvalue')
    assert _fetch.call_count == 2

    write_to_disk.side_effect = None
    write_to_disk.reset_mock()
    _fetch.reset_mock()

    write_to_disk.side_effect = IOError('test')
    assert insights_client.fetch(force=False)
    write_to_disk.assert_called_once_with(constants.egg_release_file, content='/testvalue')
    assert _fetch.call_count == 2
