import sys
import os
import pytest
import time

from insights.client import InsightsClient
from insights.client.archive import InsightsArchive
from insights.client.config import InsightsConfig
from insights import package_info
from insights.client.constants import InsightsConstants as constants
from insights.client.utilities import generate_machine_id
from mock.mock import patch, Mock, call
from pytest import mark
from pytest import raises


@pytest.fixture(autouse=True)
def mock_os_chmod():
    with patch('insights.client.client.os.chmod', Mock()) as os_chmod:
        yield os_chmod


@pytest.fixture(autouse=True)
def mock_os_umask():
    with patch('insights.client.client.os.umask', Mock()) as os_umask:
        yield os_umask


class FakeConnection(object):
    '''
    For stubbing out network calls
    '''
    def __init__(self, registered=None):
        self.registered = registered

    def api_registration_check(self):
        # True = registered
        # None or string = unregistered
        # False = unreachable
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


@pytest.mark.skip(reason="Mocked paths not working in QE jenkins")
@patch('insights.client.utilities.constants.registered_files',
       ['/tmp/insights-client.registered',
        '/tmp/redhat-access-insights.registered'])
@patch('insights.client.utilities.constants.unregistered_files',
       ['/tmp/insights-client.unregistered',
        '/tmp/redhat-access-insights.unregistered'])
@patch('insights.client.utilities.constants.machine_id_file',
       '/tmp/machine-id')
def test_register():
    config = InsightsConfig(register=True)
    client = InsightsClient(config)
    client.connection = FakeConnection()
    client.session = True
    assert client.register() is True
    for r in constants.registered_files:
        assert os.path.isfile(r) is True
    for u in constants.unregistered_files:
        assert os.path.isfile(u) is False


@pytest.mark.skip(reason="Mocked paths not working in QE jenkins")
@patch('insights.client.utilities.constants.registered_files',
       ['/tmp/insights-client.registered',
        '/tmp/redhat-access-insights.registered'])
@patch('insights.client.utilities.constants.unregistered_files',
       ['/tmp/insights-client.unregistered',
        '/tmp/redhat-access-insights.unregistered'])
@patch('insights.client.utilities.constants.machine_id_file',
       '/tmp/machine-id')
def test_unregister():
    config = InsightsConfig(unregister=True)
    client = InsightsClient(config)
    client.connection = FakeConnection(registered=True)
    client.session = True
    assert client.unregister() is True
    for r in constants.registered_files:
        assert os.path.isfile(r) is False
    for u in constants.unregistered_files:
        assert os.path.isfile(u) is True


@pytest.mark.skip(reason="Mocked paths not working in QE jenkins")
@patch('insights.client.utilities.constants.registered_files',
       ['/tmp/insights-client.registered',
        '/tmp/redhat-access-insights.registered'])
@patch('insights.client.utilities.constants.unregistered_files',
       ['/tmp/insights-client.unregistered',
        '/tmp/redhat-access-insights.unregistered'])
@patch('insights.client.utilities.constants.machine_id_file',
       '/tmp/machine-id')
def test_force_reregister():
    config = InsightsConfig(reregister=True)
    client = InsightsClient(config)
    client.connection = FakeConnection(registered=None)
    client.session = True

    # initialize comparisons
    old_machine_id = None
    new_machine_id = None

    # register first
    assert client.register() is True
    for r in constants.registered_files:
        assert os.path.isfile(r) is True

    # get modified time of .registered to ensure it's regenerated
    old_reg_file1_ts = os.path.getmtime(constants.registered_files[0])
    old_reg_file2_ts = os.path.getmtime(constants.registered_files[1])

    old_machine_id = generate_machine_id()

    # wait to allow for timestamp difference
    time.sleep(3)

    # reregister with new machine-id
    client.connection = FakeConnection(registered=True)
    config.reregister = True
    assert client.register() is True

    new_machine_id = generate_machine_id()
    new_reg_file1_ts = os.path.getmtime(constants.registered_files[0])
    new_reg_file2_ts = os.path.getmtime(constants.registered_files[1])

    assert old_machine_id != new_machine_id
    assert old_reg_file1_ts != new_reg_file1_ts
    assert old_reg_file2_ts != new_reg_file2_ts


def test_register_container():
    with pytest.raises(ValueError):
        InsightsConfig(register=True, analyze_container=True)


def test_unregister_container():
    with pytest.raises(ValueError):
        InsightsConfig(unregister=True, analyze_container=True)


def test_force_reregister_container():
    with pytest.raises(ValueError):
        InsightsConfig(reregister=True, analyze_container=True)


@pytest.mark.skip(reason="Mocked paths not working in QE jenkins")
@patch('insights.client.utilities.constants.registered_files',
       ['/tmp/insights-client.registered',
        '/tmp/redhat-access-insights.registered'])
@patch('insights.client.utilities.constants.unregistered_files',
       ['/tmp/insights-client.unregistered',
        '/tmp/redhat-access-insights.unregistered'])
