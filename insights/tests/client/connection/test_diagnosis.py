import json
from insights.client import InsightsClient
from insights.client.config import InsightsConfig
from insights.client.connection import InsightsConnection
from mock.mock import patch, Mock
import pytest

TEST_REMEDIATION_ID = 123456


class MockSession(object):
    def __init__(self):
        self.status_code = None
        self.text = None
        self.content = '{"big_dumb_error": "you_done_goofed"}'

    def get(self, url=None, timeout=None, headers=None, data=None, params=None):
        if params and params['remediation'] == TEST_REMEDIATION_ID:
            self.content = '{"specific_dumb_error": "stop_goofin"}'
        return MockResponse(self.status_code, self.text, self.content)

    def put(self, url=None, timeout=None, headers=None, data=None):
        return MockResponse(self.status_code, self.text, None)


class MockResponse(object):
    def __init__(self, status_code, text, content):
        self.status_code = status_code
        self.text = text
        self.content = content

    def json(self):
        return json.loads(self.content)


def mock_init_session(obj):
    return MockSession()


def mock_get_proxies(obj):
    return


@pytest.mark.skip()
@patch('insights.client.connection.InsightsConnection._init_session',
       mock_init_session)
@patch('insights.client.connection.InsightsConnection.get_proxies',
       mock_get_proxies)
@patch('insights.client.utilities.constants.machine_id_file',
       '/tmp/machine-id')
def test_get_diagnosis():
    conf = InsightsConfig()
    c = InsightsConnection(conf)
    c.session.status_code = 200
    assert c.get_diagnosis() == {'big_dumb_error': 'you_done_goofed'}
    c.session.status_code = 404
    assert c.get_diagnosis() is None
    c.session.status_code = 500
    c.session.text = 'oops'
    assert c.get_diagnosis() is None


@pytest.mark.skip()
@patch('insights.client.connection.InsightsConnection._init_session',
       mock_init_session)
@patch('insights.client.connection.InsightsConnection.get_proxies',
       mock_get_proxies)
@patch('insights.client.utilities.constants.machine_id_file',
       '/tmp/machine-id')
def test_get_diagnosis_with_id():
    conf = InsightsConfig()
    c = InsightsConnection(conf)
    c.session.status_code = 200
    assert c.get_diagnosis(TEST_REMEDIATION_ID) == {'specific_dumb_error': 'stop_goofin'}
    c.session.status_code = 404
    assert c.get_diagnosis() is None
    c.session.status_code = 500
    c.session.text = 'oops'
    assert c.get_diagnosis() is None


def test_get_diagnosis_offline():
    conf = InsightsConfig()
    conf.offline = True
    c = InsightsClient(conf)
    assert c.get_diagnosis() is None


@patch('insights.client.connection.InsightsConnection._init_session', Mock())
@patch('insights.client.connection.InsightsConnection.get_proxies', Mock())
@patch('insights.client.utilities.constants.machine_id_file', '/tmp/machine-id')
@patch('insights.client.connection.InsightsConnection.get')
def test_get_diagnosis_success(get):
    '''
    Verify that fetching a diagnosis without an ID succeeds and
    returns a dict when HTTP response is valid
    '''
    conf = InsightsConfig()
    c = InsightsConnection(conf)
    get.return_value = MockResponse(status_code=200, text="OK", content="{\"test\": \"test\"}")
    assert c.get_diagnosis() == {"test": "test"}
