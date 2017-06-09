import unittest

from insights.util import subproc


class TestSubproc(unittest.TestCase):
    def test_call(self):
        cmd = 'echo -n hello'
        result = subproc.call(cmd)
        expected = 'hello'
        self.assertEqual(expected, result)

    def test_call_timeout(self):
        cmd = 'sleep 3'
        with self.assertRaises(subproc.CalledProcessError):
            subproc.call(cmd, timeout=1)

    def test_call_invalid_args(self):
        cmd = [1, 2, 3]
        with self.assertRaises(subproc.CalledProcessError):
            subproc.call(cmd)
