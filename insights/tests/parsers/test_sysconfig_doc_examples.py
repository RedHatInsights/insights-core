from insights.tests import context_wrap
from insights.parsers import sysconfig
from insights.parsers.sysconfig import ChronydSysconfig, DockerSysconfig, DockerSysconfigStorage
from insights.parsers.sysconfig import HttpdSysconfig, IrqbalanceSysconfig
from insights.parsers.sysconfig import LibvirtGuestsSysconfig, MemcachedSysconfig
from insights.parsers.sysconfig import MongodSysconfig, NtpdSysconfig
from insights.parsers.sysconfig import PrelinkSysconfig, VirtWhoSysconfig
from insights.parsers.sysconfig import SshdSysconfig
from insights.parsers.sysconfig import Up2DateSysconfig, PuppetserverSysconfig
from insights.parsers.sysconfig import NetconsoleSysconfig, ForemanTasksSysconfig
from insights.parsers.sysconfig import DockerStorageSetupSysconfig, DirsrvSysconfig
from insights.parsers.sysconfig import CorosyncSysconfig
from insights.parsers.sysconfig import IfCFGStaticRoute
from insights.parsers.sysconfig import NetworkSysconfig
from insights.parsers.sysconfig import GrubSysconfig
from insights.parsers.sysconfig import OracleasmSysconfig
from insights.parsers.sysconfig import NfsSysconfig
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

SSHDSYSCONFIG = """
# Configuration file for the sshd service.

# The server keys are automatically generated if they are missing.
# To change the automatic creation, adjust sshd.service options for
# example using  systemctl enable sshd-keygen@dsa.service  to allow creation
# of DSA key or  systemctl mask sshd-keygen@rsa.service  to disable RSA key
# creation.

# System-wide crypto policy:
# To opt-out, uncomment the following line
# CRYPTO_POLICY=
CRYPTO_POLICY=
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
CONTEXT_PATH_DEVICE_1 = "etc/sysconfig/network-scripts/route-test-net"

STATIC_ROUTE_1 = """
ADDRESS0=10.65.223.0
NETMASK0=255.255.254.0
GATEWAY0=10.65.223.1
""".strip()

DOCKER_CONFIG_STORAGE = """
DOCKER_STORAGE_OPTIONS="--storage-driver devicemapper --storage-opt dm.fs=xfs --storage-opt dm.thinpooldev=/dev/mapper/dockervg-docker--pool --storage-opt dm.use_deferred_removal=true --storage-opt dm.use_deferred_deletion=true"
""".strip()

NETWORK_SYSCONFIG = """
NETWORKING=yes
HOSTNAME=rhel7-box
GATEWAY=172.31.0.1
NM_BOND_VLAN_ENABLED=no
""".strip()

GRUB_SYSCONFIG = """

