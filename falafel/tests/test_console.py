import unittest
import os
import subprocess
import ConfigParser
import re
from falafel.console.config import InsightsCliConfig

HERE = os.path.abspath(os.path.dirname(__file__))


class TestInsightsCliMain(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.path = os.path.join(HERE, "insights_heartbeat.tar.gz")
        self.insights_cli = "insights-cli"
        self.section = InsightsCliConfig.INSIGHTS_CLI
        self.config_file_path = InsightsCliConfig.CONFIG_FILE_PATH

    @classmethod
    def tearDownClass(self):
        pass

    def test_main(self):
        cmd = [self.insights_cli, '--plugin-modules', 'falafel.plugins', '-v', '--', self.path]

        try:
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError:
            self.fail("Failed to run insights-cli succesfully, test_main() "
                      "raised subprocess.CalledProcessError unexpectedly!.")

    def test_plugin_module_option_fail(self):
        cmd = [self.insights_cli, '--plugin-modules', '-v', '--', self.path]
        self.assertRaises(subprocess.CalledProcessError, subprocess.check_call, cmd)

    def test_show_plugin_list(self):
        cmd = [self.insights_cli, '--show-plugin-list', '--plugin-modules', 'falafel.plugins', '--', self.path]
        try:
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError:
            self.fail("Failed to run insights-cli succesfully, test_show_plugin_list() "
                      "raised subprocess.CalledProcessError unexpectedly!.")

    def test_extract_dir(self):
        cmd = [self.insights_cli, '--show-plugin-list', '--plugin-modules', 'falafel.plugins', '--extract-dir', '/tmp', '-v', '--', self.path]

        insights_cli = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = insights_cli.communicate()
        regex = re.compile(r"Extracting files in \'/tmp")
        test = re.search(regex, output)
        self.assertNotEqual(test, None, msg="Failed to test '--extract-dir option.")

    def test_config_options(self):
        # Take config file backup.
        self.config_org = None
        if os.path.isfile(self.config_file_path):
            with open(self.config_file_path, 'r') as config_file:
                self.config_org = config_file.read()

        # setup config file
        config_parser = ConfigParser.RawConfigParser()
        config_parser.add_section(self.section)

        key_types_map = {
                    'mem_only': 'boolean',
                    'spec_map': 'boolean',
                    'list_plugins': 'boolean',
                    'list_missing': 'boolean',
                    'max_width': 'integer',
                    'verbose': 'integer'
        }
        for key, types in key_types_map.iteritems():
            config_parser.set(self.section, key, 'junk')
            with open(self.config_file_path, 'wb') as configfile:
                config_parser.write(configfile)
            configfile.close()

            cmd = [self.insights_cli, '--plugin-modules', 'falafel.plugins', '-v', '--', self.path]

            try:
                insights_cli = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output, err = insights_cli.communicate()
                regex = re.compile(r"Value of '{0}' in section '{1}' should be of type {2}".format(key, self.section, types))
                test = re.search(regex, err)

                self.assertNotEqual(test, None, msg="Failed to test configure option: {0}.".format(key))
                config_parser.remove_option(self.section, key)

            finally:
                # Restore original config file.
                if self.config_org:
                    with open(self.config_file_path, 'wb') as config_file:
                        config_file.write(self.config_org)
                    config_file.close()

    def test_config_extract_dir_option(self):
        # Take config file backup.
        self.config_org = None
        if os.path.isfile(self.config_file_path):
            with open(self.config_file_path, 'r') as config_file:
                self.config_org = config_file.read()

        # setup config file
        config_parser = ConfigParser.RawConfigParser()
        config_parser.add_section(self.section)
        config_parser.set(self.section, 'plugin_modules', 'falafel.plugins')
        config_parser.set(self.section, 'extract_dir', '/tmp')

        with open(self.config_file_path, 'wb') as configfile:
            config_parser.write(configfile)
        configfile.close()

        cmd = [self.insights_cli, '-v', '--', self.path]
        try:
            insights_cli = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, err = insights_cli.communicate()
            regex = re.compile(r"Extracting files in \'/tmp")
            test = re.search(regex, output)
            self.assertNotEqual(test, None, msg="Failed to test '--extract-dir' option.")

        finally:
            # Restore original config file.
            if self.config_org:
                with open(self.config_file_path, 'wb') as config_file:
                    config_file.write(self.config_org)
                config_file.close()
