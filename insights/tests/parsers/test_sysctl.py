import doctest
from insights.parsers import sysctl
from insights.tests import context_wrap
from insights.util import keys_in

SYSCTL_TEST = """
a=1
b = 2
c = include an = sign
""".strip()

SYSCTL_DOC_TEST = """
kernel.domainname = example.com
kernel.modprobe = /sbin/modprobe
""".strip()

SYSCTL_CONF_TEST = """
# sysctl.conf sample
#
  kernel.domainname = example.com
# kernel.domainname.invalid = notvalid.com

; this one has a space which will be written to the sysctl!
  kernel.modprobe = /sbin/mod probe
""".strip()

SYSCTL_CONF_INITRAMFS_TEST = """
initramfs:/etc/sysctl.conf
========================================================================
# sysctl settings are defined through files in
# /usr/lib/sysctl.d/, /run/sysctl.d/, and /etc/sysctl.d/.
#
# Vendors settings live in /usr/lib/sysctl.d/.
# To override a whole file, create a new file with the same in
# /etc/sysctl.d/ and put new settings there. To override
# only specific settings, add a file with a lexically later
# name in /etc/sysctl.d/ and put new settings there.
#
# For more information, see sysctl.conf(5) and sysctl.d(5).
fs.inotify.max_user_watches=524288
key2=value2
key2_alt=value2_alt
#  key3=value3
; key4=value4
========================================================================

initramfs:/etc/sysctl.d/*.conf
========================================================================
========================================================================
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
    assert 'kernel.domainname.invalid' not in r.data


def test_sysctl_d_conf():
    r = sysctl.SysctlDConfEtc(context_wrap(SYSCTL_CONF_TEST))
    assert keys_in(['kernel.domainname', 'kernel.modprobe'], r)
    assert r['kernel.domainname'] == 'example.com'
    assert r['kernel.modprobe'] == '/sbin/mod probe'
    assert 'kernel.domainname.invalid' not in r

    r = sysctl.SysctlDConfUsr(context_wrap(SYSCTL_CONF_TEST))
    assert keys_in(['kernel.domainname', 'kernel.modprobe'], r)
    assert r['kernel.domainname'] == 'example.com'
    assert r['kernel.modprobe'] == '/sbin/mod probe'
    assert 'kernel.domainname.invalid' not in r


def test_sysctl_conf_initramfs():
    r = sysctl.SysctlConfInitramfs(context_wrap(SYSCTL_CONF_INITRAMFS_TEST))
    assert r is not None
    assert r.get('max_user_watches') == [{'raw_message': 'fs.inotify.max_user_watches=524288'}]
    assert r.get('key2') == [{'raw_message': 'key2=value2'}, {'raw_message': 'key2_alt=value2_alt'}]
    assert r.get('key3') == []
    assert r.get('key4') == []


def test_docs():
    env = {
        'sysctl': sysctl.Sysctl(context_wrap(SYSCTL_DOC_TEST)),
        'sysctl_conf': sysctl.SysctlConf(context_wrap(SYSCTL_CONF_TEST)),
        'sysctl_d_conf_etc': sysctl.SysctlDConfEtc(context_wrap(SYSCTL_CONF_TEST)),
        'sysctl_d_conf_usr': sysctl.SysctlDConfUsr(context_wrap(SYSCTL_CONF_TEST)),
        'sysctl_initramfs': sysctl.SysctlConfInitramfs(context_wrap(SYSCTL_CONF_INITRAMFS_TEST))
    }
    failed, total = doctest.testmod(sysctl, globs=env)
    assert failed == 0
