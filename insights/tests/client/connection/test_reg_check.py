import requests
import json
from insights.client.connection import InsightsConnection
from mock.mock import MagicMock, Mock, patch


@patch("insights.client.connection.generate_machine_id", return_value='xxxxxx')
@patch("insights.client.connection.machine_id_exists", return_value=True)
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_registration_check_ok_reg(get_proxies, _init_session, _machine_id_exists, _generate_machine_id):
    '''
    Request completed OK, registered
        Returns True
    '''
    config = Mock(legacy_upload=False, base_url='example.com')
    conn = InsightsConnection(config)

    res = requests.Response()
    res._content = json.dumps(
        {
            'insights_id': 'xxxxxx',
            'id': 'yyyyyy'
        })
    res.status_code = 200

    conn.get = MagicMock(return_value=res)
    assert conn.api_registration_check()


@patch("insights.client.connection.machine_id_exists", return_value=False)
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_registration_check_ok_unreg(get_proxies, _init_session, _machine_id_exists):
    '''
    Request completed OK, has not been registered
        Returns False
    '''
    config = Mock(legacy_upload=False, base_url='example.com')
    conn = InsightsConnection(config)

    res = requests.Response()
    res._content = json.dumps(
        {
            "count": 0,
            "page": 1,
            "per_page": 50,
            "results": [],
            "total": 0
        })
    res.status_code = 200

    conn.get = MagicMock(return_value=res)
    assert conn.api_registration_check() is False


@patch("insights.client.connection.generate_machine_id", return_value='xxxxxx')
@patch("insights.client.connection.machine_id_exists", return_value=True)
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_registration_check_parse_error(get_proxies, _init_session, _machine_id_exists, _generate_machine_id):
    '''
    Can't parse response
        Returns None
    '''
    config = Mock(legacy_upload=False, base_url='example.com')
    conn = InsightsConnection(config)

    res = requests.Response()
    res._content = 'zSDFasfghsRGH'
    res.status_code = 200

    conn.get = MagicMock(return_value=res)
    assert conn.api_registration_check() is None


@patch("insights.client.connection.generate_machine_id", return_value='xxxxxx')
@patch("insights.client.connection.machine_id_exists", return_value=True)
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_registration_check_no_host(get_proxies, _init_session, _machine_id_exists, _generate_machine_id):
    '''
    No hosts found in response
        Returns False
    '''
    config = Mock(legacy_upload=False, base_url='example.com')
    conn = InsightsConnection(config)

    res = requests.Response()
    res._content = json.dumps(
        {
            "title": "Not Found",
            "detail": "No host found for Insights ID 'xxxxxx'.",
            "insights_id": "xxxxxx",
        })
    res.status_code = 404

    conn.get = MagicMock(return_value=res)
    assert conn.api_registration_check() is False


@patch("insights.client.connection.generate_machine_id", return_value='xxxxxx')
@patch("insights.client.connection.machine_id_exists", return_value=True)
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_registration_check_multiple_hosts(get_proxies, _init_session, _machine_id_exists, _generate_machine_id):
    '''
    Multiple hosts found in response
        Returns False
    '''
    config = Mock(legacy_upload=False, base_url='example.com')
    conn = InsightsConnection(config)

    res = requests.Response()
    res._content = json.dumps(
        {
            "title": "Conflict",
            "detail": "Multiple hosts with Insights ID 'xxxxxx' detected.",
            "insights_id": "xxxxxx",
        })
    res.status_code = 409

    conn.get = MagicMock(return_value=res)
    assert conn.api_registration_check() is False


@patch("insights.client.connection.generate_machine_id", return_value='xxxxxx')
@patch("insights.client.connection.machine_id_exists", return_value=True)
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_registration_check_bad_res(get_proxies, _init_session, _machine_id_exists, _generate_machine_id):
    '''
    Failure HTTP response
        Returns None
    '''
    config = Mock(legacy_upload=False, base_url='example.com')
    conn = InsightsConnection(config)

    res = requests.Response()
    res._content = 'wakannai'
    res.status_code = 500

    conn.get = MagicMock(return_value=res)
    assert conn.api_registration_check() is None


@patch("insights.client.connection.generate_machine_id", return_value='xxxxxx')
@patch("insights.client.connection.machine_id_exists", return_value=True)
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_registration_check_conn_error(get_proxies, _init_session, _machine_id_exists, _generate_machine_id):
    '''
    Connection error
        Returns None
    '''
    config = Mock(legacy_upload=False, base_url='example.com')
    conn = InsightsConnection(config)
    conn.get = MagicMock()
    conn.get.side_effect = requests.ConnectionError()
    assert conn.api_registration_check() is None