@patch('insights.client.utilities.constants.machine_id_file',
       '/tmp/machine-id')
def test_reg_check_registered():
    # register the machine first
    config = InsightsConfig()
    client = InsightsClient(config)
    client.connection = FakeConnection(registered=True)
    client.session = True

    # test function and integration in .register()
    assert client.get_registration_status()['status'] is True
    assert client.register() is True
    for r in constants.registered_files:
        assert os.path.isfile(r) is True
    for u in constants.unregistered_files:
        assert os.path.isfile(u) is False


@pytest.mark.skip(reason="Mocked paths not working in QE jenkins")
@patch('insights.client.utilities.constants.registered_files',
       ['/tmp/insights-client.registered',
        '/tmp/redhat-access-insights.registered'])
@patch('insights.client.utilities.constants.unregistered_files',
       ['/tmp/insights-client.unregistered',
        '/tmp/redhat-access-insights.unregistered'])
@patch('insights.client.utilities.constants.machine_id_file',
       '/tmp/machine-id')
def test_reg_check_unregistered():
    # unregister the machine first
    config = InsightsConfig()
    client = InsightsClient(config)
    client.connection = FakeConnection(registered='unregistered')
    client.session = True

    # test function and integration in .register()
    assert client.get_registration_status()['status'] is False
    assert client.register() is False
    for r in constants.registered_files:
        assert os.path.isfile(r) is False
    for u in constants.unregistered_files:
        assert os.path.isfile(u) is True


@pytest.mark.skip(reason="Mocked paths not working in QE jenkins")
@patch('insights.client.utilities.constants.registered_files',
       ['/tmp/insights-client.registered',
        '/tmp/redhat-access-insights.registered'])
@patch('insights.client.utilities.constants.unregistered_files',
       ['/tmp/insights-client.unregistered',
        '/tmp/redhat-access-insights.unregistered'])
@patch('insights.client.utilities.constants.machine_id_file',
       '/tmp/machine-id')
def test_reg_check_registered_unreachable():
    # register the machine first
    config = InsightsConfig(register=True)
    client = InsightsClient(config)
    client.connection = FakeConnection(registered=None)
    client.session = True
    assert client.register() is True

    # reset config and try to check registration
    config.register = False
    client.connection = FakeConnection(registered=False)
    assert client.get_registration_status()['unreachable'] is True
    assert client.register() is None
    for r in constants.registered_files:
        assert os.path.isfile(r) is True
    for u in constants.unregistered_files:
        assert os.path.isfile(u) is False


@pytest.mark.skip(reason="Mocked paths not working in QE jenkins")
@patch('insights.client.utilities.constants.registered_files',
       ['/tmp/insights-client.registered',
        '/tmp/redhat-access-insights.registered'])
@patch('insights.client.utilities.constants.unregistered_files',
       ['/tmp/insights-client.unregistered',
        '/tmp/redhat-access-insights.unregistered'])
@patch('insights.client.utilities.constants.machine_id_file',
       '/tmp/machine-id')
def test_reg_check_unregistered_unreachable():
    # unregister the machine first
    config = InsightsConfig(unregister=True)
    client = InsightsClient(config)
    client.connection = FakeConnection(registered=True)
    client.session = True
    assert client.unregister() is True

    # reset config and try to check registration
    config.unregister = False
    client.connection = FakeConnection(registered=False)
    assert client.get_registration_status()['unreachable'] is True
    assert client.register() is None
    for r in constants.registered_files:
        assert os.path.isfile(r) is False
    for u in constants.unregistered_files:
        assert os.path.isfile(u) is True


@patch('insights.client.client.constants.sleep_time', 0)
@patch('insights.client.client.InsightsConnection.upload_archive',
       return_value=Mock(status_code=500))
@patch('insights.client.os.path.exists', return_value=True)
def test_upload_500_retry(_, upload_archive):

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
    finally:
        sys.argv = tmp


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
def test_cleanup_tmp(storing_archive):
    config = InsightsConfig(keep_archive=False)
    arch = InsightsArchive(config)
    arch.tar_file = os.path.join(arch.tmp_dir, 'test.tar.gz')
    arch.cleanup_tmp()
    assert not os.path.exists(arch.tmp_dir)
    storing_archive.assert_not_called()

    config.keep_archive = True
    arch.cleanup_tmp()
    assert not os.path.exists(arch.tmp_dir)
    storing_archive.assert_called_once()


@patch('insights.client.archive.InsightsArchive.storing_archive')
def test_cleanup_tmp_obfuscation(storing_archive):
    config = InsightsConfig(keep_archive=False, obfuscate=True)
    arch = InsightsArchive(config)
    arch.tar_file = os.path.join(arch.tmp_dir, 'test.tar.gz')
    arch.cleanup_tmp()
    assert not os.path.exists(arch.tmp_dir)
    storing_archive.assert_not_called()

    config.keep_archive = True
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
