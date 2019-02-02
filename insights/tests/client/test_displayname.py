from insights.client.config import InsightsConfig
from insights.client.connection import InsightsConnection
from mock.mock import patch


class MockSession(object):
    def __init__(self):
        self.status_code = None
        self.text = None
        self.content = '{"display_name": "test"}'
        self.base_url = "https://www.example.com"

    def get(self, url=None, timeout=None, headers=None, data=None):
        return MockResponse(self.status_code, self.text, self.content)

    def put(self, url=None, timeout=None, headers=None, data=None):
        return MockResponse(self.status_code, self.text, None)


class MockResponse(object):
    def __init__(self, expected_status, expected_text, expected_content):
        self.status_code = expected_status
        self.text = expected_text
        self.content = expected_content


def mock_init_session(ignore, obj):
    return MockSession()


def mock_get_proxies(obj):
    return


@patch('insights.client.connection.InsightsConnection.new_session',
        mock_init_session)
@patch('insights.client.utilities.constants.machine_id_file',
       '/tmp/machine-id')
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
