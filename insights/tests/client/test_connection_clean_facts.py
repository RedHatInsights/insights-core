try:
    from unittest.mock import patch
except Exception:
    from mock import patch

from copy import deepcopy

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


CFACTS = {
    'hostname': determine_hostname(),
    'ip': ['10.0.0.1', '192.168.0.1'],
}


@patch('insights.client.connection.InsightsConnection._init_session', mock_init_session)
@patch('insights.client.connection.InsightsConnection.post', return_value=MockSession())
@patch('insights.client.connection.InsightsUploadConf.get_rm_conf', return_value={})
def test_connection_clean_facts_no_clean_all(rm_conf, post):
    # No cleaning per client configuration
    config = InsightsConfig(obfuscate=False)
    conn = InsightsConnection(config)
    tmp = deepcopy(CFACTS)
    ret = conn._clean_facts(tmp)
    # Nothing changed
    assert ret == CFACTS


@patch('insights.client.connection.InsightsConnection._init_session', mock_init_session)
@patch('insights.client.connection.InsightsConnection.post', return_value=MockSession())
@patch('insights.client.connection.InsightsUploadConf.get_rm_conf', return_value={})
def test_connection_clean_facts_clean_ip_only(rm_conf, post):
    # No hostname cleaning per client configuration
    config = InsightsConfig(obfuscate=True, obfuscate_hostname=False)
    conn = InsightsConnection(config)
    tmp = deepcopy(CFACTS)
    ret = conn._clean_facts(tmp)
    # Hostname is not changed
    assert ret['hostname'] == CFACTS['hostname']
    # IPs are changed
    assert ret['ip'] != CFACTS['ip']


@patch('insights.client.connection.InsightsConnection._init_session', mock_init_session)
@patch('insights.client.connection.InsightsConnection.post', return_value=MockSession())
@patch('insights.client.connection.InsightsUploadConf.get_rm_conf', return_value={})
def test_connection_clean_facts_clean_all(rm_conf, post):
    config = InsightsConfig(obfuscate=True, obfuscate_hostname=True)
    conn = InsightsConnection(config)
    tmp = deepcopy(CFACTS)
    ret = conn._clean_facts(tmp)
    # Hostname is changed
    assert ret['hostname'] != CFACTS['hostname']
    # IPs are changed
    assert ret['ip'] != CFACTS['ip']