GRUB_TIMEOUT=1
GRUB_DISTRIBUTOR="$(sed 's, release .*$,,g' /etc/system-release)"
GRUB_DEFAULT=saved
GRUB_DISABLE_SUBMENU=true
GRUB_TERMINAL_OUTPUT="console"
GRUB_CMDLINE_LINUX="console=ttyS0 console=ttyS0,115200n8 no_timer_check net.ifnames=0 crashkernel=auto"
GRUB_DISABLE_RECOVERY="true"
GRUB_ENABLE_BLSCFG=true
""".strip()

ORACLEASM_SYSCONFIG = """
#
# This is a configuration file for automatic loading of the Oracle
# Automatic Storage Management library kernel driver.  It is generated
# By running /etc/init.d/oracleasm configure.  Please use that method
# to modify this file
#
# ORACLEASM_ENABELED: 'true' means to load the driver on boot.
ORACLEASM_ENABLED=true
# ORACLEASM_UID: Default user owning the /dev/oracleasm mount point.
ORACLEASM_UID=oracle
# ORACLEASM_GID: Default group owning the /dev/oracleasm mount point.
ORACLEASM_GID=oinstall
# ORACLEASM_SCANBOOT: 'true' means scan for ASM disks on boot.
ORACLEASM_SCANBOOT=true
# ORACLEASM_SCANORDER: Matching patterns to order disk scanning
ORACLEASM_SCANORDER="dm"
# ORACLEASM_SCANEXCLUDE: Matching patterns to exclude disks from scan
ORACLEASM_SCANEXCLUDE="sd"
""".strip()

NFS_SYSCONFIG = """
# Optional arguments passed to rpc.nfsd. See rpc.nfsd(8)
RPCNFSDARGS="--rdma=20049"
# Port rpc.statd should listen on.
#STATD_PORT=662
# Enable usage of gssproxy. See gssproxy-mech(8).
GSS_USE_PROXY="yes"
# Optional arguments passed to rpc.svcgssd. See rpc.svcgssd(8)
RPCSVCGSSDARGS=""
# Optional arguments passed to blkmapd. See blkmapd(8)
BLKMAPDARGS=""
RPCNFSDCOUNT=256
""".strip()


def test_sysconfig_doc():
    env = {
            'chronyd_syscfg': ChronydSysconfig(context_wrap(CHRONYDSYSCONFIG)),
            'ntpd_syscfg': NtpdSysconfig(context_wrap(NTPDSYSCONFIG)),
            'docker_syscfg': DockerSysconfig(context_wrap(DOCKERSYSCONFIG)),
            'docker_syscfg_storage': DockerSysconfigStorage(context_wrap(DOCKER_CONFIG_STORAGE)),
            'httpd_syscfg': HttpdSysconfig(context_wrap(HTTPDSYSCONFIG)),
            'irqb_syscfg': IrqbalanceSysconfig(context_wrap(IRQBALANCESYSCONFIG)),
            'vwho_syscfg': VirtWhoSysconfig(context_wrap(VIRTWHOSYSCONFIG)),
            'mongod_syscfg': MongodSysconfig(context_wrap(MONGODSYSCONFIG)),
            'memcached_syscfg': MemcachedSysconfig(context_wrap(MEMCACHEDSYSCONFIG)),
            'libvirt_guests_syscfg': LibvirtGuestsSysconfig(context_wrap(LIBVIRTGUESTSSYSCONFIG)),
            'prelink_syscfg': PrelinkSysconfig(context_wrap(PRELINKSYSCONFIG)),
            'u2d_syscfg': Up2DateSysconfig(context_wrap(UP2DATESYSCONFIG)),
            'netcs_syscfg': NetconsoleSysconfig(context_wrap(NETCONSOLESYSCONFIG)),
            'sshd_syscfg': SshdSysconfig(context_wrap(SSHDSYSCONFIG)),
            'pps_syscfg': PuppetserverSysconfig(context_wrap(PUPPETSERVERCONFIG)),
            'ft_syscfg': ForemanTasksSysconfig(context_wrap(FOREMANTASKSYSCONFG)),
            'dss_syscfg': DockerStorageSetupSysconfig(context_wrap(DOCKERSTORAGESETUPSYSCONFG)),
            'dirsrv_syscfg': DirsrvSysconfig(context_wrap(DIRSRVSYSCONFG)),
            'cs_syscfg': CorosyncSysconfig(context_wrap(COROSYNCSYSCONFIG)),
            'conn_info': IfCFGStaticRoute(context_wrap(STATIC_ROUTE_1, CONTEXT_PATH_DEVICE_1)),
            'net_syscfg': NetworkSysconfig(context_wrap(NETWORK_SYSCONFIG)),
            'nfs_syscfg': NfsSysconfig(context_wrap(NFS_SYSCONFIG)),
            'grub_syscfg': GrubSysconfig(context_wrap(GRUB_SYSCONFIG)),
            'oracleasm_syscfg': OracleasmSysconfig(context_wrap(ORACLEASM_SYSCONFIG))
          }
    failed, total = doctest.testmod(sysconfig, globs=env)
    assert failed == 0
