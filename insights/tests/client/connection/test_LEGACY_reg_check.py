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
    config = Mock(legacy_upload=True, base_url='example.com')
    conn = InsightsConnection(config)

    res = requests.Response()
    res._content = json.dumps({'unregistered_at': None})
    res.status_code = 200

    conn.session.get = MagicMock(return_value=res)
    assert conn.api_registration_check()


@patch("insights.client.connection.generate_machine_id", return_value='xxxxxx')
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_registration_check_ok_reg_then_unreg(get_proxies, _init_session, _):
    '''
    Request completed OK, was once registered but has been unregistered
        Returns the date it was unregistered
    '''
    config = Mock(legacy_upload=True, base_url='example.com')
    conn = InsightsConnection(config)

    res = requests.Response()
    res._content = json.dumps({'unregistered_at': '2019-04-10'})
    res.status_code = 200

    conn.session.get = MagicMock(return_value=res)
    assert conn.api_registration_check() == '2019-04-10'


@patch("insights.client.connection.generate_machine_id", return_value='xxxxxx')
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_registration_check_ok_unreg(get_proxies, _init_session, _):
    '''
    Request completed OK, has never been registered
        Returns None
    '''
    config = Mock(legacy_upload=True, base_url='example.com')
    conn = InsightsConnection(config)

    res = requests.Response()
    res._content = json.dumps({})
    res.status_code = 404

    conn.session.get = MagicMock(return_value=res)
    assert conn.api_registration_check() is None


@patch("insights.client.connection.generate_machine_id", return_value='xxxxxx')
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_registration_check_bad_res(get_proxies, _init_session, _):
    '''
    Can't parse response
        Returns False
    '''
    config = Mock(legacy_upload=True, base_url='example.com')
    conn = InsightsConnection(config)

    res = requests.Response()
    res._content = 'zSDFasfghsRGH'
    res.status_code = 500

    conn.session.get = MagicMock(return_value=res)
    assert conn.api_registration_check() is False


@patch("insights.client.connection.generate_machine_id", return_value='xxxxxx')
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
@patch("insights.client.connection.InsightsConnection.test_connection")
def test_registration_check_conn_error(test_connection, get_proxies, _init_session, _):
    '''
    Can't connect, run connection test
        Returns False
    '''
    config = Mock(legacy_upload=True, base_url='example.com')
    conn = InsightsConnection(config)

    conn.session.get = MagicMock()
    conn.session.get.side_effect = requests.ConnectionError()
    assert conn.api_registration_check() is False
    test_connection.assert_called_once()
