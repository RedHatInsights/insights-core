import requests
import json
from insights.client.connection import InsightsConnection
from mock.mock import MagicMock, Mock, patch


@patch("insights.client.connection.generate_machine_id", return_value='xxxxxx')
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_registration_check_ok_reg(get_proxies, _init_session, _):
    '''
    Request completed OK, registered
        Returns True
    '''
    config = Mock(legacy_upload=False, base_url='example.com')
    conn = InsightsConnection(config)

    res = requests.Response()
    res._content = json.dumps(
        {
            "count": 1,
            "page": 1,
            "per_page": 50,
            "results": [
                {
                    'insights_id': 'xxxxxx',
                    'id': 'yyyyyy'
                }
            ],
            "total": 1
        })
    res.status_code = 200

    conn.session.get = MagicMock(return_value=res)
    assert conn.api_registration_check()


@patch("insights.client.connection.generate_machine_id", return_value='xxxxxx')
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_registration_check_ok_unreg(get_proxies, _init_session, _):
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

    conn.session.get = MagicMock(return_value=res)
    assert conn.api_registration_check() is False


@patch("insights.client.connection.generate_machine_id", return_value='xxxxxx')
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_registration_check_parse_error(get_proxies, _init_session, _):
    '''
    Can't parse response
        Returns None
    '''
    config = Mock(legacy_upload=False, base_url='example.com')
    conn = InsightsConnection(config)

    res = requests.Response()
    res._content = 'zSDFasfghsRGH'
    res.status_code = 200

    conn.session.get = MagicMock(return_value=res)
    assert conn.api_registration_check() is None


@patch("insights.client.connection.generate_machine_id", return_value='xxxxxx')
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_registration_check_bad_res(get_proxies, _init_session, _):
    '''
    Failure HTTP response
        Returns None
    '''
    config = Mock(legacy_upload=False, base_url='example.com')
    conn = InsightsConnection(config)

    res = requests.Response()
    res._content = 'wakannai'
    res.status_code = 500

    conn.session.get = MagicMock(return_value=res)
    assert conn.api_registration_check() is None


@patch("insights.client.connection.generate_machine_id", return_value='xxxxxx')
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_registration_check_conn_error(get_proxies, _init_session, _):
    '''
    Connection error
        Returns None
    '''
    config = Mock(legacy_upload=False, base_url='example.com')
    conn = InsightsConnection(config)
    conn.session.get.side_effect = requests.ConnectionError()
    assert conn.api_registration_check() is None
