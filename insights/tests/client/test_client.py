from contextlib import contextmanager
from shutil import rmtree
import logging
import logging.handlers
import sys
import os
import pytest

from insights.client import InsightsClient
from insights.client.client import get_file_handler
from insights.client.archive import InsightsArchive
from insights.client.config import InsightsConfig
from insights import package_info
from insights.client.constants import InsightsConstants as constants
from mock.mock import patch, Mock, call, ANY
from pytest import mark
from pytest import raises

# Temporary directory to mock registration files
TEMP_TEST_REG_DIR = "/tmp/insights-client-registration"
TEMP_TEST_REG_DIR2 = "/tmp/redhat-access-insights-registration"


@pytest.fixture(autouse=True)
def mock_os_chmod():
    with patch('insights.client.client.os.chmod', Mock()) as os_chmod:
        yield os_chmod


@pytest.fixture(autouse=True)
def mock_os_umask():
    with patch('insights.client.client.os.umask', Mock()) as os_umask:
        yield os_umask


class _mock_InsightsConnection(object):
    '''
    For stubbing out network calls
    '''
    def __init__(self, registered=None):
        self.registered = registered

    def api_registration_check(self):
        # True = registered
        # None = unregistered
        # False = unreachable
        # Legacy code:
        # True = system exists in inventory
        # False = Error connection or parsing response
        # None = Machine is not register
        return self.registered

    def register(self):
        return ('msg', 'hostname', "None", "")

    def unregister(self):
        return True


# @TODO DRY the args hack.

def test_version():

    # Hack to prevent client from parsing args to py.test
    tmp = sys.argv
    sys.argv = []

    try:
        config = InsightsConfig(logging_file='/tmp/insights.log')
        client = InsightsClient(config)
        result = client.version()
        assert result == "%s-%s" % (package_info["VERSION"], package_info["RELEASE"])
    finally:
        sys.argv = tmp


@contextmanager
def _mock_no_register_files():
    # mock a directory with the fresh install files
    if not os.path.exists(TEMP_TEST_REG_DIR):
        os.mkdir(TEMP_TEST_REG_DIR)
    if not os.path.exists(TEMP_TEST_REG_DIR2):
        os.mkdir(TEMP_TEST_REG_DIR2)
    try:
        unregistered_path = os.path.join(TEMP_TEST_REG_DIR, ".unregistered")
        with open(unregistered_path, "w") as unregistered_file:
            unregistered_file.write("date")
        unregistered_path2 = os.path.join(TEMP_TEST_REG_DIR2, ".unregistered")
        with open(unregistered_path2, "w") as unregistered_file:
            unregistered_file.write("date")
        yield
    finally:
        rmtree(TEMP_TEST_REG_DIR)
        rmtree(TEMP_TEST_REG_DIR2)


@contextmanager
def _mock_no_register_files_machineid_present():
    # mock a directory with the fresh install files
    if not os.path.exists(TEMP_TEST_REG_DIR):
        os.mkdir(TEMP_TEST_REG_DIR)
    if not os.path.exists(TEMP_TEST_REG_DIR2):
        os.mkdir(TEMP_TEST_REG_DIR2)
    try:
        unregistered_path = os.path.join(TEMP_TEST_REG_DIR, ".unregistered")
        with open(unregistered_path, "w") as unregistered_file:
            unregistered_file.write("date")
        unregistered_path2 = os.path.join(TEMP_TEST_REG_DIR2, ".unregistered")
        with open(unregistered_path2, "w") as unregistered_file:
            unregistered_file.write("date")
        machine_id_path = os.path.join(TEMP_TEST_REG_DIR, "machine-id")
        with open(machine_id_path, "w") as machine_id_file:
            machine_id_file.write("id")
        yield
    finally:
        rmtree(TEMP_TEST_REG_DIR)
        rmtree(TEMP_TEST_REG_DIR2)


@patch('insights.client.client.os.path.dirname')
@patch('insights.client.client.get_version_info')
def test_get_log_handler_by_client_version(get_version_info, mock_path_dirname):
    '''
    Verify that get_log_handler() returns
    the correct file handler depending on
    the client rpm version.
    '''
    mock_path_dirname.return_value = "mock_dirname"

    # RPM version is older than 3.2.0
    get_version_info.return_value = {'client_version': '3.1.8'}
    conf = InsightsConfig(logging_file='/tmp/insights.log')
    assert isinstance(get_file_handler(conf), logging.handlers.RotatingFileHandler) is True

    # RPM version is 3.2.0
    get_version_info.return_value = {'client_version': '3.2.0'}
    conf = InsightsConfig(logging_file='/tmp/insights.log')
    assert isinstance(get_file_handler(conf), logging.FileHandler) is True

    # RPM version is newer than 3.2.0
    get_version_info.return_value = {'client_version': '3.2.1'}
    conf = InsightsConfig(logging_file='/tmp/insights.log')
    assert isinstance(get_file_handler(conf), logging.FileHandler) is True


