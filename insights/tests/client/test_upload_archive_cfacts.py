import json

try:
    from unittest.mock import patch, mock_open
    builtin_open = "builtins.open"
except Exception:
    from mock import patch
    from mock.mock import mock_open
    builtin_open = "__builtin__.open"

from insights.client.connection import InsightsConnection
from insights.util.hostname import determine_hostname
from insights.client.config import InsightsConfig


class MockSession(object):
    def __init__(self):
        self.status_code = None
        self.text = None
        self.content = '{"display_name": "test"}'
        self.headers = dict()


def mock_init_session(obj):
    return MockSession()


@patch("insights.client.connection.InsightsConnection._legacy_upload_archive", return_value=None)
def test_cfacts_no_cleaning_1(legacy_upload):
    # 1. No need to cleaning as legacy_upload=True
    config = InsightsConfig(legacy_upload=True, obfuscate=True, obfuscate_hostname=True)
    conn = InsightsConnection(config)
    conn.upload_archive('data_collected', 'content_type')
    legacy_upload.assert_called()


@patch('insights.client.connection.InsightsConnection._init_session', mock_init_session)
@patch('insights.client.connection.InsightsConnection.post', return_value=MockSession())
@patch(builtin_open, new_callable=mock_open, read_data='')
@patch('insights.client.connection.InsightsUploadConf.get_rm_conf', return_value={})
@patch("insights.client.connection.get_canonical_facts", return_value={'hostname': determine_hostname()})
@patch("insights.client.connection.logger")
def test_cfacts_no_cleaning_2(logger, facts, rm_conf, _open, post):
    # 2. No cleaning per client configuration
    config = InsightsConfig(legacy_upload=False, obfuscate=False)
    conn = InsightsConnection(config)
    conn.upload_archive('data_collected', 'content_type')
    cfacts = facts.return_value
    cfacts.update({"branch_info": {"remote_branch": -1, "remote_leaf": -1}, "satellite_id": -1})
    c_facts = json.dumps(cfacts)

    for log_message in logger.debug.mock_calls:
        if c_facts in str(log_message):
            break
    else:
        assert False, "Canonical facts weren't obfuscated or logged properly"


@patch('insights.client.connection.InsightsConnection._init_session', mock_init_session)
@patch('insights.client.connection.InsightsConnection.post', return_value=MockSession())
@patch(builtin_open, new_callable=mock_open, read_data='')
@patch('insights.client.connection.InsightsUploadConf.get_rm_conf', return_value={})
@patch("insights.client.connection.get_canonical_facts", return_value={'hostname': determine_hostname(), 'ip': '10.0.0.1'})
@patch("insights.client.connection.logger")
def test_cfacts_cleaned(logger, facts, rm_conf, _open, post):
    # 3. Cleaned per client configuration
    config = InsightsConfig(legacy_upload=False, obfuscate=True, obfuscate_hostname=True)
    conn = InsightsConnection(config)
    conn.upload_archive('data_collected', 'content_type')

    for log_message in logger.debug.mock_calls:
        log_message = str(log_message)
        if (
            "hostname" in log_message
            and determine_hostname() not in log_message
            and "ip" in log_message
            and "10.0.0.1" not in log_message
        ):
            break
    else:
        assert False, "Canonical facts weren't obfuscated or logged properly"
