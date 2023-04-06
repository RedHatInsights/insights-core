# -*- coding: UTF-8 -*-

from insights.client.config import InsightsConfig
from insights.client.connection import InsightsConnection
from insights.client.support import InsightsSupport, registration_check
from mock.mock import Mock, patch


TEMP_TEST_REG_DIR = "/tmp/insights-client-registration"
TEMP_TEST_REG_DIR2 = "/tmp/redhat-access-insights-registration"


@patch("insights.client.support.subprocess")
@patch("insights.client.support.InsightsSupport._support_diag_dump")
def test_collect_support_info_support_diag_dump(support_diag_dump, subprocess):
    """
    collect_suppport_info_method callse _support_diag_dump method.
    """
    config = Mock()
    support = InsightsSupport(config)
    support.collect_support_info()

    support_diag_dump.assert_called_once_with()


@patch("insights.client.support.os.statvfs", **{"return_value.f_bavail": 1, "return_value.f_frsize": 1})
@patch("insights.client.support.Popen", **{"return_value.communicate.return_value": ("", "")})
@patch("insights.client.support.os.path.isfile", return_value=False)
@patch("insights.client.support.registration_check", return_value={})
@patch("insights.client.support.InsightsConnection")
def test_support_diag_dump_insights_connection(insights_connection, registration_check, isfile, popen, statvfs):
    """
    _support_diag_dump method instantiates InsightsConnection with InsightsConfig.
    """
    config = Mock(**{"return_value.auto_config": "", "proxy": "", "offline": False})
    support = InsightsSupport(config)
    support._support_diag_dump()

    insights_connection.assert_called_once_with(config)


@patch('insights.client.support.InsightsConnection')
@patch('insights.client.support.registration_check')
def test_registration_check_called_for_support(registration_check, InsightsConnection):
    '''
        Check registration when doing --support
    '''
    support = InsightsSupport(InsightsConfig(offline=False))
    support.collect_support_info()
    registration_check.assert_called_once()


@patch('insights.client.support.InsightsConnection')
@patch('insights.client.support.registration_check')
@patch('insights.client.support.InsightsConnection.test_connection')
def test_support_diag_dump_offline(test_connection, registration_check, InsightsConnection):
    '''
        Check registration when doing --support
    '''
    support = InsightsSupport(InsightsConfig(offline=True))
    support.collect_support_info()
    InsightsConnection.assert_not_called()
    registration_check.assert_not_called()
    test_connection.assert_not_called()


@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
@patch('insights.client.support.write_registered_file')
@patch('insights.client.support.write_unregistered_file')
@patch('insights.client.support.write_to_disk')
def test_registration_check_unregistered(write_to_disk, write_unregistered_file, write_registered_file, _, __):
    '''
    Ensure that connection function is called and files are written.
    '''
    config = Mock(base_url=None, legacy_upload=False)
    conn = InsightsConnection(config)
    conn.api_registration_check = Mock(return_value=False)
    assert registration_check(conn) is False
    conn.api_registration_check.assert_called_once()
    write_registered_file.assert_not_called()
    write_unregistered_file.assert_called_once()


@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
@patch('insights.client.support.write_registered_file')
@patch('insights.client.support.write_unregistered_file')
def test_registration_check_registered(write_unregistered_file, write_registered_file, _, __):
    '''
    Ensure that connection function is called and files are written.
    '''
    config = Mock(base_url=None, legacy_upload=False)
    conn = InsightsConnection(config)
    conn.api_registration_check = Mock(return_value=True)
    assert registration_check(conn) is True
    conn.api_registration_check.assert_called_once()
    write_registered_file.assert_called_once()
    write_unregistered_file.assert_not_called()


@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_registration_check_registered_unreach(_, __):
    '''
    Ensure that connection function is called and files are written.
    '''
    config = Mock(base_url=None, legacy_upload=False)
    conn = InsightsConnection(config)
    conn.api_registration_check = Mock(return_value=None)
    assert registration_check(conn) is None
    conn.api_registration_check.assert_called_once()


@patch('insights.client.connection.generate_machine_id', return_value="xxxx-xxx-xxxx-xxx")
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
@patch("insights.client.connection.InsightsConnection.get", return_value=Mock(status_code=404, content='{"detail": "System with insights_id ID not found"}'))
@patch('insights.client.support.write_registered_file')
@patch('insights.client.support.write_unregistered_file')
@patch('insights.client.support.write_to_disk')
def test_registration_check_legacy_unregistered_good_json(write_to_disk, write_unregistered_file, write_registered_file, _geturl, __, ___, _generate_machine_id):
    '''
    Ensure that connection function is called and data processed.
    When the system is not registered the server sends a 404 error with a json content.
    Check that when the client get this response the registered file and the machine-id files
    are removed and the unregistered file is created
    '''
    config = Mock(base_url=None, legacy_upload=True)
    conn = InsightsConnection(config)
    check = registration_check(conn)
    assert isinstance(check, dict)
    assert check['status'] is False
    write_registered_file.assert_not_called()
    write_unregistered_file.assert_called_once()
    write_to_disk.assert_called_once()