@patch('insights.client.client.generate_machine_id')
@patch('insights.client.utilities.delete_unregistered_file')
@patch('insights.client.utilities.write_to_disk')
@patch('insights.client.utilities.constants.registered_files',
       [TEMP_TEST_REG_DIR + '/.registered',
        TEMP_TEST_REG_DIR2 + '/.registered'])
@patch('insights.client.utilities.constants.unregistered_files',
       [TEMP_TEST_REG_DIR + '/.unregistered',
        TEMP_TEST_REG_DIR2 + '/.unregistered'])
@patch('insights.client.utilities.constants.machine_id_file',
       TEMP_TEST_REG_DIR + '/machine-id')
def test_register_legacy(utilities_write, delete_unregistered_file, generate_machine_id):
    config = InsightsConfig(register=True, legacy_upload=True)
    client = InsightsClient(config)
    client.connection = _mock_InsightsConnection(registered=None)
    client.connection.config = config
    client.session = True
    with _mock_no_register_files():
        client.register() is True
    delete_unregistered_file.assert_called_once()
    generate_machine_id.assert_called_once_with()
    utilities_write.assert_has_calls((
        call(constants.registered_files[0]),
        call(constants.registered_files[1])
    ))


@patch('insights.client.client.generate_machine_id')
@patch('insights.client.utilities.delete_unregistered_file')
@patch('insights.client.utilities.write_to_disk')
@patch('insights.client.utilities.constants.registered_files',
       [TEMP_TEST_REG_DIR + '/.registered',
        TEMP_TEST_REG_DIR2 + '/.registered'])
@patch('insights.client.utilities.constants.unregistered_files',
       [TEMP_TEST_REG_DIR + '/.unregistered',
        TEMP_TEST_REG_DIR2 + '/.unregistered'])
@patch('insights.client.utilities.constants.machine_id_file',
       TEMP_TEST_REG_DIR + '/machine-id')
def test_register_legacy_error_machineid(utilities_write, delete_unregistered_file, generate_machine_id):
    config = InsightsConfig(register=True, legacy_upload=True)
    client = InsightsClient(config)
    client.connection = _mock_InsightsConnection(registered=False)
    client.connection.config = config
    client.session = True
    # this should return False
    with _mock_no_register_files_machineid_present():
        client.register() is False
    delete_unregistered_file.assert_not_called()
    generate_machine_id.assert_not_called()


@contextmanager
def _mock_registered_files():
    # mock a directory with the registered files
    if not os.path.exists(TEMP_TEST_REG_DIR):
        os.mkdir(TEMP_TEST_REG_DIR)
    if not os.path.exists(TEMP_TEST_REG_DIR2):
        os.mkdir(TEMP_TEST_REG_DIR2)
    try:
        registered_path = os.path.join(TEMP_TEST_REG_DIR, ".registered")
        with open(registered_path, "w") as registered_file:
            registered_file.write("date")
        machine_id_path = os.path.join(TEMP_TEST_REG_DIR, "machine-id")
        with open(machine_id_path, "w") as machine_id_file:
            machine_id_file.write("id")
        registered_path2 = os.path.join(TEMP_TEST_REG_DIR2, ".registered")
        with open(registered_path2, "w") as registered_file:
            registered_file.write("date")

        yield
    finally:
        rmtree(TEMP_TEST_REG_DIR)
        rmtree(TEMP_TEST_REG_DIR2)


@patch('insights.client.utilities.write_unregistered_file')
@patch('insights.client.utilities.delete_cache_files')
@patch('insights.client.utilities.write_to_disk')
@patch('insights.client.client.write_to_disk')
@patch('insights.client.utilities.get_time', return_value='now')
@patch('insights.client.utilities.constants.registered_files',
       [TEMP_TEST_REG_DIR + '/.registered',
        TEMP_TEST_REG_DIR2 + '/.registered'])
@patch('insights.client.utilities.constants.unregistered_files',
       [TEMP_TEST_REG_DIR + '/.unregistered',
        TEMP_TEST_REG_DIR2 + '/.unregistered'])
@patch('insights.client.utilities.constants.machine_id_file',
       TEMP_TEST_REG_DIR + '/machine-id')
