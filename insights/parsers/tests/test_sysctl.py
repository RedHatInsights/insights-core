from insights.parsers import sysctl
from insights.tests import context_wrap
from insights.util import keys_in

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


def test_sysctl():
    r = sysctl.Sysctl(context_wrap(SYSCTL_TEST))
    assert keys_in(["a", "b", "c"], r.data)
    assert r.data["a"] == "1"
    assert r.data["b"] == "2"
    assert r.data["c"] == "include an = sign"


def test_sysctl_conf():
    r = sysctl.SysctlConf(context_wrap(SYSCTL_CONF_TEST))
    assert keys_in(['kernel.domainname', 'kernel.modprobe'], r.data)
    assert r.data['kernel.domainname'] == 'example.com'
    assert r.data['kernel.modprobe'] == '/sbin/mod probe'
