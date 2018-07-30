import sys

from insights.client import InsightsClient
from insights.client.config import InsightsConfig
from insights import package_info
from mock.mock import patch
from mock.mock import Mock


# @TODO DRY the args hack.

def test_version():

    # Hack to prevent client from parsing args to py.test
    tmp = sys.argv
    sys.argv = []

    try:
        config = InsightsConfig(logging_file='/tmp/insights.log')
        client = InsightsClient(config)
        result = client.version()
        assert result == "%s-%s" % (package_info["VERSION"], package_info["RELEASE"])
    finally:
        sys.argv = tmp


@patch('insights.client.client.constants.sleep_time', 0)
@patch('insights.client.client.InsightsConnection.upload_archive',
       return_value=Mock(status_code=500))
def test_upload_500_retry(upload_archive):

    # Hack to prevent client from parsing args to py.test
    tmp = sys.argv
    sys.argv = []

    try:
        retries = 3

        config = InsightsConfig(logging_file='/tmp/insights.log', retries=retries)
        client = InsightsClient(config)
        client.upload('/tmp/insights.tar.gz')

        upload_archive.assert_called()
        assert upload_archive.call_count == retries
    finally:
        sys.argv = tmp


@patch('insights.client.client.InsightsConnection.handle_fail_rcs')
@patch('insights.client.client.InsightsConnection.upload_archive',
       return_value=Mock(status_code=412))
def test_upload_412_no_retry(upload_archive, handle_fail_rcs):

    # Hack to prevent client from parsing args to py.test
    tmp = sys.argv
    sys.argv = []

    try:
        config = InsightsConfig(logging_file='/tmp/insights.log', retries=3)
        client = InsightsClient(config)
        client.upload('/tmp/insights.tar.gz')

        upload_archive.assert_called_once()
    finally:
        sys.argv = tmp


@patch('insights.client.connection.write_unregistered_file')
@patch('insights.client.client.InsightsConnection.upload_archive',
       return_value=Mock(**{"status_code": 412,
                            "json.return_value": {"unregistered_at": "now", "message": "msg"}}))
def test_upload_412_write_unregistered_file(upload_archive, write_unregistered_file):

    # Hack to prevent client from parsing args to py.test
    tmp = sys.argv
    sys.argv = []

    try:
        config = InsightsConfig(logging_file='/tmp/insights.log', retries=3)
        client = InsightsClient(config)
        client.upload('/tmp/insights.tar.gz')

        unregistered_at = upload_archive.return_value.json()["unregistered_at"]
        write_unregistered_file.assert_called_once_with(unregistered_at)
    finally:
        sys.argv = tmp
