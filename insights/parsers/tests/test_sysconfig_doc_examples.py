from insights.tests import context_wrap
from insights.parsers import sysconfig
from insights.parsers.sysconfig import ChronydSysconfig, DockerSysconfig
from insights.parsers.sysconfig import HttpdSysconfig, IrqbalanceSysconfig
from insights.parsers.sysconfig import LibvirtGuestsSysconfig, MemcachedSysconfig
from insights.parsers.sysconfig import MongodSysconfig, NtpdSysconfig
from insights.parsers.sysconfig import PrelinkSysconfig, VirtWhoSysconfig
import doctest


CHRONYDSYSCONFIG = """
OPTIONS="-d"
#HIDE="me"
""".strip()

NTPDSYSCONFIG = """
OPTIONS="-x -g"
#HIDE="me"
""".strip()

DOCKERSYSCONFIG = """
OPTIONS="--selinux-enabled"
DOCKER_CERT_PATH="/etc/docker"
""".strip()

HTTPDSYSCONFIG = """
HTTPD=/usr/sbin/httpd.worker
OPTIONS=
""".strip()

IRQBALANCESYSCONFIG = """
#IRQBALANCE_ONESHOT=yes
IRQBALANCE_BANNED_CPUS=f8
IRQBALANCE_ARGS="-d"
""".strip()

VIRTWHOSYSCONFIG = """
# Register ESX machines using vCenter
# VIRTWHO_ESX=0
# Register guests using RHEV-M
VIRTWHO_RHEVM=1
# Options for RHEV-M mode
VIRTWHO_RHEVM_OWNER=
TEST_OPT="A TEST"
""".strip()

MONGODSYSCONFIG = """
OPTIONS="--quiet -f /etc/mongod.conf"
""".strip()

MEMCACHEDSYSCONFIG = """
PORT="11211"
USER="memcached"
# max connection 2048
MAXCONN="2048"
CACHESIZE="4096"
OPTIONS="-U 0 -l 127.0.0.1"
""".strip()

LIBVIRTGUESTSSYSCONFIG = """
ON_BOOT=ignore
""".strip()

PRELINKSYSCONFIG = """
PRELINKING=no
PRELINK_OPTS=-mR
""".strip()


def test_sysconfig_doc():
    env = {
            'chronyd_syscfg': ChronydSysconfig(context_wrap(CHRONYDSYSCONFIG)),
            'ntpd_syscfg': NtpdSysconfig(context_wrap(NTPDSYSCONFIG)),
            'docker_syscfg': DockerSysconfig(context_wrap(DOCKERSYSCONFIG)),
            'httpd_syscfg': HttpdSysconfig(context_wrap(HTTPDSYSCONFIG)),
            'irqb_syscfg': IrqbalanceSysconfig(context_wrap(IRQBALANCESYSCONFIG)),
            'vwho_syscfg': VirtWhoSysconfig(context_wrap(VIRTWHOSYSCONFIG)),
            'mongod_syscfg': MongodSysconfig(context_wrap(MONGODSYSCONFIG)),
            'memcached_syscfg': MemcachedSysconfig(context_wrap(MEMCACHEDSYSCONFIG)),
            'libvirt_guests_syscfg': LibvirtGuestsSysconfig(context_wrap(LIBVIRTGUESTSSYSCONFIG)),
            'prelink_syscfg': PrelinkSysconfig(context_wrap(PRELINKSYSCONFIG)),
          }
    failed, total = doctest.testmod(sysconfig, globs=env)
    assert failed == 0
