import os
import tempfile
import uuid
import insights.client.utilities as util
from insights.client.constants import InsightsConstants as constants
import re
import mock
import six
from mock.mock import patch


machine_id = str(uuid.uuid4())
remove_file_content = """
[remove]
foo = bar
potato = pancake
""".strip().encode("utf-8")


def test_display_name():
    assert util.determine_hostname(display_name='foo') == 'foo'


def test_determine_hostname():
    import socket
    hostname = socket.gethostname()
    fqdn = socket.getfqdn()
    assert util.determine_hostname() in (hostname, fqdn)
    assert util.determine_hostname() != 'foo'


def test_get_time():
    time_regex = re.match('\d{4}-\d{2}-\d{2}\D\d{2}:\d{2}:\d{2}\.\d+',
                          util.get_time())
    assert time_regex.group(0) is not None


def test_write_to_disk():
    content = 'boop'
    filename = '/tmp/testing'
    util.write_to_disk(filename, content=content)
    assert os.path.isfile(filename)
    with open(filename, 'r') as f:
        result = f.read()
    assert result == 'boop'
    util.write_to_disk(filename, delete=True) is None


def test_generate_machine_id():
    machine_id_regex = re.match('\w{8}-\w{4}-\w{4}-\w{4}-\w{12}',
                                util.generate_machine_id(destination_file='/tmp/testmachineid'))
    assert machine_id_regex.group(0) is not None
    with open('/tmp/testmachineid', 'r') as _file:
        machine_id = _file.read()
    assert util.generate_machine_id(destination_file='/tmp/testmachineid') == machine_id
    os.remove('/tmp/testmachineid')


def test_expand_paths():
    assert util._expand_paths('/tmp') == ['/tmp']


def test_magic_plan_b():
    tf = tempfile.NamedTemporaryFile()
    with open(tf.name, 'w') as f:
        f.write('testing stuff')
    assert util.magic_plan_b(tf.name) == 'text/plain; charset=us-ascii'


def test_run_command_get_output():
    cmd = 'echo hello'
    assert util.run_command_get_output(cmd) == {'status': 0, 'output': u'hello\n'}


@patch('insights.client.utilities.run_command_get_output')
@patch.dict('insights.client.utilities.package_info', {'VERSION': '1', 'RELEASE': '1'})
def test_get_version_info(run_command_get_output):
    # package_info['VERSION'] = '1'
    # package_info['RELEASE'] = '1'
    run_command_get_output.return_value = {'output': 1, 'status': 0}
    version_info = util.get_version_info()
    assert version_info == {'core_version': '1-1', 'client_version': 1}


def test_validate_remove_file():
    tf = '/tmp/remove.cfg'
    with open(tf, 'wb') as f:
        f.write(remove_file_content)
    assert util.validate_remove_file(remove_file='/tmp/boop') is False
    os.chmod(tf, 0o644)
    assert util.validate_remove_file(remove_file=tf) is False
    os.chmod(tf, 0o600)
    assert util.validate_remove_file(remove_file=tf) is not False
    os.remove(tf)

# TODO: DRY


@patch('insights.client.utilities.constants.registered_files',
       ['/tmp/insights-client.registered',
        '/tmp/redhat-access-insights.registered'])
@patch('insights.client.utilities.constants.unregistered_files',
       ['/tmp/insights-client.unregistered',
        '/tmp/redhat-access-insights.unregistered'])
def test_write_registered_file():
    util.write_registered_file()
    for r in constants.registered_files:
        assert os.path.isfile(r) is True
    for u in constants.unregistered_files:
        assert os.path.isfile(u) is False


@patch('insights.client.utilities.constants.registered_files',
       ['/tmp/insights-client.registered',
        '/tmp/redhat-access-insights.registered'])
@patch('insights.client.utilities.constants.unregistered_files',
       ['/tmp/insights-client.unregistered',
        '/tmp/redhat-access-insights.unregistered'])
def test_delete_registered_file():
    util.write_registered_file()
    util.delete_registered_file()
    for r in constants.registered_files:
        assert os.path.isfile(r) is False


@patch('insights.client.utilities.constants.registered_files',
       ['/tmp/insights-client.registered',
        '/tmp/redhat-access-insights.registered'])
@patch('insights.client.utilities.constants.unregistered_files',
       ['/tmp/insights-client.unregistered',
        '/tmp/redhat-access-insights.unregistered'])