def test_unregister_legacy(date, client_write, utilities_write, _delete_cache_file, _write_unregistered_file):
    config = InsightsConfig(unregister=True, legacy_upload=True)
    client = InsightsClient(config)
    client.connection = _mock_InsightsConnection(registered=True)
    client.connection.config = config
    client.session = True
    with _mock_registered_files():
        assert client.unregister() is True
    client_write.assert_called_once_with(constants.machine_id_file, delete=True)
    utilities_write.assert_has_calls((
        call(constants.registered_files[0], delete=True),
        call(constants.registered_files[1], delete=True),
        call(constants.unregistered_files[0], content=date.return_value),
        call(constants.unregistered_files[1], content=date.return_value)
    ))


def test_register_container():
    with pytest.raises(ValueError):
        InsightsConfig(register=True, analyze_container=True)


def test_unregister_container():
    with pytest.raises(ValueError):
        InsightsConfig(unregister=True, analyze_container=True)


@pytest.mark.skip(reason="Mocked paths not working in QE jenkins")
@patch('insights.client.utilities.constants.registered_files',
       [TEMP_TEST_REG_DIR + '/.registered',
        TEMP_TEST_REG_DIR2 + '/.registered'])
@patch('insights.client.utilities.constants.unregistered_files',
       [TEMP_TEST_REG_DIR + '/.unregistered',
        TEMP_TEST_REG_DIR2 + '/.unregistered'])
@patch('insights.client.utilities.constants.machine_id_file',
       TEMP_TEST_REG_DIR + '/machine-id')
def test_reg_check_registered():

    config = InsightsConfig()
    client = InsightsClient(config)
    client.connection = _mock_InsightsConnection(registered=True)
    client.connection.config = config
    client.session = True

    with _mock_registered_files():
        assert client.get_registration_status()['status'] is True
        for r in constants.registered_files:
            assert os.path.isfile(r) is True
        for u in constants.unregistered_files:
            assert os.path.isfile(u) is False


@patch('insights.client.utilities.constants.registered_files',
       [TEMP_TEST_REG_DIR + '/.registered',
        TEMP_TEST_REG_DIR2 + '/.registered'])
@patch('insights.client.utilities.constants.unregistered_files',
       [TEMP_TEST_REG_DIR + '/.unregistered',
        TEMP_TEST_REG_DIR2 + '/.unregistered'])
@patch('insights.client.utilities.constants.machine_id_file',
       TEMP_TEST_REG_DIR + '/machine-id')
def test_reg_check_unregistered():
    # unregister the machine first
    config = InsightsConfig()
    client = InsightsClient(config)
    client.connection = _mock_InsightsConnection(registered=False)
    client.connection.config = config
    client.session = True

    # test function and integration in .register()
    with _mock_no_register_files():
        assert client.get_registration_status()['status'] is False
        for r in constants.registered_files:
            assert os.path.isfile(r) is False
        for u in constants.unregistered_files:
            assert os.path.isfile(u) is True


@patch('insights.client.utilities.constants.registered_files',
       [TEMP_TEST_REG_DIR + '/.registered',
        TEMP_TEST_REG_DIR2 + '/.registered'])
@patch('insights.client.utilities.constants.unregistered_files',
       [TEMP_TEST_REG_DIR + '/.unregistered',
        TEMP_TEST_REG_DIR2 + '/.unregistered'])
@patch('insights.client.utilities.constants.machine_id_file',
       TEMP_TEST_REG_DIR + '/machine-id')
def test_reg_check_registered_res_unreg_legacy():
    # system is registered but receives the unregistration status
    config = InsightsConfig(legacy_upload=True)
    client = InsightsClient(config)
    client.connection = _mock_InsightsConnection(registered=None)
    client.connection.config = config
    client.session = True

    # test function and integration in .register()
    with _mock_registered_files():
        assert client.get_registration_status()['status'] is False
        for r in constants.registered_files:
            assert os.path.isfile(r) is False
        for u in constants.unregistered_files:
            assert os.path.isfile(u) is True


@patch('insights.client.utilities.constants.registered_files',
       [TEMP_TEST_REG_DIR + '/.registered',
        TEMP_TEST_REG_DIR2 + '/.registered'])
@patch('insights.client.utilities.constants.unregistered_files',
       [TEMP_TEST_REG_DIR + '/.unregistered',
        TEMP_TEST_REG_DIR2 + '/.unregistered'])
@patch('insights.client.utilities.constants.machine_id_file',
       TEMP_TEST_REG_DIR + '/machine-id')