@patch('insights.client.connection.generate_machine_id', return_value="xxxx-xxx-xxxx-xxx")
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
@patch("insights.client.connection.InsightsConnection.get", return_value=Mock(status_code=404, content='{Page Not Found}'))
@patch('insights.client.support.write_registered_file')
@patch('insights.client.support.write_unregistered_file')
@patch('insights.client.support.write_to_disk')
def test_registration_check_legacy_unregistered_bad_json(write_to_disk, write_unregistered_file, write_registered_file, _geturl, __, ___, _generate_machine_id):
    '''
    Ensure that connection function is called and data processed.
    Check a 404 from a forward that doesn't contain a json a content.
    Check that when the client get this response nothing happens
    '''
    config = Mock(base_url=None, legacy_upload=True)
    conn = InsightsConnection(config)
    check = registration_check(conn)
    assert isinstance(check, dict)
    assert check['status'] is False
    write_registered_file.assert_not_called()
    write_unregistered_file.assert_not_called()
    write_to_disk.assert_not_called()


@patch('insights.client.connection.generate_machine_id', return_value="xxxx-xxx-xxxx-xxx")
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
@patch("insights.client.connection.InsightsConnection.get", return_value=Mock(status_code=200, content='{"unregistered_at": "2019-04-10"}'))
@patch('insights.client.support.write_registered_file')
@patch('insights.client.support.write_unregistered_file')
@patch('insights.client.support.write_to_disk')
def test_registration_check_legacy_registered_then_unregistered(write_to_disk, write_unregistered_file, write_registered_file, _geturl, _, __, _generate_machine_id):
    '''
    Ensure that connection function is called and data processed.
    Legacy version responded with the unregistered_at as a json parameter.
    Check that when the client get this response the registered file and the machine-id files
    are removed and the unregistered file is created
    '''
    config = Mock(base_url=None, legacy_upload=True)
    conn = InsightsConnection(config)
    check = registration_check(conn)
    assert isinstance(check, dict)
    assert check['status'] is False
    write_registered_file.assert_not_called()
    write_unregistered_file.assert_called_once()


@patch('insights.client.connection.generate_machine_id', return_value="xxxx-xxx-xxxx-xxx")
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
@patch("insights.client.connection.InsightsConnection.get", return_value=Mock(status_code=200, content='{"unregistered_at": null}'))
@patch('insights.client.support.write_registered_file')
@patch('insights.client.support.write_unregistered_file')
def test_registration_check_legacy_registered(write_unregistered_file, write_registered_file, _geturl, _proxy, _session, _generate_machine_id):
    '''
    Ensure that connection function is called and data processed.
    When the systems is registered it get a 200 message with a json with the unregistered_at=null
    Check that when the client get this response the unregistered file is removed
    and the registered file and machine-id exists
    '''
    config = Mock(base_url=None, legacy_upload=True)
    conn = InsightsConnection(config)
    check = registration_check(conn)
    assert isinstance(check, dict)
    assert check['status'] is True
    write_registered_file.assert_called_once()
    write_unregistered_file.assert_not_called()


@patch('insights.client.connection.generate_machine_id', return_value="xxxx-xxx-xxxx-xxx")
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
@patch("insights.client.connection.InsightsConnection.get", return_value=Mock(status_code=502, content='zSDFasfghsRGH'))
@patch('insights.client.support.write_registered_file')
@patch('insights.client.support.write_unregistered_file')
@patch('insights.client.support.write_to_disk')
def test_registration_check_legacy_bad_json(write_to_disk, write_unregistered_file, write_registered_file, _geturl, _, __, _generate_machine_id):
    '''
    Ensure the function does not remove any file if a network error is encountered
    '''
    config = Mock(base_url=None, legacy_upload=True)
    conn = InsightsConnection(config)
    check = registration_check(conn)
    assert isinstance(check, dict)
    assert check['status'] is False
    assert check['unreachable'] is True
    write_registered_file.assert_not_called()
    write_unregistered_file.assert_not_called()
    write_to_disk.assert_not_called()


@patch('insights.client.connection.generate_machine_id', return_value="xxxx-xxx-xxxx-xxx")
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
@patch("insights.client.connection.InsightsConnection.get", return_value=Mock(status_code=502, content='{"details": "Bad gateway"}'))
@patch('insights.client.support.write_registered_file')
@patch('insights.client.support.write_unregistered_file')
@patch('insights.client.support.write_to_disk')
def test_registration_check_legacy_bad_connection(write_to_disk, write_unregistered_file, write_registered_file, _geturl, _, __, _generate_machine_id):
    '''
    Ensure the function does not remove any file if a network error is encountered
    '''
    config = Mock(base_url=None, legacy_upload=True)
    conn = InsightsConnection(config)
    check = registration_check(conn)
    assert isinstance(check, dict)
    assert check['status'] is False
    assert check['unreachable'] is True
    write_registered_file.assert_not_called()
    write_unregistered_file.assert_not_called()
    write_to_disk.assert_not_called()