def test_write_unregistered_file():
    util.write_unregistered_file()
    for r in constants.registered_files:
        assert os.path.isfile(r) is False
    for u in constants.unregistered_files:
        assert os.path.isfile(u) is True


@patch('insights.client.utilities.constants.registered_files',
       ['/tmp/insights-client.registered',
        '/tmp/redhat-access-insights.registered'])
@patch('insights.client.utilities.constants.unregistered_files',
       ['/tmp/insights-client.unregistered',
        '/tmp/redhat-access-insights.unregistered'])
def test_delete_unregistered_file():
    util.write_unregistered_file()
    util.delete_unregistered_file()
    for u in constants.unregistered_files:
        assert os.path.isfile(u) is False


def test_read_pidfile():
    '''
    Test a pidfile that exists
    '''
    if six.PY3:
        open_name = 'builtins.open'
    else:
        open_name = '__builtin__.open'

    with patch(open_name, create=True) as mock_open:
        mock_open.side_effect = [mock.mock_open(read_data='420').return_value]
        assert util.read_pidfile() == '420'


def test_read_pidfile_failure():
    '''
    Test a pidfile that does not exist
    '''
    if six.PY3:
        open_name = 'builtins.open'
    else:
        open_name = '__builtin__.open'

    with patch(open_name, create=True) as mock_open:
        mock_open.side_effect = IOError
        assert util.read_pidfile() is None


@patch('insights.client.utilities.Popen')
@patch('insights.client.utilities.os.path.exists')
def test_systemd_notify_no_socket(exists, Popen):
    '''
    Test this function when NOTIFY_SOCKET is
    undefined, i.e. when we run the client on demand
    and not via systemd job
    '''
    exists.return_value = True
    Popen.return_value.communicate.return_value = ('', '')
    util.systemd_notify('420')
    Popen.assert_not_called()


@patch('insights.client.utilities.Popen')
@patch('insights.client.utilities.os.path.exists')
@patch.dict('insights.client.utilities.os.environ', {'NOTIFY_SOCKET': '/tmp/test.sock'})
def test_systemd_notify(exists, Popen):
    '''
    Test calling systemd-notify with a "valid" PID
    On RHEL 7, exists(/usr/bin/systemd-notify) == True
    '''
    exists.return_value = True
    Popen.return_value.communicate.return_value = ('', '')
    util.systemd_notify('420')
    Popen.assert_called_once()


@patch('insights.client.utilities.Popen')
@patch('insights.client.utilities.os.path.exists')
@patch.dict('insights.client.utilities.os.environ', {'NOTIFY_SOCKET': '/tmp/test.sock'})
def test_systemd_notify_failure_bad_pid(exists, Popen):
    '''
    Test calling systemd-notify with an invalid PID
    On RHEL 7, exists(/usr/bin/systemd-notify) == True
    '''
    exists.return_value = True
    util.systemd_notify(None)
    exists.assert_not_called()
    Popen.assert_not_called()


@patch('insights.client.utilities.Popen')
@patch('insights.client.utilities.os.path.exists')
@patch.dict('insights.client.utilities.os.environ', {'NOTIFY_SOCKET': '/tmp/test.sock'})
def test_systemd_notify_failure_rhel_6(exists, Popen):
    '''
    Test calling systemd-notify on RHEL 6
    On RHEL 6, exists(/usr/bin/systemd-notify) == False
    '''
    exists.return_value = False
    util.systemd_notify('420')
    Popen.assert_not_called()


def test_get_tags():
    content = b"foo: bar"
    fp = tempfile.NamedTemporaryFile(delete=False)
    fp.write(content)
    fp.close()
    got = util.get_tags(fp.name)
    assert got == {"foo": "bar"}


def test_get_tags_empty():
    content = b""
    fp = tempfile.NamedTemporaryFile(delete=False)
    fp.write(content)
    fp.close()
    got = util.get_tags(fp.name)
    assert got is None


def test_get_tags_nonexist():
    got = util.get_tags("/file/does/not/exist")
    assert got is None


def test_write_tags():
    tags = {'foo': 'bar'}
    fp = tempfile.NamedTemporaryFile()
    util.write_tags(tags, tags_file_path=fp.name)
    got = util.get_tags(fp.name)
    assert got == tags
