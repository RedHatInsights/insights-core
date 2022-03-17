import doctest

from insights.combiners import sysctl_conf
from insights.parsers import sysctl
from insights.tests import context_wrap


SYSCTL_CONF_TEST1 = """
# sysctl.conf sample
#
  kernel.domainname = example.com
# kernel.domainname.invalid = notvalid.com

; this one has a space which will be written to the sysctl!
  kernel.modprobe = /sbin/mod probe
""".strip()

SYSCTL_CONF_TEST2 = """
kernel.sysrq = 1
kernel.panic_on_oops = 1
kernel.panic_on_unrecovered_nmi = 1
kernel.softlockup_panic = 1
kernel.unknown_nmi_panic = 1
kernel.nmi_watchdog = 1
""".strip()

SYSCTL_CONF_TEST3 = """
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5
vm.swappiness = 10
"""

SYSCTL_CONF_TEST4 = """
vm.dirty_ratio = 30
vm.dirty_background_ratio = 50
vm.swappiness = 60
kernel.sysrq = 16
kernel.domainname = test.example.com
"""

SYSCTL1_CONF_FILENAME = "/etc/sysctl.d/10-test.conf"
SYSCTL2_CONF_FILENAME = "/etc/sysctl.d/20-test.conf"
SYSCTL3_CONF_FILENAME = "/etc/sysctl.d/30-test.conf"
SYSCTL4_CONF_FILENAME = "/etc/sysctl.d/99-test.conf"
SYSCTL5_CONF_FILENAME = "/etc/sysctl.conf"
SYSCTL6_CONF_FILENAME = "/usr/lib/sysctl.d/99-test.conf"


def test_all_sysctl_conf():
    conf_1 = sysctl.SysctlConf(context_wrap(SYSCTL_CONF_TEST1, path=SYSCTL5_CONF_FILENAME))
    conf_2 = sysctl.SysctlDConfEtc(context_wrap(SYSCTL_CONF_TEST2, path=SYSCTL2_CONF_FILENAME))
    conf_3 = sysctl.SysctlDConfEtc(context_wrap(SYSCTL_CONF_TEST3, path=SYSCTL3_CONF_FILENAME))
    r = sysctl_conf.SysctlConfs(conf_1, None, [conf_2, conf_3])

    assert r['kernel.domainname'] == 'example.com'
    assert r['kernel.modprobe'] == '/sbin/mod probe'
    assert 'kernel.domainname.invalid' not in r
    assert r.search("dirty") == {"vm.dirty_ratio": "15", "vm.dirty_background_ratio": "5"}
    assert r.search("test") == {}


def test_all_sysctl_conf_different_order():
    conf_1 = sysctl.SysctlConf(context_wrap(SYSCTL_CONF_TEST1, path=SYSCTL5_CONF_FILENAME))
    conf_2 = sysctl.SysctlDConfUsr(context_wrap(SYSCTL_CONF_TEST2, path=SYSCTL6_CONF_FILENAME))
    conf_3 = sysctl.SysctlDConfEtc(context_wrap(SYSCTL_CONF_TEST3, path=SYSCTL2_CONF_FILENAME))
    conf_4 = sysctl.SysctlDConfEtc(context_wrap(SYSCTL_CONF_TEST4, path=SYSCTL4_CONF_FILENAME))
    r = sysctl_conf.SysctlConfs(conf_1, [conf_2], [conf_3, conf_4])

    assert r['kernel.domainname'] == 'example.com'
    assert r['kernel.sysrq'] == '16'
    assert r.search("dirty") == {"vm.dirty_ratio": "30", "vm.dirty_background_ratio": "50"}


def test_docs():
    conf_1 = sysctl.SysctlDConfEtc(context_wrap(SYSCTL_CONF_TEST1, path=SYSCTL1_CONF_FILENAME))
    conf_2 = sysctl.SysctlDConfEtc(context_wrap(SYSCTL_CONF_TEST2, path=SYSCTL2_CONF_FILENAME))
    conf_3 = sysctl.SysctlDConfEtc(context_wrap(SYSCTL_CONF_TEST3, path=SYSCTL3_CONF_FILENAME))

    env = {
        'sysctl_conf': sysctl_conf.SysctlConfs(None, None, [conf_1, conf_2, conf_3]),
    }
    failed, total = doctest.testmod(sysctl_conf, globs=env)
    assert failed == 0