def test_reg_check_registered_res_unreg():
    # system is registered but receives the unregistration status
    config = InsightsConfig(legacy_upload=False)
    client = InsightsClient(config)
    client.connection = _mock_InsightsConnection(registered=False)
    client.connection.config = config
    client.session = True

    # test function and integration in .register()
    with _mock_registered_files():
        assert client.get_registration_status() is False
        for r in constants.registered_files:
            assert os.path.isfile(r) is False
        for u in constants.unregistered_files:
            assert os.path.isfile(u) is True


@patch('insights.client.utilities.constants.registered_files',
       [TEMP_TEST_REG_DIR + '/.registered',
        TEMP_TEST_REG_DIR2 + '/.registered'])
@patch('insights.client.utilities.constants.unregistered_files',
       [TEMP_TEST_REG_DIR + '/.unregistered',
        TEMP_TEST_REG_DIR2 + '/.unregistered'])
@patch('insights.client.utilities.constants.machine_id_file',
       TEMP_TEST_REG_DIR + '/machine-id')
def test_reg_check_registered_unreachable_legacy():
    config = InsightsConfig(legacy_upload=True)
    client = InsightsClient(config)
    client.connection = _mock_InsightsConnection(registered=False)
    client.connection.config = config
    client.session = True

    with _mock_registered_files():
        assert client.get_registration_status()['unreachable'] is True
        for r in constants.registered_files:
            assert os.path.isfile(r) is True
        for u in constants.unregistered_files:
            assert os.path.isfile(u) is False


@patch('insights.client.utilities.constants.registered_files',
       [TEMP_TEST_REG_DIR + '/.registered',
        TEMP_TEST_REG_DIR2 + '/.registered'])
@patch('insights.client.utilities.constants.unregistered_files',
       [TEMP_TEST_REG_DIR + '/.unregistered',
        TEMP_TEST_REG_DIR2 + '/.unregistered'])
@patch('insights.client.utilities.constants.machine_id_file',
       TEMP_TEST_REG_DIR + '/machine-id')
def test_reg_check_registered_unreachable():
    # If it is unreachable do nothing
    config = InsightsConfig(legacy_upload=False)
    client = InsightsClient(config)
    client.connection = _mock_InsightsConnection(registered=None)
    client.connection.config = config
    client.session = True

    with _mock_registered_files():
        assert client.get_registration_status() is None
        for r in constants.registered_files:
            assert os.path.isfile(r) is True
        for u in constants.unregistered_files:
            assert os.path.isfile(u) is False


@patch('insights.client.utilities.constants.registered_files',
       [TEMP_TEST_REG_DIR + '/.registered',
        TEMP_TEST_REG_DIR2 + '/.registered'])
@patch('insights.client.utilities.constants.unregistered_files',
       [TEMP_TEST_REG_DIR + '/.unregistered',
        TEMP_TEST_REG_DIR2 + '/.unregistered'])
@patch('insights.client.utilities.constants.machine_id_file',
       TEMP_TEST_REG_DIR + '/machine-id')
def test_reg_check_unregistered_unreachable():
    config = InsightsConfig(legacy_upload=False)
    client = InsightsClient(config)
    client.connection = _mock_InsightsConnection(registered=False)
    client.connection.config = config
    client.session = True

    with _mock_no_register_files():
        assert client.get_registration_status() is False
        for r in constants.registered_files:
            assert os.path.isfile(r) is False
        for u in constants.unregistered_files:
            assert os.path.isfile(u) is True


@patch('insights.client.utilities.constants.registered_files',
       [TEMP_TEST_REG_DIR + '/.registered',
        TEMP_TEST_REG_DIR2 + '/.registered'])
@patch('insights.client.utilities.constants.unregistered_files',
       [TEMP_TEST_REG_DIR + '/.unregistered',
        TEMP_TEST_REG_DIR2 + '/.unregistered'])
@patch('insights.client.utilities.constants.machine_id_file',
       TEMP_TEST_REG_DIR + '/machine-id')
def test_reg_check_unregistered_unreachable_legacy():
    config = InsightsConfig(legacy_upload=True)
    client = InsightsClient(config)
    client.connection = _mock_InsightsConnection(registered=False)
    client.connection.config = config
    client.session = True

    with _mock_no_register_files():
        assert client.get_registration_status()['unreachable'] is True
        for r in constants.registered_files:
            assert os.path.isfile(r) is False
        for u in constants.unregistered_files:
            assert os.path.isfile(u) is True


