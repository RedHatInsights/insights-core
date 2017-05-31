import unittest
from insights.tools import generate_api_config


class TestAPIGen(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from insights.parsers import *  # noqa
        pass

    def setUp(self):
        self.latest = generate_api_config.APIConfigGenerator(plugin_package="insights.tests.test_plugins").serialize_data_spec()

    def tearDown(self):
        self.latest = None

    def test_top_level(self):
        # these sections must exist and not be empty
        for each in ['version', 'files', 'commands', 'specs', 'pre_commands', 'meta_specs']:
            self.assertIn(each, self.latest)
            self.assertGreater(len(self.latest[each]), 0)

    def test_meta_specs(self):
        # these sections must exist in the meta_specs, have a 'archive_file_name' field,
        #   and it must not be empty
        for each in ['analysis_target', 'branch_info', 'machine-id', 'uploader_log']:
            self.assertIn(each, self.latest['meta_specs'])
            self.assertIn('archive_file_name', self.latest['meta_specs'][each])
            self.assertGreater(len(self.latest['meta_specs'][each]['archive_file_name']), 0)

    def test_specs(self):
        # check that each spec only has target sections for known targets
        for eachspec in self.latest['specs']:
            for eachtarget in self.latest['specs'][eachspec]:
                self.assertIn(eachtarget, ['host', 'docker_container', 'docker_image'])
