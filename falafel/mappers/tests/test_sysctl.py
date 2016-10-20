import unittest

from falafel.mappers import sysctl
from falafel.tests import context_wrap
from falafel.util import keys_in

SYSCTL_TEST = """
a=1
b = 2
c = include an = sign
""".strip()
SYSCTL_CONF_TEST = """
# sysctl.conf sample
#
  kernel.domainname = example.com

; this one has a space which will be written to the sysctl!
  kernel.modprobe = /sbin/mod probe
""".strip()


class TestSysctl(unittest.TestCase):
    def test_sysctl(self):
        r = sysctl.Sysctl(context_wrap(SYSCTL_TEST))
        self.assertTrue(keys_in(["a", "b", "c"], r.data))
        self.assertEqual(r.data["a"], "1")
        self.assertEqual(r.data["b"], "2")
        self.assertEqual(r.data["c"], "include an = sign")

    def test_sysctl_conf(self):
        r = sysctl.SysctlConf(context_wrap(SYSCTL_CONF_TEST))
        self.assertTrue(keys_in(['kernel.domainname', 'kernel.modprobe'], r.data))
        self.assertEqual(r.data['kernel.domainname'], 'example.com')
        self.assertEqual(r.data['kernel.modprobe'], '/sbin/mod probe')
