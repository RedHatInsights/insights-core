import os
import tempfile
import uuid
import insights.client.utilities as util
from insights.client.constants import InsightsConstants as constants
import re
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
@patch('insights.client.InsightsClient')
def test_get_version_info(insights_client, run_command_get_output):
    insights_client.return_value.version.return_value = 1
    run_command_get_output.return_value = {'output': 1}
    version_info = util.get_version_info()
    assert version_info == {'core_version': 1, 'client_version': 1}


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
