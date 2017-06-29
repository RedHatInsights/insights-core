import unittest
import os
import tempfile
import uuid
import insights.client.utilities as util

machine_id = str(uuid.uuid4())


class TestUtilites(unittest.TestCase):

    def test_display_name(self):
        self.assertEquals(util.determine_hostname(display_name='foo'), 'foo')

    def test_determine_hostname(self):
        import socket
        hostname = socket.gethostname()
        fqdn = socket.getfqdn()
        self.assertEquals(hostname or fqdn, util.determine_hostname())
        self.assertNotEquals('foo', util.determine_hostname())

    def test_write_machine_id(self):
        tf = tempfile.NamedTemporaryFile()
        util._write_machine_id(machine_id, tf.name)
        with open(tf.name, 'r') as f:
            written_file = f.read()

        self.assertEquals(machine_id, written_file)

    def test_get_time(self):
        import re
        time_regex = re.match('\d{4}-\d{2}-\d{2}\D\d{2}:\d{2}:\d{2}\.\d+',
                              util.get_time())
        assert time_regex.group(0) is not None

    def test_generate_machine_id(self):
        import re
        machine_id_regex = re.match('\w{8}-\w{4}-\w{4}-\w{4}-\w{12}',
                                    util.generate_machine_id(destination_file='/tmp/testmachineid'))
        assert machine_id_regex.group(0) is not None
        with open('/tmp/testmachineid', 'r') as _file:
            machine_id = _file.read()
        self.assertEquals(machine_id, util.generate_machine_id(destination_file='/tmp/testmachineid'))
        os.remove('/tmp/testmachineid')
