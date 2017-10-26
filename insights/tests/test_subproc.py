import unittest
import sys

from insights.util import subproc


class TestSubproc(unittest.TestCase):
    def test_call(self):
        cmd = 'echo -n hello'
        result = subproc.call(cmd)
        expected = 'hello'
        self.assertEqual(expected, result)

    def test_call_timeout(self):
        cmd = 'sleep 3'
        if sys.platform != "darwin":
            with self.assertRaises(subproc.CalledProcessError):
                subproc.call(cmd, timeout=1)
