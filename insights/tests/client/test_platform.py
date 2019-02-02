import json
from insights.client.config import InsightsConfig
from insights.client.connection import InsightsConnection
from mock.mock import patch, mock_open, ANY
from pytest import raises


class MockSession(object):
    def __init__(self):
        self.status_code = None
        self.text = None
        self.content = '{"display_name": "test"}'
        self.base_url = "https://cert-api.access.redhat.com/r/insights"

    def get(self, url=None, timeout=None, headers=None, data=None):
        return MockResponse(self.status_code, self.text, self.content, None, headers or {})

    def post(self, url=None, timeout=None, headers=None, data=None, files=None):
        return MockResponse(self.status_code, self.text, self.content, None, headers or {})

    def put(self, url=None, timeout=None, headers=None, data=None):
        return MockResponse(self.status_code, self.text, None, None, headers or {})


class MockResponse(object):
    def __init__(self, expected_status, expected_text, expected_content, expected_reason, headers):
        self.status_code = expected_status
        self.text = expected_text
        self.content = expected_content
        self.reason = expected_reason
        self.headers = headers


def mock_init_session(ignore, obj):
    return MockSession()


def mock_get_proxies(obj):
    return


def mock_machine_id():
    return 'XXXXXXXX'


class MockMagic():
    def __init__(*args):
        pass

    def load(self):
        return None

    def file(self, *args):
        return 'application/gzip'


def test_config_conflicts():
    '''
    Ensure --payload requires --content-type
    '''
    with raises(ValueError) as v:
        InsightsConfig(payload='aaa')
    assert str(v.value) == '--payload requires --content-type'


@patch('insights.client.connection.InsightsConnection.new_session',
       mock_init_session)
def test_upload_urls():
    '''
    Ensure upload urls are defined correctly
    '''
    # legacy default
    conf = InsightsConfig()
    c = InsightsConnection(conf)
    assert c.upload_url == 'https://' + conf.base_url + '/uploads'

    # plaform implied
    conf = InsightsConfig(legacy_upload=False)
    c = InsightsConnection(conf)
    assert c.upload_url == 'https://' + conf.base_url + '/platform/upload/api/v1/upload'

    # explicitly configured
    conf = InsightsConfig(upload_url='BUNCHANONSENSE')
    c = InsightsConnection(conf)
    assert c.upload_url == 'BUNCHANONSENSE'


@patch("insights.client.connection.get_canonical_facts",
        return_value={'test': 'facts'})
@patch('insights.client.connection.InsightsConnection.new_session',
        mock_init_session)
@patch("insights.client.connection.open", new_callable=mock_open)
def test_payload_upload(op, new_session):
    '''
    Ensure a payload upload occurs with the right URL and params
    '''
    conf = InsightsConfig(legacy_upload=False)
    c = InsightsConnection(conf)
    c.session = new_session
    c.upload_archive('testp', 'testct', None)
    c.session.post.assert_called_with(
        'https://' + c.config.base_url + '/platform/upload/api/v1/upload',
        files={
            'file': ('testp', ANY, 'testct'),  # ANY = return call from mocked open(), acts as filepointer here
            'metadata': json.dumps({'test': 'facts'})},
        headers={})


@patch('insights.contrib.magic.open', MockMagic)
@patch('insights.client.connection.generate_machine_id', mock_machine_id)
@patch("insights.client.connection.get_canonical_facts",
        return_value={'test': 'facts'})
@patch('insights.client.connection.InsightsConnection.new_session',
        mock_init_session)
@patch("insights.client.connection.open", new_callable=mock_open)
def test_legacy_upload(op, new_session):
    '''
    Ensure an Insights collected tar upload to legacy occurs with the right URL and params
    '''
    conf = InsightsConfig()
    c = InsightsConnection(conf)
    c.session = new_session
    c.upload_archive('testp', 'testct', None)
    c.session.post.assert_called_with(
        'https://' + c.config.base_url + '/uploads/XXXXXXXX',
        files={
            'file': ('testp', ANY, 'application/gzip')},  # ANY = return call from mocked open(), acts as filepointer here
        headers={'x-rh-collection-time': 'None'})