@patch('insights.client.client.constants.sleep_time', 0)
@patch('insights.client.client.InsightsConnection.upload_archive',
       return_value=Mock(status_code=500))
@patch('insights.client.os.path.exists', return_value=True)
@patch("insights.client.client.logger")
def test_upload_500_retry(logger, _, upload_archive):

    # Hack to prevent client from parsing args to py.test
    tmp = sys.argv
    sys.argv = []

    try:
        retries = 3

        config = InsightsConfig(logging_file='/tmp/insights.log', retries=retries)
        client = InsightsClient(config)
        with pytest.raises(RuntimeError):
            client.upload('/tmp/insights.tar.gz')

        upload_archive.assert_called()
        assert upload_archive.call_count == retries
        logger.error.assert_any_call("Upload attempt %d of %d failed! Reason: %s", 1, config.retries, ANY)
        logger.error.assert_called_with("All attempts to upload have failed!")
    finally:
        sys.argv = tmp


@patch('insights.client.client.constants.sleep_time', 0)
@patch('insights.client.client.InsightsConnection.upload_archive')
@patch("insights.client.client.logger")
def test_upload_exception_retry(logger, upload_archive):
    from requests.exceptions import ConnectionError, ProxyError, Timeout, HTTPError, SSLError
    upload_archive.side_effect = [ConnectionError("Connection Error"),
                                  ProxyError("Proxy Error"),
                                  Timeout("Timeout Error")]
    retries = 3

    config = InsightsConfig(legacy_upload=False, logging_file='/tmp/insights.log', retries=retries)
    client = InsightsClient(config)
    with patch('insights.client.os.path.exists', return_value=True):
        with pytest.raises(RuntimeError):
            client.upload('/tmp/insights.tar.gz')
    assert upload_archive.call_count == retries
    logger.debug.assert_any_call("Upload attempt %d of %d ...", 1, config.retries)
    logger.error.assert_any_call("Upload attempt %d of %d failed! Reason: %s", 1, config.retries, "Connection Error")
    logger.error.assert_any_call("Upload attempt %d of %d failed! Reason: %s", 2, config.retries, "Proxy Error")
    logger.error.assert_any_call("Upload attempt %d of %d failed! Reason: %s", 3, config.retries, "Timeout Error")
    logger.error.assert_called_with("All attempts to upload have failed!")

    # Test legacy uploads
    logger.reset_mock()
    upload_archive.reset_mock()
    upload_archive.side_effect = [HTTPError("HTTP Error"),
                                  SSLError("SSL Error")]
    retries = 2
    config = InsightsConfig(legacy_upload=True, logging_file='/tmp/insights.log', retries=retries)
    client = InsightsClient(config)
    with patch('insights.client.os.path.exists', return_value=True):
        with pytest.raises(RuntimeError):
            client.upload('/tmp/insights.tar.gz')
    assert upload_archive.call_count == retries
    logger.debug.assert_any_call("Legacy upload attempt %d of %d ...", 1, config.retries)
    logger.error.assert_any_call("Upload attempt %d of %d failed! Reason: %s", 1, config.retries, "HTTP Error")
    logger.error.assert_any_call("Upload attempt %d of %d failed! Reason: %s", 2, config.retries, "SSL Error")
    logger.error.assert_called_with("All attempts to upload have failed!")


@patch('insights.client.client.InsightsConnection.handle_fail_rcs')
@patch('insights.client.client.InsightsConnection.upload_archive',
       return_value=Mock(status_code=412))
@patch('insights.client.os.path.exists', return_value=True)
def test_upload_412_no_retry(_, upload_archive, handle_fail_rcs):

    # Hack to prevent client from parsing args to py.test
    tmp = sys.argv
    sys.argv = []

    try:
        config = InsightsConfig(logging_file='/tmp/insights.log', retries=3)
        client = InsightsClient(config)
        with pytest.raises(RuntimeError):
            client.upload('/tmp/insights.tar.gz')

        upload_archive.assert_called_once()
    finally:
        sys.argv = tmp


@patch('insights.client.connection.write_unregistered_file')
@patch('insights.client.client.InsightsConnection.upload_archive',
       return_value=Mock(**{"status_code": 412,
                            "json.return_value": {"unregistered_at": "now", "message": "msg"}}))
@patch('insights.client.os.path.exists', return_value=True)
def test_upload_412_write_unregistered_file(_, upload_archive, write_unregistered_file):

    # Hack to prevent client from parsing args to py.test
    tmp = sys.argv
    sys.argv = []

    try:
        config = InsightsConfig(logging_file='/tmp/insights.log', retries=3)
        client = InsightsClient(config)
        with pytest.raises(RuntimeError):
            client.upload('/tmp/insights.tar.gz')

        unregistered_at = upload_archive.return_value.json()["unregistered_at"]
        write_unregistered_file.assert_called_once_with(unregistered_at)
    finally:
        sys.argv = tmp


