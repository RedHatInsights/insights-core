import json
import requests
from insights.client import InsightsClient
from insights.client.config import InsightsConfig
from insights.client.connection import InsightsConnection
from unittest.mock import MagicMock, patch, Mock
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
@patch("insights.client.connection.InsightsConnection._fetch_system_by_machine_id", return_value={"id": "inv-1"})
@patch('insights.client.connection.InsightsConnection.get')
def test_get_diagnosis_success(get, fetch_system_by_machine_id):
    '''
    Verify that fetching a diagnosis without an ID succeeds and
    returns a dict when HTTP response is valid
    '''
    conf = InsightsConfig()
    c = InsightsConnection(conf)
    get.return_value = MockResponse(status_code=200, text="OK", content="{\"test\": \"test\"}")
    assert c.get_diagnosis() == {"test": "test"}


@patch('insights.client.connection.InsightsConnection._init_session', Mock())
@patch('insights.client.connection.InsightsConnection.get_proxies', Mock())
@patch("insights.client.connection.InsightsConnection._fetch_system_by_machine_id", return_value=False)
def test_get_diagnosis_not_registered(fetch_system_by_machine_id):
    '''
    Verify that fetching a diagnosis fails when the system is not registered
    '''
    conf = InsightsConfig()
    c = InsightsConnection(conf)
    assert c.get_diagnosis() is False


@patch("insights.client.connection.generate_machine_id", return_value="machine-1")
@patch("insights.client.connection.InsightsConnection._init_session", Mock())
@patch("insights.client.connection.InsightsConnection.get_proxies", Mock())
@patch("insights.client.connection.InsightsConnection._fetch_system_by_machine_id")
@patch("insights.client.connection.InsightsConnection.get")
def test_get_diagnosis_uses_stored_insights_id(get, fetch_system, _machine_id):
    '''
    Remediations is keyed by the insights_id Inventory stored, including
    the nil UUID. An empty 404 must not be parsed as JSON.
    '''
    fetch_system.return_value = {
        "id": "inv-1",
        "insights_id": "00000000-0000-0000-0000-000000000000",
    }
    body = {
        "id": "inv-1",
        "insights_id": "00000000-0000-0000-0000-000000000000",
        "details": {},
    }
    get.return_value = MockResponse(200, "OK", json.dumps(body))
    c = InsightsConnection(InsightsConfig())
    assert c.get_diagnosis() == body
    assert get.call_args[0][0].endswith(
        "/diagnosis/00000000-0000-0000-0000-000000000000"
    )

    empty = requests.Response()
    empty.status_code = 404
    empty._content = b""
    get.return_value = empty
    assert c.get_diagnosis() is None


NIL_UUID = "00000000-0000-0000-0000-000000000000"
ONE_HOST = {"total": 1, "results": [{"id": "inv-1", "insights_id": NIL_UUID}]}


def _body(status, payload):
    res = MagicMock()
    res.status_code = status
    res.content = json.dumps(payload).encode("utf-8")
    return res


def _empty_404():
    res = requests.Response()
    res.status_code = 404
    res._content = b""
    return res


@patch("insights.client.connection._get_rhsm_identity", return_value="sub-1")
@patch("insights.client.connection.generate_machine_id", return_value="machine-1")
@patch("insights.client.connection.machine_id_exists", return_value=True)
@patch("insights.client.connection.InsightsConnection._init_session", Mock())
@patch("insights.client.connection.InsightsConnection.get_proxies", Mock())
@pytest.mark.parametrize("host_exists,lookup,expected", [
    # hit: the subscription is never asked
    (_body(200, {"id": "inv-1"}), None, {"id": "inv-1", "insights_id": "machine-1"}),
    # miss with a JSON or an empty body: the one host for this subscription
    (_body(404, {"detail": "No host found"}), _body(200, ONE_HOST), ONE_HOST["results"][0]),
    (_empty_404(), _body(200, ONE_HOST), ONE_HOST["results"][0]),
    # lookup failed: an error, not "not registered"
    (_body(404, {"detail": "No host found"}), _body(500, {}), None),
    # no host for this subscription: the collection answers 200 with total 0
    (_body(404, {"detail": "No host found"}),
     _body(200, {"total": 0, "results": []}), False),
    # a 404 from the collection is a routing error, not an absent host
    (_body(404, {"detail": "No host found"}), _body(404, {}), None),
])
def test_fetch_system_by_machine_id(_exists, _machine_id, _subman, host_exists, lookup, expected):
    '''
    A host_exists miss is not proof that the host is unregistered: the
    subscription-manager lookup decides, and a failed lookup is an error.
    '''
    conn = InsightsConnection(Mock(legacy_upload=False, base_url="example.com"))

    def _get(url, **kwargs):
        return host_exists if "host_exists" in url else lookup

    conn.get = MagicMock(side_effect=_get)
    assert conn._fetch_system_by_machine_id() == expected
    if lookup is None:
        conn.get.assert_called_once()
    else:
        assert "subscription_manager_id=sub-1" in conn.get.call_args_list[-1][0][0]


@patch("insights.client.connection._get_rhsm_identity", return_value="sub-1")
@patch("insights.client.connection.InsightsConnection._init_session", Mock())
@patch("insights.client.connection.InsightsConnection.get_proxies", Mock())
@pytest.mark.parametrize("get,expected", [
    (MagicMock(side_effect=requests.ConnectionError), None),
    (MagicMock(return_value=_body(500, {})), None),
    (MagicMock(return_value=_body(200, ["not", "an", "object"])), None),
    (MagicMock(return_value=_body(200, {"total": 1, "results": {"id": "inv-1"}})), None),
    (MagicMock(return_value=_body(200, {"total": 1, "results": "x"})), None),
    # the collection answers 200 with total 0 when nothing matches; a 404
    # means the route is wrong, which must not read as "no host"
    (MagicMock(return_value=_body(200, {"total": 0, "results": []})), False),
    (MagicMock(return_value=_body(404, {})), None),
    (MagicMock(return_value=_body(200, {"total": 2, "results": [{}, {}]})), False),
    (MagicMock(return_value=_body(200, ONE_HOST)), ONE_HOST["results"][0]),
])
def test_host_by_subscription_manager_id(_subman, get, expected):
    '''
    Only a miss means "no host". A failed or unexpected response is an
    error, so callers keep the local registration.
    '''
    conn = InsightsConnection(Mock(legacy_upload=False, base_url="example.com"))
    conn.get = get
    assert conn._host_by_subscription_manager_id() == expected
