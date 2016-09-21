import unittest
import os
import subprocess

HERE = os.path.abspath(os.path.dirname(__file__))


class TestInsightsCliMain(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.path = os.path.join(HERE, "insights_heartbeat.tar.gz")
        self.insights_cli = 'insights-cli'

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