@patch('insights.client.archive.InsightsArchive.storing_archive')
@patch('insights.client.archive.tempfile.mkdtemp', Mock())
@patch('insights.client.archive.os.makedirs', Mock())
@patch('insights.client.archive.atexit', Mock())
def test_cleanup_tmp(storing_archive):
    config = InsightsConfig(keep_archive=False)
    arch = InsightsArchive(config)
    arch.tmp_dir = "/test"
    arch.tar_file = "/test/test.tar.gz"
    arch.keep_archive_dir = "/test-keep-archive"
    arch.cleanup_tmp()
    assert not os.path.exists(arch.tmp_dir)
    storing_archive.assert_not_called()

    config.keep_archive = True
    arch.cleanup_tmp()
    assert not os.path.exists(arch.tmp_dir)
    storing_archive.assert_called_once()


@patch('insights.client.archive.InsightsArchive.storing_archive')
@patch('insights.client.archive.tempfile.mkdtemp', Mock())
@patch('insights.client.archive.os.makedirs', Mock())
@patch('insights.client.archive.atexit', Mock())
def test_cleanup_tmp_obfuscation(storing_archive):
    config = InsightsConfig(keep_archive=False, obfuscate=True)
    arch = InsightsArchive(config)
    arch.tmp_dir = '/var/tmp/insights-archive-000000'
    arch.tar_file = '/var/tmp/insights-archive-test.tar.gz'
    arch.keep_archive_dir = '/var/tmp/test-archive'
    arch.cleanup_tmp()
    assert not os.path.exists(arch.tmp_dir)
    storing_archive.assert_not_called()

    arch.config.keep_archive = True
    arch.cleanup_tmp()
    assert not os.path.exists(arch.tmp_dir)
    storing_archive.assert_called_once()


@patch('insights.client.client._legacy_handle_registration')
def test_legacy_register(_legacy_handle_registration):
    '''
    _legacy_handle_registration called when legacy upload
    '''
    config = InsightsConfig(legacy_upload=True)
    client = InsightsClient(config)
    client.register()
    _legacy_handle_registration.assert_called_once()


@patch('insights.client.client._legacy_handle_unregistration')
def test_legacy_unregister(_legacy_handle_unregistration):
    '''
    _legacy_handle_unregistration called when legacy upload
    '''
    config = InsightsConfig(legacy_upload=True)
    client = InsightsClient(config)
    client.unregister()
    _legacy_handle_unregistration.assert_called_once()


@patch('insights.client.client.handle_registration')
def test_register_upload(handle_registration):
    '''
    handle_registration called when upload
    '''
    config = InsightsConfig(legacy_upload=False)
    client = InsightsClient(config)
    client.register()
    handle_registration.assert_called_once()


@patch('insights.client.client.handle_unregistration')
def test_unregister_upload(handle_unregistration):
    '''
    handle_unregistration called when upload
    '''
    config = InsightsConfig(legacy_upload=False)
    client = InsightsClient(config)
    client.unregister()
    handle_unregistration.assert_called_once()


@patch('insights.client.os.path.exists', return_value=True)
@patch('insights.client.connection.InsightsConnection.upload_archive', Mock(return_value=Mock(status_code=200)))
@patch('insights.client.client._legacy_upload')
@patch('insights.client.client.write_to_disk', Mock())
def test_legacy_upload(_legacy_upload, path_exists):
    '''
    _legacy_upload called when legacy upload
    '''
    config = InsightsConfig(legacy_upload=True)
    client = InsightsClient(config)
    client.upload('test.gar.gz', 'test.content.type')
    _legacy_upload.assert_called_once()


@patch('insights.client.os.path.exists', return_value=True)
@patch('insights.client.connection.InsightsConnection.upload_archive', Mock(return_value=Mock(status_code=200)))
@patch('insights.client.client._legacy_upload')
@patch('insights.client.client.write_to_disk', Mock())
def test_platform_upload(_legacy_upload, path_exists):
    '''
    _legacy_upload not called when platform upload
    '''
    config = InsightsConfig(legacy_upload=False)
    client = InsightsClient(config)
    client.upload('test.gar.gz', 'test.content.type')
    _legacy_upload.assert_not_called()


