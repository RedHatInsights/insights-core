import os
import tempfile
import uuid
import insights.client.utilities as util
from insights.client.constants import InsightsConstants
import re

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
    orig_dir = InsightsConstants.insights_ansible_facts_dir
    InsightsConstants.insights_ansible_facts_dir = tempfile.mkdtemp()
    InsightsConstants.insights_ansible_machine_id_file = os.path.join(
        InsightsConstants.insights_ansible_facts_dir, "ansible_machine_id.fact")
    machine_id_regex = re.match('\w{8}-\w{4}-\w{4}-\w{4}-\w{12}',
                                util.generate_machine_id(destination_file='/tmp/testmachineid'))
    assert machine_id_regex.group(0) is not None
    with open('/tmp/testmachineid', 'r') as _file:
        machine_id = _file.read()
    assert util.generate_machine_id(destination_file='/tmp/testmachineid') == machine_id
    os.remove('/tmp/testmachineid')
    os.remove(InsightsConstants.insights_ansible_machine_id_file)
    os.rmdir(InsightsConstants.insights_ansible_facts_dir)
    InsightsConstants.insights_ansible_facts_dir = orig_dir
    InsightsConstants.insights_ansible_machine_id_file = os.path.join(
        InsightsConstants.insights_ansible_facts_dir, "ansible_machine_id.fact")


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


def test_validate_remove_file():
    tf = '/tmp/remove.cfg'
    with open(tf, 'wb') as f:
        f.write(remove_file_content)
    assert util.validate_remove_file(remove_file='/tmp/boop') is False
    os.chmod(tf, 0o644)
    assert util.validate_remove_file(remove_file=tf) is False
    os.chmod(tf, 0o600)
    assert util.validate_remove_file(remove_file=tf) is not False
