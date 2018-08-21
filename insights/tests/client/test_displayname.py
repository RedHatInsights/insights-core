from insights.client.config import InsightsConfig
from insights.client.connection import InsightsConnection
from mock.mock import patch


class MockSession(object):
    def __init__(self):
        self.status_code = None
        self.text = None

    def put(self, url=None, timeout=None, headers=None, data=None):
        return MockResponse(self.status_code, self.text)


class MockResponse(object):
    def __init__(self, expected_status, expected_text):
        self.status_code = expected_status
        self.text = expected_text


def mock_init_session(obj):
    return MockSession()


def mock_get_proxies(obj):
    return


@patch('insights.client.connection.InsightsConnection._init_session',
       mock_init_session)
@patch('insights.client.connection.InsightsConnection.get_proxies',
       mock_get_proxies)
def test_set_display_name():
    conf = InsightsConfig()
    c = InsightsConnection(conf)
    c.session.status_code = 200
    assert c.set_display_name('GO STICK YOUR HEAD IN A PIG')
    c.session.status_code = 404
    assert not c.set_display_name('GO STICK YOUR HEAD IN A PIG')
    c.session.status_code = 500
    c.session.text = 'oops'
    assert not c.set_display_name('GO STICK YOUR HEAD IN A PIG')
