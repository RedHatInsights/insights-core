import os
from tarfile import open as tar_open
import tarfile
import tempfile
import uuid
import insights.client.utilities as util
import insights.client.cert_auth
from insights.client.constants import InsightsConstants as constants
import re
try:
    from unittest import mock
    from unittest.mock import patch
except ImportError:
    import mock
    from mock.mock import patch
import six
import pytest
import errno
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
    time_regex = re.match(r'\d{4}-\d{2}-\d{2}\D\d{2}:\d{2}:\d{2}\.\d+',
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


@patch("insights.client.utilities._get_rhsm_identity", lambda: None)
def test_generate_machine_id_with_no_subman():
    machine_id_regex = re.match(
        r'\w{8}-\w{4}-\w{4}-\w{4}-\w{12}',
        util.generate_machine_id(destination_file='/tmp/testmachineid')
    )
    assert machine_id_regex.group(0) is not None
    with open('/tmp/testmachineid', 'r') as _file:
        machine_id = _file.read()
    assert util.generate_machine_id(destination_file='/tmp/testmachineid') == machine_id
    os.remove('/tmp/testmachineid')


@pytest.mark.skipif(insights.client.cert_auth.RHSM_CONFIG is None, reason="RHSM config is not available")
@patch("insights.client.utilities.os.path.isfile", lambda _: True)
@patch("insights.client.cert_auth.rhsmCertificate")
@patch("insights.client.utilities.cert_auth.RHSM_CONFIG")
def test__get_rhsm_identity(mock_config, mock_rhsm_cert):
    mock_config.return_value = "non-None-value"

    cert = mock.MagicMock()
    cert.CERT = "cert.pem"
    cert.getConsumerId.return_value = machine_id
    mock_rhsm_cert.read.return_value = cert

    assert machine_id == util._get_rhsm_identity()


@patch("insights.client.utilities._get_rhsm_identity", lambda: machine_id)
def test_generate_machine_id_with_subman():
    """Use sub-man's identity certificate for generating new machine-id."""
    machine_id_file = "/tmp/test-machine-id"
    read_uuid = util.generate_machine_id(destination_file=machine_id_file)
    os.remove(machine_id_file)

    assert machine_id == read_uuid


def test_generate_machine_id_with_non_hyphen_id():
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


@pytest.mark.parametrize(
    "family,version,raw_os_release",
    [
        ("Red Hat Enterprise Linux", "9.5", ['NAME="Red Hat Enterprise Linux"\n', 'VERSION_ID="9.5"\n']),
        ("Red Hat Enterprise Linux", "8.9", ['NAME="Red Hat Enterprise Linux"\n', 'VERSION_ID="8.9"\n']),
        ("Red Hat Enterprise Linux", "7.9", ['NAME="Red Hat Enterprise Linux"\n', 'VERSION_ID="7.9"\n']),
        ("CentOS Stream", "10", ['NAME="CentOS Stream"\n', 'VERSION_ID="10"\n']),
        ("CentOS Stream", "8", ['NAME="CentOS Stream"\n', 'VERSION_ID="8"\n']),
        ("Fedora Linux", "41", ['NAME="Fedora Linux"\n', 'VERSION_ID=41\n']),
    ]
)
def test_os_release_info__os_release(family, version, raw_os_release):
    # type: (str, str, str) -> None
    with patch("insights.client.utilities._read_file", return_value=raw_os_release):
        actual_family, actual_version = util.os_release_info()
        assert (actual_family, actual_version) == (family, version)


@pytest.mark.parametrize(
    "family,version,raw_redhat_release",
    [
        ("Red Hat Enterprise Linux", "9.5", ["Red Hat Enterprise Linux release 9.5 (Plow)"]),
        ("Red Hat Enterprise Linux", "8.9", ["Red Hat Enterprise Linux release 8.9 (Ootpa)"]),
        ("Red Hat Enterprise Linux Server", "7.9", ["Red Hat Enterprise Linux Server release 7.9 (Maipo)"]),
        ("Red Hat Enterprise Linux Server", "6.10", ["Red Hat Enterprise Linux Server release 6.10 (Santiago)"]),
        ("Fedora", "41", ["Fedora release 41 (Forty One)"]),
        ("CentOS Stream", "10", ["CentOS Stream release 10"]),
        ("CentOS Stream", "9", ["CentOS Stream release 9"]),
        ("CentOS Stream", "8", ["CentOS Stream release 8"]),
        ("CentOS Linux", "8.4.2105", ["CentOS Linux release 8.4.2105"]),
        ("CentOS Linux", "7.9.2009", ["CentOS Linux release 7.9.2009 (Core)"]),
    ]
)
def test_os_release_info__redhat_release(family, version, raw_redhat_release):
    # type: (str, str, str) -> None
    with patch("insights.client.utilities._read_file", side_effect=[IOError, raw_redhat_release]):
        actual_family, actual_version = util.os_release_info()
        assert (actual_family, actual_version) == (family, version)


@pytest.mark.parametrize(
    "expected,distribution,version",
    [
        (9, "Red Hat Enterprise Linux", "9.5"),
        (8, "Red Hat Enterprise Linux", "8.9"),
        (7, "Red Hat Enterprise Linux Server", "7.9"),
        (6, "Red Hat Enterprise Linux Server", "6.10"),
        (10, "Fedora", "41"),
        (10, "CentOS Stream", "10"),
        (9, "CentOS Stream", "9"),
        (8, "CentOS Stream", "8"),
        (8, "CentOS Linux", "8.4.2105"),
        (7, "CentOS Linux", "7.9.2009"),
    ]
)
def test_get_rhel_version(expected, distribution, version):
    # type: (str, str, str) -> None
    with patch("insights.client.utilities.os_release_info", return_value=(distribution, version)):
        actual = insights.client.utilities.get_rhel_version()
        assert actual == expected


@pytest.mark.parametrize(
    "error,distribution,version",
    [
        # Defaults of utilities.os_release_info()
        ("Could not determine distribution family.", "Unknown", ""),
        # Unlikely irl; might happen with corrupted os-release (?)
        ("Could not determine version of 'Fedora'.", "Fedora", ""),
        # When running on non-RHEL distribution
        ("Unknown distribution 'Alpine Linux'.", "Alpine Linux", "3.21.2"),
    ]
)
def test_get_rhel_version_error(error, distribution, version):
    # type: (str, str, str) -> None
    with patch("insights.client.utilities.os_release_info", return_value=(distribution, version)):
        with pytest.raises(ValueError) as exc_info:
            insights.client.utilities.get_rhel_version()
        assert str(exc_info.value) == error
