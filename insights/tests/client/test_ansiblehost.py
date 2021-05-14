import pytest
from insights.client.config import InsightsConfig
from insights.client.connection import InsightsConnection
from mock.mock import patch


class MockSession(object):
    def __init__(self):
        self.status_code = None
        self.text = None
        self.content = '{"display_name": "test"}'

    def get(self, url=None, timeout=None, headers=None, data=None):
        return MockResponse(self.status_code, self.text, self.content)

    def put(self, url=None, timeout=None, headers=None, data=None):
        return MockResponse(self.status_code, self.text, None)


class MockResponse(object):
    def __init__(self, expected_status, expected_text, expected_content):
        self.status_code = expected_status
        self.text = expected_text
        self.content = expected_content


def mock_init_session(obj):
    return MockSession()


def mock_get_proxies(obj):
    return


@pytest.mark.skip(reason='No time to fix this for double-API calling')
@patch('insights.client.connection.InsightsConnection._init_session',
       mock_init_session)
@patch('insights.client.connection.InsightsConnection.get_proxies',
       mock_get_proxies)
@patch('insights.client.utilities.constants.machine_id_file',
       '/tmp/machine-id')
def test_set_ansible_host():
    conf = InsightsConfig()
    c = InsightsConnection(conf)
    c.session.status_code = 200
    assert c.set_ansible_host('GO STICK YOUR HEAD IN A PIG')
    c.session.status_code = 404
    assert not c.set_ansible_host('GO STICK YOUR HEAD IN A PIG')
    c.session.status_code = 500
    c.session.text = 'oops'
    assert not c.set_ansible_host('GO STICK YOUR HEAD IN A PIG')


def test_ansible_host_no_reg_forces_legacy_false():
    '''
    When not specifying --register, using --ansible-host on the CLI forces legacy_upload to False
    '''
    conf = InsightsConfig(register=False, ansible_host="test", legacy_upload=True)
    conf._cli_opts = ["ansible_host"]
    conf._imply_options()
    assert not conf.legacy_upload
    conf = InsightsConfig(register=False, ansible_host="test", legacy_upload=False)
    conf._cli_opts = ["ansible_host"]
    conf._imply_options()
    assert not conf.legacy_upload


def test_ansible_host_reg_legacy_no_change():
    '''
    When specifying --register, using --ansible-host on the CLI does not affect legacy_upload
    '''
    conf = InsightsConfig(register=True, ansible_host="test", legacy_upload=True)
    conf._cli_opts = ["ansible_host"]
    conf._imply_options()
    assert conf.legacy_upload
    conf = InsightsConfig(register=True, ansible_host="test", legacy_upload=False)
    conf._cli_opts = ["ansible_host"]
    conf._imply_options()
    assert not conf.legacy_upload
