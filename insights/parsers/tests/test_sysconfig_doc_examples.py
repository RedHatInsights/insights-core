from insights.tests import context_wrap
from insights.parsers import sysconfig
from insights.parsers.sysconfig import ChronydSysconfig, DockerSysconfig
from insights.parsers.sysconfig import HttpdSysconfig, IrqbalanceSysconfig
from insights.parsers.sysconfig import LibvirtGuestsSysconfig, MemcachedSysconfig
from insights.parsers.sysconfig import MongodSysconfig, NtpdSysconfig
from insights.parsers.sysconfig import PrelinkSysconfig, VirtWhoSysconfig
from insights.parsers.sysconfig import Up2DateSysconfig, PuppetserverSysconfig
from insights.parsers.sysconfig import NetconsoleSysconfig, ForemanTasksSysconfig
from insights.parsers.sysconfig import DockerStorageSetupSysconfig, DirsrvSysconfig
from insights.parsers.sysconfig import CorosyncSysconfig
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

UP2DATESYSCONFIG = """
serverURL[comment]=Remote server URL
#serverURL=https://rhnproxy.glb.tech.markit.partners
serverURL=https://rhnproxy.glb.tech.markit.partners/XMLRPC
""".strip()

PUPPETSERVERCONFIG = """
USER="puppet"
GROUP="puppet"
INSTALL_DIR="/opt/puppetlabs/server/apps/puppetserver"
CONFIG="/etc/puppetlabs/puppetserver/conf.d"
START_TIMEOUT=300
""".strip()

NETCONSOLESYSCONFIG = """
LOCALPORT=6666
""".strip()

FOREMANTASKSYSCONFG = """
FOREMAN_USER=foreman
BUNDLER_EXT_HOME=/usr/share/foreman
RAILS_ENV=production
FOREMAN_LOGGING=warn
""".strip()

DOCKERSTORAGESETUPSYSCONFG = """
VG=vgtest
AUTO_EXTEND_POOL=yes
##name = mydomain
POOL_AUTOEXTEND_THRESHOLD=60
POOL_AUTOEXTEND_PERCENT=20
""".strip()

DIRSRVSYSCONFG = """
#STARTPID_TIME=10 ; export STARTPID_TIME
#PID_TIME=600 ; export PID_TIME
KRB5CCNAME=/tmp/krb5cc_995
KRB5_KTNAME=/etc/dirsrv/ds.keytab
""".strip()

COROSYNCSYSCONFIG = """
# COROSYNC_INIT_TIMEOUT specifies number of seconds to wait for corosync
# initialization (default is one minute).
COROSYNC_INIT_TIMEOUT=60
# COROSYNC_OPTIONS specifies options passed to corosync command
# (default is no options).
# See "man corosync" for detailed descriptions of the options.
COROSYNC_OPTIONS=""
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
            'u2d_syscfg': Up2DateSysconfig(context_wrap(UP2DATESYSCONFIG)),
            'netcs_syscfg': NetconsoleSysconfig(context_wrap(NETCONSOLESYSCONFIG)),
            'pps_syscfg': PuppetserverSysconfig(context_wrap(PUPPETSERVERCONFIG)),
            'ft_syscfg': ForemanTasksSysconfig(context_wrap(FOREMANTASKSYSCONFG)),
            'dss_syscfg': DockerStorageSetupSysconfig(context_wrap(DOCKERSTORAGESETUPSYSCONFG)),
            'dirsrv_syscfg': DirsrvSysconfig(context_wrap(DIRSRVSYSCONFG)),
            'cs_syscfg': CorosyncSysconfig(context_wrap(COROSYNCSYSCONFIG)),
          }
    failed, total = doctest.testmod(sysconfig, globs=env)
    assert failed == 0
