import sys
import os
import pytest
import time

from insights.client import InsightsClient
from insights.client.config import InsightsConfig
from insights import package_info
from insights.client.constants import InsightsConstants as constants
from insights.client.utilities import generate_machine_id
from mock.mock import patch
from mock.mock import Mock


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
    assert client.get_registation_status()['status'] is True
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
    assert client.get_registation_status()['status'] is False
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
    assert client.get_registation_status()['unreachable'] is True
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
    assert client.get_registation_status()['unreachable'] is True
    assert client.register() is None
    for r in constants.registered_files:
        assert os.path.isfile(r) is False
    for u in constants.unregistered_files:
        assert os.path.isfile(u) is True


@patch('insights.client.client.constants.sleep_time', 0)
@patch('insights.client.client.InsightsConnection.upload_archive',
       return_value=Mock(status_code=500))
def test_upload_500_retry(upload_archive):

    # Hack to prevent client from parsing args to py.test
    tmp = sys.argv
    sys.argv = []

    try:
        retries = 3

        config = InsightsConfig(logging_file='/tmp/insights.log', retries=retries)
        client = InsightsClient(config)
        client.upload('/tmp/insights.tar.gz')

        upload_archive.assert_called()
        assert upload_archive.call_count == retries
    finally:
        sys.argv = tmp


@patch('insights.client.client.InsightsConnection.handle_fail_rcs')
@patch('insights.client.client.InsightsConnection.upload_archive',
       return_value=Mock(status_code=412))
def test_upload_412_no_retry(upload_archive, handle_fail_rcs):

    # Hack to prevent client from parsing args to py.test
    tmp = sys.argv
    sys.argv = []

    try:
        config = InsightsConfig(logging_file='/tmp/insights.log', retries=3)
        client = InsightsClient(config)
        client.upload('/tmp/insights.tar.gz')

        upload_archive.assert_called_once()
    finally:
        sys.argv = tmp


@patch('insights.client.connection.write_unregistered_file')
@patch('insights.client.client.InsightsConnection.upload_archive',
       return_value=Mock(**{"status_code": 412,
                            "json.return_value": {"unregistered_at": "now", "message": "msg"}}))
def test_upload_412_write_unregistered_file(upload_archive, write_unregistered_file):

    # Hack to prevent client from parsing args to py.test
    tmp = sys.argv
    sys.argv = []

    try:
        config = InsightsConfig(logging_file='/tmp/insights.log', retries=3)
        client = InsightsClient(config)
        client.upload('/tmp/insights.tar.gz')

        unregistered_at = upload_archive.return_value.json()["unregistered_at"]
        write_unregistered_file.assert_called_once_with(unregistered_at)
    finally:
        sys.argv = tmp
