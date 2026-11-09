# -*- coding: UTF-8 -*-

from insights.client.config import InsightsConfig
from insights.client.connection import InsightsConnection
from insights.client.support import InsightsSupport, registration_check
from insights.client.constants import InsightsConstants as constants
from unittest.mock import Mock, patch


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


@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
@patch("insights.client.connection.InsightsConnection.api_registration_check", return_value=False)
@patch("insights.client.support.machine_id_exists", return_value=True)
@patch("os.path.exists", side_effect=lambda path: path == constants.registered_files[0])
def test_registration_check_registered_no_inventory(mock_os_path_exists, machine_id_exists, api_registration_check, get_proxies, _init_session):
    '''
    Test the registration check function when the system does not exist in Inventory,
    but the machine-id and .registered files are present locally on the system.
    '''
    config = Mock(base_url=None, legacy_upload=False)
    conn = InsightsConnection(config)
    check = registration_check(conn)
    assert check is True


@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
@patch("insights.client.connection.os.path.isfile", return_value=False)
@patch("insights.client.support.write_registered_file")
@patch("insights.client.support.write_unregistered_file")
@patch("insights.client.support.write_to_disk")
def test_registration_check_legacy_not_registered_locally(
    write_to_disk,
    write_unregistered_file,
    write_registered_file,
    _conn_isfile,
    _proxies,
    _init_session,
):
    """No local .registered marker: treat as unregistered and do not GET /v1/systems."""
    config = Mock(base_url=None, legacy_upload=True)
    conn = InsightsConnection(config)
    conn.get = Mock()
    check = registration_check(conn)
    assert check is False
    conn.get.assert_not_called()
    write_registered_file.assert_not_called()
    write_unregistered_file.assert_called_once()
    write_to_disk.assert_called_once()


@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
@patch("insights.client.connection.os.path.isfile", return_value=True)
@patch("insights.client.support.write_registered_file")
@patch("insights.client.support.write_unregistered_file")
def test_registration_check_legacy_registered_locally(
    write_unregistered_file,
    write_registered_file,
    _conn_isfile,
    _proxies,
    _init_session,
):
    """Local .registered marker: treat as registered and do not GET /v1/systems."""
    config = Mock(base_url=None, legacy_upload=True)
    conn = InsightsConnection(config)
    conn.get = Mock()
    check = registration_check(conn)
    assert check is True
    conn.get.assert_not_called()
    write_registered_file.assert_called_once()
    write_unregistered_file.assert_not_called()