@patch('insights.client.os.path.exists', return_value=True)
@patch('insights.client.connection.InsightsConnection.upload_archive', return_value=Mock(status_code=200))
@patch('insights.client.client._legacy_upload')
def test_platform_upload_with_no_log_path(_legacy_upload, _, path_exists):
    '''
    testing logger when no path is given
    '''
    config = InsightsConfig(legacy_upload=True, logging_file='tmp.log')
    client = InsightsClient(config)
    response = client.upload('test.gar.gz', 'test.content.type')
    _legacy_upload.assert_called_once()
    assert response is not None


@patch('insights.client.InsightsClient._copy_soscleaner_files')
@patch('insights.client.shutil')
def test_copy_to_output_dir(shutil_, _copy_soscleaner_files):
    '''
    Test that shutil is called to copy the collection to
    the specified output dir
    '''
    config = InsightsConfig()
    client = InsightsClient(config)
    client.copy_to_output_dir('test')
    shutil_.copytree.assert_called_once()
    _copy_soscleaner_files.assert_not_called()


@patch('insights.client.InsightsClient._copy_soscleaner_files')
@patch('insights.client.shutil')
def test_copy_to_output_dir_obfuscate_on(shutil_, _copy_soscleaner_files):
    '''
    Test that shutil is called to copy the collection to
    the specified output dir, and soscleaner copy function
    is called
    '''
    # obfuscate off, no soscleaner files
    config = InsightsConfig(obfuscate=True)
    client = InsightsClient(config)
    client.copy_to_output_dir('test')
    shutil_.copytree.assert_called_once()
    _copy_soscleaner_files.assert_called_once()


@patch('insights.client.InsightsClient._copy_soscleaner_files')
@patch('insights.client.shutil')
@patch('insights.client.os')
def test_copy_to_output_dir_exists_and_empty(os_, shutil_, _copy_soscleaner_files):
    '''
    Test that writing to an existing but empty directory is
    performed
    '''
    config = InsightsConfig(output_dir='dest')
    client = InsightsClient(config)
    # raise file exists error first, then raise for "b" and "c" below
    shutil_.copytree.side_effect = [OSError(17, 'File exists'), None, None]

    # returns empty list for destination, file list for source
    os_.listdir.side_effect = [[], ['a', 'b', 'c']]

    # os.path.join called 6 times, once for each file per src and dest
    os_.path.join.side_effect = [
        os.path.join('src', 'a'),
        os.path.join(config.output_dir, 'a'),
        os.path.join('src', 'b'),
        os.path.join(config.output_dir, 'b'),
        os.path.join('src', 'c'),
        os.path.join(config.output_dir, 'c')]

    # 'a' is file, 'b', 'c' are dirs
    os_.path.isfile.side_effect = [True, False, False]
    # a is file so the check for 'a' does not fall through to the elif
    os_.path.isdir.side_effect = [True, True]

    client.copy_to_output_dir('src')

    os_.listdir.assert_has_calls([call(config.output_dir), call('src')])
    os_.path.isfile.assert_has_calls([call('src/a'), call('src/b'), call('src/c')])
    # a is file so the check for 'a' does not fall through to the elif
    os_.path.isdir.assert_has_calls([call('src/b'), call('src/c')])
    # initial (failed) copy is part of the calls
    shutil_.copytree.assert_has_calls([
        call('src', config.output_dir),
        call(os.path.join('src', 'b'), os.path.join(config.output_dir, 'b')),
        call(os.path.join('src', 'c'), os.path.join(config.output_dir, 'c'))])
    shutil_.copyfile.assert_has_calls([
        call(os.path.join('src', 'a'), os.path.join(config.output_dir, 'a'))])
    _copy_soscleaner_files.assert_not_called()


