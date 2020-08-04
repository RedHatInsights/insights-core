import requests
import json
import pytest
from insights.client.connection import InsightsConnection
from mock.mock import MagicMock, Mock, patch


@patch("insights.client.connection.generate_machine_id", Mock(return_value='xxxxxx'))
@patch("insights.client.connection.InsightsConnection._init_session", Mock())
@patch("insights.client.connection.InsightsConnection.get_proxies", Mock())
def test_registration_check_ok_reg():
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
        }).encode('utf-8')
    res.status_code = 200

    conn.get = MagicMock(return_value=res)
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
        }).encode('utf-8')
    res.status_code = 200

    conn.get = MagicMock(return_value=res)
    assert conn.api_registration_check() is False


@patch("insights.client.connection.generate_machine_id", return_value='xxxxxx')
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_registration_check_parse_error(get_proxies, _init_session, _):
    '''
    Can't parse response
        Return False
    '''
    config = Mock(legacy_upload=False, base_url='example.com')
    conn = InsightsConnection(config)

    res = requests.Response()
    res._content = b'zSDFasfghsRGH'
    res.status_code = 200

    conn.get = MagicMock(return_value=res)
    assert conn.api_registration_check() is False


@patch("insights.client.connection.generate_machine_id", return_value='xxxxxx')
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_registration_check_bad_res(get_proxies, _init_session, _):
    '''
    Failure HTTP response
        Return False
    '''
    config = Mock(legacy_upload=False, base_url='example.com')
    conn = InsightsConnection(config)

    res = requests.Response()
    res._content = b'wakannai'
    res.status_code = 500

    conn.get = MagicMock(return_value=res)
    assert conn.api_registration_check() is False


@patch("insights.client.connection.generate_machine_id", return_value='xxxxxx')
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
@patch("insights.client.connection.InsightsConnection.get")
def test_registration_check_conn_error(get, get_proxies, _init_session, _):
    '''
    Connection error
        RuntimeError raised
    '''
    config = Mock(legacy_upload=False, base_url='example.com')
    conn = InsightsConnection(config)
    get.side_effect = RuntimeError
    with pytest.raises(RuntimeError):
        conn.api_registration_check()
