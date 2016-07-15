import unittest

from falafel.mappers import sysctl
from falafel.tests import context_wrap
from falafel.util import keys_in

SYSCTL_TEST = """
a=1
b = 2
c = include an = sign
""".strip()


class TestSysctl(unittest.TestCase):
    def test_sysctl(self):
        r = sysctl.runtime(context_wrap(SYSCTL_TEST))
        self.assertTrue(keys_in(["a", "b", "c"], r))
        self.assertEqual(r["a"], "1")
        self.assertEqual(r["b"], "2")
        self.assertEqual(r["c"], "include an = sign")