@patch('insights.client.InsightsClient._copy_soscleaner_files')
@patch('insights.client.shutil')
@patch('insights.client.os')
def test_copy_to_output_dir_exists_and_empty_err_during_copy(os_, shutil_, _copy_soscleaner_files):
    '''
    Test that when writing to an existing but empty directory,
    if an error occurs, we bail out before finishing.
    '''
    config = InsightsConfig(output_dir='dest')
    client = InsightsClient(config)
    # raise file exists error first, then raise nothing for "b" and "c" below
    shutil_.copytree.side_effect = [OSError(17, 'File exists'), None, None]

    # raise an unknown error for "a"
    shutil_.copyfile.side_effect = [OSError(19, '???'), None, None]

    # returns empty list for destination, file list for source
    os_.listdir.side_effect = [[], ['a', 'b', 'c']]

    # os.path.join called 6 times, once for each file per src and dest
    os_.path.join.side_effect = [
        os.path.join('src', 'a'),
        os.path.join(config.output_dir, 'a'),
        os.path.join('src', 'b'),
        os.path.join(config.output_dir, 'b'),
        os.path.join('src', 'c'),
        os.path.join(config.output_dir, 'c')]

    # 'a' is file, 'b', 'c' are dirs
    os_.path.isfile.side_effect = [True, False, False]
    # a is file so the check for 'a' does not fall through to the elif
    os_.path.isdir.side_effect = [True, True]

    client.copy_to_output_dir('src')

    os_.listdir.assert_has_calls([call(config.output_dir), call('src')])
    os_.path.isfile.assert_has_calls([call('src/a')])
    # a is file so the check for 'a' does not fall through to the elif
    os_.path.isdir.assert_not_called()
    # initial (failed) copy is part of the calls
    shutil_.copytree.assert_has_calls([call('src', config.output_dir)])
    shutil_.copyfile.assert_has_calls([
        call(os.path.join('src', 'a'), os.path.join(config.output_dir, 'a'))])
    _copy_soscleaner_files.assert_not_called()


@patch('insights.client.InsightsClient._copy_soscleaner_files')
@patch('insights.client.shutil')
@patch('insights.client.os')
def test_copy_to_output_dir_exists_and_not_empty(os_, shutil_, _copy_soscleaner_files):
    '''
    Test that writing to an existing and non-empty directory is
    NOT performed. Due to the check in config.py this should never happen,
    but just to be safe.
    '''
    config = InsightsConfig(output_dir='dest')
    client = InsightsClient(config)
    shutil_.copytree.side_effect = [OSError(17, 'File exists')]

    os_.listdir.return_value = ['test']

    client.copy_to_output_dir('src')

    os_.listdir.assert_called_once_with(config.output_dir)
    shutil_.copytree.assert_called_once_with('src', config.output_dir)
    shutil_.copyfile.assert_not_called()


@patch('insights.client.InsightsClient._copy_soscleaner_files')
@patch('insights.client.shutil')
@patch('insights.client.os')
def test_copy_to_output_dir_other_oserror(os_, shutil_, _copy_soscleaner_files):
    '''
    Test that any OSError != 17 is logged and we bail out
    before attempting to copy anything else
    '''
    config = InsightsConfig(output_dir='dest')
    client = InsightsClient(config)
    shutil_.copytree.side_effect = [OSError(19, '???'), None, None]

    client.copy_to_output_dir('src')

    os_.listdir.assert_not_called
    shutil_.copytree.assert_called_once_with('src', config.output_dir)
    shutil_.copyfile.assert_not_called()


@patch('insights.client.InsightsClient._copy_soscleaner_files')
@patch('insights.client.shutil')
def test_copy_to_output_file(shutil_, _copy_soscleaner_files):
    '''
    Test that shutil is called to copy the collection to
    the specified output file
    '''
    config = InsightsConfig()
    client = InsightsClient(config)
    client.copy_to_output_file('test')
    shutil_.copyfile.assert_called_once()
    _copy_soscleaner_files.assert_not_called()


@patch('insights.client.InsightsClient._copy_soscleaner_files')
@patch('insights.client.shutil')
def test_copy_to_output_file_obfuscate_on(shutil_, _copy_soscleaner_files):
    '''
    Test that shutil is called to copy the collection to
    the specified output file, and soscleaner copy function
    is called
    '''
    # obfuscate off, no soscleaner files
    config = InsightsConfig(obfuscate=True)
    client = InsightsClient(config)
    client.copy_to_output_file('test')
    shutil_.copyfile.assert_called_once()
    _copy_soscleaner_files.assert_called_once()


@mark.parametrize(("expected_result",), ((True,), (None,)))
def test_checkin_result(expected_result):
    config = InsightsConfig()
    client = InsightsClient(config)
    client.connection = Mock(**{"checkin.return_value": expected_result})
    client.session = True

    actual_result = client.checkin()
    client.connection.checkin.assert_called_once_with()
    assert actual_result is expected_result


def test_checkin_error():
    config = InsightsConfig()
    client = InsightsClient(config)
    client.connection = Mock(**{"checkin.side_effect": Exception})
    client.session = True

    with raises(Exception):
        client.checkin()

    client.connection.checkin.assert_called_once_with()


def test_checkin_offline():
    config = InsightsConfig(offline=True)
    client = InsightsClient(config)
    client.connection = Mock()

    result = client.checkin()
    assert result is None
    client.connection.checkin.assert_not_called()
