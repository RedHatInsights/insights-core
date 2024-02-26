import os
import sys
from tarfile import open as tar_open
import tarfile
import tempfile
import uuid
import insights.client.utilities as util
from insights.client.constants import InsightsConstants as constants
import re
import mock
import six
import pytest
import errno
from mock.mock import patch
from json import loads as json_load


machine_id = str(uuid.uuid4())
remove_file_content = """
[remove]
commands=foo
files=bar
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


def test_write_to_disk_with_broken_path():
    """
    Ensure that the `write_to_disk` method only
    executes without raising an exception if
    the encountered exception has error code 2
    (No such file or directory), otherwise
    raise the exception.
    """
    content = 'boop'
    filename = '/tmp/testing'
    util.write_to_disk(filename, content=content)
    assert os.path.exists(filename)

    with patch("os.remove") as mock_remove:
        mock_remove.side_effect = OSError()
        mock_remove.side_effect.errno = errno.ENOENT
        assert util.write_to_disk(filename, delete=True) is None

        mock_remove.side_effect.errno = errno.ENOTTY
        with pytest.raises(OSError):
            util.write_to_disk(filename, delete=True)
    os.remove(filename)


def test_get_machine_id():
    """
    Test get machine_id with generate_machine_id method, if the machine-id file exists
    """
    machine_id_regex = re.match('\w{8}-\w{4}-\w{4}-\w{4}-\w{12}',
                                util.generate_machine_id(destination_file='/tmp/testmachineid'))
    assert machine_id_regex.group(0) is not None
    with open('/tmp/testmachineid', 'r') as _file:
        machine_id = _file.read()
    assert util.generate_machine_id(destination_file='/tmp/testmachineid') == machine_id
    os.remove('/tmp/testmachineid')


def test_get_machineid_with_non_hyphen_id():
    content = '86f6f5fad8284730b708a2e44ba5c14a'
    filename = '/tmp/testmachineid'
    util.write_to_disk(filename, content=content)

    returned_uuid = str(uuid.UUID(content, version=4))

    assert util.generate_machine_id(destination_file=filename) == returned_uuid
    os.remove(filename)


def test_bad_machine_id():
    with mock.patch.object(util.sys, "exit") as mock_exit:
        with open('/tmp/testmachineid', 'w') as _file:
            _file.write("this_is_bad")
        util.generate_machine_id(destination_file='/tmp/testmachineid')
    assert mock_exit.call_args[0][0] == constants.sig_kill_bad
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


@patch('insights.client.utilities.wrapper_constants')
@patch.dict('insights.client.utilities.package_info', {'VERSION': '1', 'RELEASE': '1'})
def test_get_version_info_OK(wrapper_constants):
    '''
    insights_client constants are imported OK and version
    is reported. Return version as defined
    '''
    wrapper_constants.version = 1
    version_info = util.get_version_info()
    assert version_info == {'core_version': '1-1', 'client_version': 1}


@patch('insights.client.utilities.wrapper_constants', new=None)
@patch.dict('insights.client.utilities.package_info', {'VERSION': '1', 'RELEASE': '1'})
def test_get_version_info_no_module():
    '''
    insights_client constants cannot be imported,
    constants object is None. Return None version.
    '''
    version_info = util.get_version_info()
    assert version_info == {'core_version': '1-1', 'client_version': None}


@patch('insights.client.utilities.wrapper_constants')
@patch.dict('insights.client.utilities.package_info', {'VERSION': '1', 'RELEASE': '1'})
def test_get_version_info_no_version(wrapper_constants):
    '''
    insights_client constants are imported OK but
    constants object has no attribute "version."
    Return None version
    '''
    del wrapper_constants.version
    version_info = util.get_version_info()
    assert version_info == {'core_version': '1-1', 'client_version': None}


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


@patch('insights.client.utilities.threading.Thread')
@patch('insights.client.utilities.os.path.exists')
def test_systemd_notify_init_thread_no_socket(exists, thread):
    '''
    Test this function when NOTIFY_SOCKET is
    undefined, i.e. when we run the client on demand
    and not via systemd job
    '''
    exists.return_value = True
    util.systemd_notify_init_thread()
    thread.assert_not_called()


@patch('insights.client.utilities.Popen')
def test_systemd_notify(Popen):
    '''
    Test calling systemd-notify with a "valid" PID
    On RHEL 7, exists(/usr/bin/systemd-notify) == True
    '''
    Popen.return_value.communicate.return_value = ('', '')
    util._systemd_notify('420')
    Popen.assert_called_once()


@patch('insights.client.utilities.read_pidfile', mock.Mock(return_value=None))
@patch('insights.client.utilities.threading.Thread')
@patch('insights.client.utilities.os.path.exists')
@patch.dict('insights.client.utilities.os.environ', {'NOTIFY_SOCKET': '/tmp/test.sock'})
def test_systemd_notify_init_thread_failure_bad_pid(exists, thread):
    '''
    Test initializing systemd-notify loop with an invalid PID
    On RHEL 7, exists(/usr/bin/systemd-notify) == True
    '''
    exists.return_value = True
    util.systemd_notify_init_thread()
    exists.assert_not_called()
    thread.assert_not_called()


@patch('insights.client.utilities.threading.Thread')
@patch('insights.client.utilities.os.path.exists')
@patch.dict('insights.client.utilities.os.environ', {'NOTIFY_SOCKET': '/tmp/test.sock'})
def test_systemd_notify_init_thread_failure_rhel_6(exists, thread):
    '''
    Test calling systemd-notify on RHEL 6
    On RHEL 6, exists(/usr/bin/systemd-notify) == False
    '''
    exists.return_value = False
    util.systemd_notify_init_thread()
    thread.assert_not_called()


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
    assert got == {}


def test_get_tags_nonexist():
    got = util.get_tags("/file/does/not/exist")
    assert got is None


@pytest.mark.skipif(sys.version_info < (2, 7), reason='Playbook verifier uses oyaml library which is incompatable with this test')
def test_write_tags():
    tags = {'foo': 'bar'}
    fp = tempfile.NamedTemporaryFile()
    util.write_tags(tags, tags_file_path=fp.name)
    got = util.get_tags(fp.name)
    assert got == tags


@patch('insights.client.utilities.os.rename')
@patch('insights.client.utilities.os.path.exists')
def test_migrate_tags(path_exists, os_rename):
    '''
    Test the migrate_tags function for the following cases:
        1) tags.yaml does not exist, tags.conf does not exist
            - do nothing
        2) tags.yaml exists, tags.conf does not exist
            - do nothing
        3) tags.yaml does not exist, tags.conf exists
            - rename tags.conf to tags.yaml
        4) tags.yaml exists, tags.conf exists
            - do nothing
    '''
    # existence of tags.yaml is checked FIRST, tags.conf is checked SECOND
    #   mock side effects are according to this order

    # case 1
    path_exists.side_effect = [False, False]
    util.migrate_tags()
    os_rename.assert_not_called()
    os_rename.reset_mock()
    # case 2
    path_exists.side_effect = [True, False]
    util.migrate_tags()
    os_rename.assert_not_called()
    os_rename.reset_mock()
    # case 3
    path_exists.side_effect = [False, True]
    util.migrate_tags()
    os_rename.assert_called_once()
    os_rename.reset_mock()
    # case 4
    path_exists.side_effect = [True, True]
    util.migrate_tags()
    os_rename.assert_not_called()
    os_rename.reset_mock()


def mock_open(name, mode, files=[["meta_data/insights.spec-small", 1], ["meta_data/insights.spec-big", 1], ["data/insights/small", 1], ["data/insights/big", 100]]):
    base_path = "./insights-client"
    with tempfile.TemporaryFile(suffix='.tar.gz') as f:
        tarball = tar_open(fileobj=f, mode='w:gz')
        for file in files:
            member = tarfile.TarInfo(name=os.path.join(base_path, file[0]))
            member.size = file[1]
            tarball.addfile(member, None)
        return tarball


def mock_extract_file(self, filename):
    if "small" in filename:
        f = "small"
    else:
        f = "big"
    return f


def mock_json_load(filename):
    if "small" in filename:
        content = json_load('{"name": "insights.spec-small", "results": {"type": "insights.core.spec_factory.CommandOutputProvider", "object": { "relative_path": "insights/small"}}}')
    else:
        content = json_load('{"name": "insights.spec-big", "results": {"type": "insights.core.spec_factory.CommandOutputProvider", "object": { "relative_path": "insights/big"}}}')
    return content


# TODO: try to pass files as mock_open parameter
@patch('insights.client.utilities.tarfile.open', mock_open)
@patch('insights.client.utilities.json.load', mock_json_load)
@patch('insights.client.utilities.tarfile.TarFile.extractfile', mock_extract_file)
def test_largest_spec_in_archive():
    largest_file = util.largest_spec_in_archive("/tmp/insights-client.tar.gz")
    assert largest_file[0] == "insights/big"
    assert largest_file[1] == 100
    assert largest_file[2] == "insights.spec-big"
