"""
Sysconfig - files in ``/etc/sysconfig/``
========================================

This is a collection of parsers that all deal with the system's configuration
files under the ``/etc/sysconfig/`` folder.  Parsers included in this module
are:

CorosyncSysconfig - file ``/etc/sysconfig/corosync``
----------------------------------------------------

ChronydSysconfig - file ``/etc/sysconfig/chronyd``
--------------------------------------------------

DirsrvSysconfig - file ``/etc/sysconfig/dirsrv``
------------------------------------------------

DockerStorageSetupSysconfig - file ``/etc/sysconfig/docker-storage-setup``
--------------------------------------------------------------------------

DockerSysconfig - file ``/etc/sysconfig/docker``
------------------------------------------------

DockerSysconfigStorage - file ``/etc/sysconfig/docker-storage``
---------------------------------------------------------------

ForemanTasksSysconfig - file ``/etc/sysconfig/foreman-tasks``
-------------------------------------------------------------

HttpdSysconfig - file ``/etc/sysconfig/httpd``
----------------------------------------------

IrqbalanceSysconfig - file ``/etc/sysconfig/irqbalance``
--------------------------------------------------------

KdumpSysconfig - file ``/etc/sysconfig/kdump``
----------------------------------------------

LibvirtGuestsSysconfig - file ``/etc/sysconfig/libvirt-guests``
---------------------------------------------------------------

MemcachedSysconfig - file ``/etc/sysconfig/memcached``
------------------------------------------------------

MongodSysconfig - file ``/etc/sysconfig/mongod``
------------------------------------------------

NetconsoleSysconfig -file ``/etc/sysconfig/netconsole``
-------------------------------------------------------

NetworkSysconfig -file ``/etc/sysconfig/network``
-------------------------------------------------

NfsSysconfig - file ``/etc/sysconfig/nfs``
------------------------------------------

NtpdSysconfig - file ``/etc/sysconfig/ntpd``
--------------------------------------------

PrelinkSysconfig - file ``/etc/sysconfig/prelink``
--------------------------------------------------

SshdSysconfig - file ``/etc/sysconfig/sshd``
--------------------------------------------

PuppetserverSysconfig - file ``/etc/sysconfig/puppetserver``
------------------------------------------------------------

Up2DateSysconfig - file ``/etc/sysconfig/rhn/up2date``
------------------------------------------------------

VirtWhoSysconfig - file ``/etc/sysconfig/virt-who``
---------------------------------------------------

IfCFGStaticRoute - files ``/etc/sysconfig/network-scripts/route-*``
-------------------------------------------------------------------

GrubSysconfig - files ``/etc/sysconfig/grub``
---------------------------------------------

OracleasmSysconfig - files ``/etc/sysconfig/oracleasm``
-------------------------------------------------------
"""


from insights import parser, SysconfigOptions, get_active_lines
from insights.specs import Specs


@parser(Specs.corosync)
class CorosyncSysconfig(SysconfigOptions):
    """
    This parser reads the ``/etc/sysconfig/corosync`` file.  It uses the
    ``SysconfigOptions`` parser class to convert the file into a dictionary of
    options.  It also provides the ``options`` property as a helper to retrieve
    the ``COROSYNC_OPTIONS`` variable.

    Sample Input::

        # COROSYNC_INIT_TIMEOUT specifies number of seconds to wait for corosync
        # initialization (default is one minute).
        COROSYNC_INIT_TIMEOUT=60
        # COROSYNC_OPTIONS specifies options passed to corosync command
        # (default is no options).
        # See "man corosync" for detailed descriptions of the options.
        COROSYNC_OPTIONS=""

    Examples:
        >>> 'COROSYNC_OPTIONS' in cs_syscfg
        True
        >>> cs_syscfg.options
        ''
    """
    @property
    def options(self):
        """ (str): The value of the ``COROSYNC_OPTIONS`` variable."""
        return self.data.get('COROSYNC_OPTIONS', '')


@parser(Specs.sysconfig_chronyd)
class ChronydSysconfig(SysconfigOptions):
    """
    This parser analyzes the ``/etc/sysconfig/chronyd`` configuration file.

    Sample Input::

      OPTIONS="-d"
      #HIDE="me"

    Examples:
        >>> 'OPTIONS' in chronyd_syscfg
        True
        >>> 'HIDE' in chronyd_syscfg
        False
        >>> chronyd_syscfg['OPTIONS']
        '-d'

    """
    pass


@parser(Specs.dirsrv)
class DirsrvSysconfig(SysconfigOptions):
    """
    This parser parses the `dirsrv` service's start-up configuration
    ``/etc/sysconfig/dirsrv``.

    Sample Input::

        #STARTPID_TIME=10 ; export STARTPID_TIME
        #PID_TIME=600 ; export PID_TIME
        KRB5CCNAME=/tmp/krb5cc_995
        KRB5_KTNAME=/etc/dirsrv/ds.keytab

    Examples:
        >>> dirsrv_syscfg.get('KRB5_KTNAME')
        '/etc/dirsrv/ds.keytab'
        >>> 'PID_TIME' in dirsrv_syscfg
        False
    """
    pass


@parser(Specs.docker_storage_setup)
class DockerStorageSetupSysconfig(SysconfigOptions):
    """
    Parser for parsing ``/etc/sysconfig/docker-storage-setup``

    Sample Input::

        VG=vgtest
        AUTO_EXTEND_POOL=yes
        ##name = mydomain
        POOL_AUTOEXTEND_THRESHOLD=60
        POOL_AUTOEXTEND_PERCENT=20

    Examples:
        >>> dss_syscfg['VG'] # Pseudo-dict access
        'vgtest'
        >>> 'name' in dss_syscfg
        False
        >>> dss_syscfg.get('POOL_AUTOEXTEND_THRESHOLD')
        '60'

    """
    pass


@parser(Specs.docker_sysconfig)
class DockerSysconfig(SysconfigOptions):
    """
    Parser for parsing the ``/etc/sysconfig/docker`` file using the standard
    ``SysconfigOptions`` parser class.  The 'OPTIONS' variable is also provided
    in the ``options`` property as a convenience.

    Sample Input::

        OPTIONS="--selinux-enabled"
        DOCKER_CERT_PATH="/etc/docker"

    Examples:
        >>> 'OPTIONS' in docker_syscfg
        True
        >>> docker_syscfg['OPTIONS']
        '--selinux-enabled'
        >>> docker_syscfg.options
        '--selinux-enabled'
        >>> docker_syscfg['DOCKER_CERT_PATH']
        '/etc/docker'
    """
    @property
    def options(self):
        """ Return the value of the 'OPTIONS' variable, or '' if not defined. """
        return self.data.get('OPTIONS', '')


@parser(Specs.docker_storage)
class DockerSysconfigStorage(SysconfigOptions):
    """
    A Parser for /etc/sysconfig/docker-storage.

    Sample input::
        DOCKER_STORAGE_OPTIONS="--storage-driver devicemapper --storage-opt dm.fs=xfs --storage-opt dm.thinpooldev=/dev/mapper/dockervg-docker--pool --storage-opt dm.use_deferred_removal=true --storage-opt dm.use_deferred_deletion=true"

    Examples:
        >>> 'DOCKER_STORAGE_OPTIONS' in docker_syscfg_storage
        True
        >>> docker_syscfg_storage["DOCKER_STORAGE_OPTIONS"]
        '--storage-driver devicemapper --storage-opt dm.fs=xfs --storage-opt dm.thinpooldev=/dev/mapper/dockervg-docker--pool --storage-opt dm.use_deferred_removal=true --storage-opt dm.use_deferred_deletion=true'
        >>> docker_syscfg_storage.storage_options
        '--storage-driver devicemapper --storage-opt dm.fs=xfs --storage-opt dm.thinpooldev=/dev/mapper/dockervg-docker--pool --storage-opt dm.use_deferred_removal=true --storage-opt dm.use_deferred_deletion=true'
    """
    @property
    def storage_options(self):
        """ Return the value of the 'DOCKER_STORAGE_OPTIONS' variable, or '' if not defined. """
        return self.data.get('DOCKER_STORAGE_OPTIONS', '')


@parser(Specs.foreman_tasks_config)
class ForemanTasksSysconfig(SysconfigOptions):
    """
    Parse the ``/etc/sysconfig/foreman-tasks`` configuration file.

    Sample configuration file::

        FOREMAN_USER=foreman
        BUNDLER_EXT_HOME=/usr/share/foreman
        RAILS_ENV=production
        FOREMAN_LOGGING=warn

    Examples:
        >>> ft_syscfg['RAILS_ENV']
        'production'
        >>> 'AUTO' in ft_syscfg
        False
    """
    pass


@parser(Specs.sysconfig_httpd)
class HttpdSysconfig(SysconfigOptions):
    """
    This parser analyzes the ``/etc/sysconfig/httpd`` configuration file.

    Sample Input::

        HTTPD=/usr/sbin/httpd.worker
        #
        # To pass additional options (for instance, -D definitions) to the
        # httpd binary at startup, set OPTIONS here.
        #
        OPTIONS=

    Examples:
        >>> httpd_syscfg['HTTPD']
        '/usr/sbin/httpd.worker'
        >>> httpd_syscfg.get('OPTIONS')
        ''
        >>> 'NOOP' in httpd_syscfg
        False
    """
    pass


@parser(Specs.sysconfig_irqbalance)
class IrqbalanceSysconfig(SysconfigOptions):
    """
    This parser analyzes the ``/etc/sysconfig/irqbalance`` configuration file.

    Sample Input::

        #IRQBALANCE_ONESHOT=yes
        #
        IRQBALANCE_BANNED_CPUS=f8
        IRQBALANCE_ARGS="-d"

    Examples:
        >>> irqb_syscfg['IRQBALANCE_BANNED_CPUS']
        'f8'
        >>> irqb_syscfg.get('IRQBALANCE_ARGS')  # quotes will be stripped
        '-d'
        >>> irqb_syscfg.get('IRQBALANCE_ONESHOT') is None
        True
        >>> 'ONESHOT' in irqb_syscfg
        False
    """
    pass


@parser(Specs.sysconfig_kdump)
class KdumpSysconfig(SysconfigOptions):
    """
    This parser reads data from the ``/etc/sysconfig/kdump`` file.

    This parser sets the following properties for ease of access:

    * KDUMP_COMMANDLINE
    * KDUMP_COMMANDLINE_REMOVE
    * KDUMP_COMMANDLINE_APPEND
    * KDUMP_KERNELVER
    * KDUMP_IMG
    * KDUMP_IMG_EXT
    * KEXEC_ARGS

    These are set to the value of the named variable in the kdump sysconfig
    file, or '' if not found.
    """
    KDUMP_KEYS = [
        'KDUMP_COMMANDLINE',
        'KDUMP_COMMANDLINE_REMOVE',
        'KDUMP_COMMANDLINE_APPEND',
        'KDUMP_KERNELVER',
        'KDUMP_IMG',
        'KDUMP_IMG_EXT',
        'KEXEC_ARGS',
    ]

    def parse_content(self, content):
        super(KdumpSysconfig, self).parse_content(content)
        for key in self.KDUMP_KEYS:
            setattr(self, key, self.data.get(key, ''))


@parser(Specs.sysconfig_libvirt_guests)
class LibvirtGuestsSysconfig(SysconfigOptions):
    """
    This parser analyzes the ``/etc/sysconfig/libvirt-guests`` configuration file.

    Sample Input::

        # URIs to check for running guests
        # example: URIS='default xen:/// vbox+tcp://host/system lxc:///'
        #URIS=default
        ON_BOOT=ignore

    Examples:
        >>> libvirt_guests_syscfg.get('ON_BOOT')
        'ignore'
    """
    pass


@parser(Specs.sysconfig_memcached)
class MemcachedSysconfig(SysconfigOptions):
    """
    This parser analyzes the ``/etc/sysconfig/memcached`` configuration file.

    Sample Input::

        PORT="11211"
        USER="memcached"
        # max connection 2048
        MAXCONN="2048"
        # set ram size to 2048 - 2GiB
        CACHESIZE="4096"
        # disable UDP and listen to loopback ip 127.0.0.1, for network connection use real ip e.g., 10.0.0.5
        OPTIONS="-U 0 -l 127.0.0.1"

    Examples:
        >>> memcached_syscfg.get('OPTIONS')
        '-U 0 -l 127.0.0.1'
    """
    pass


@parser(Specs.sysconfig_mongod)
class MongodSysconfig(SysconfigOptions):
    """
    A parser for analyzing the ``mongod`` service configuration file, like
    '/etc/sysconfig/mongod' and '/etc/opt/rh/rh-mongodb26/sysconfig/mongod'.

    Sample Input::

        OPTIONS="--quiet -f /etc/mongod.conf"

    Examples:
        >>> mongod_syscfg.get('OPTIONS')
        '--quiet -f /etc/mongod.conf'
        >>> mongod_syscfg.get('NO_SUCH_OPTION') is None
        True
        >>> 'NOSUCHOPTION' in mongod_syscfg
        False
    """
    pass


@parser(Specs.netconsole)
class NetconsoleSysconfig(SysconfigOptions):
    '''
    Parse the ``/etc/sysconfig/netconsole`` file.

    Sample Input::

        # The local port number that the netconsole module will use
        LOCALPORT=6666

    Examples:
        >>> 'LOCALPORT' in netcs_syscfg
        True
        >>> 'DEV' in netcs_syscfg
        False
    '''
    pass


@parser(Specs.sysconfig_network)
class NetworkSysconfig(SysconfigOptions):
    """
    This parser parses the ``/etc/sysconfig/network`` configuration file

    Sample Input::

        NETWORKING=yes
        HOSTNAME=rhel7-box
        GATEWAY=172.31.0.1
        NM_BOND_VLAN_ENABLED=no

    Examples:

        >>> 'NETWORKING' in net_syscfg
        True
        >>> net_syscfg['GATEWAY']
        '172.31.0.1'
    """
    pass


@parser(Specs.sysconfig_nfs)
class NfsSysconfig(SysconfigOptions):
    """
    A parser for analyzing the ``/etc/sysconfig/nfs`` configuration file.

    .. note::
        In some RHEL version, both the file ``/etc/nfs.conf`` and file
        ``/etc/sysconfig/nfs`` exist, and take effect at the same time for NFS
        services on the host. And it's possible that there are overlaps between
        the two configuration files.
        A combiner for the two configuration files was considered.
        Since the two files' coverage are different, and it is quite complicate
        to enumerate all the configuration options and combine them properly,
        and also, ``/etc/sysconfig/nfs`` is deprecated in lately RHEL releases.
        We deselect it as a consequence.

    Sample Input::

      RPCNFSDARGS="--rdma=20049"
      #STATD_PORT=662

    Examples:
        >>> 'RPCNFSDARGS' in nfs_syscfg
        True
        >>> nfs_syscfg['RPCNFSDARGS']
        '--rdma=20049'
        >>> 'STATD_PORT' in nfs_syscfg
        False
    """
    pass


@parser(Specs.sysconfig_ntpd)
class NtpdSysconfig(SysconfigOptions):
    """
    A parser for analyzing the ``/etc/sysconfig/ntpd`` configuration file.

    Sample Input::

      OPTIONS="-x -g"
      #HIDE="me"

    Examples:
        >>> 'OPTIONS' in ntpd_syscfg
        True
        >>> 'HIDE' in ntpd_syscfg
        False
        >>> ntpd_syscfg['OPTIONS']
        '-x -g'
    """
    pass


@parser(Specs.sysconfig_prelink)
class PrelinkSysconfig(SysconfigOptions):
    """
    A parser for analyzing the ``/etc/sysconfig/prelink`` configuration file.

    Sample Input::

        # Set this to no to disable prelinking altogether
        # (if you change this from yes to no prelink -ua
        # will be run next night to undo prelinking)
        PRELINKING=no

        # Options to pass to prelink
        # -m    Try to conserve virtual memory by allowing overlapping
        #       assigned virtual memory slots for libraries which
        #       never appear together in one binary
        # -R    Randomize virtual memory slot assignments for libraries.
        #       This makes it slightly harder for various buffer overflow
        #       attacks, since library addresses will be different on each
        #       host using -R.
        PRELINK_OPTS=-mR

    Examples:
        >>> prelink_syscfg.get('PRELINKING')
        'no'
    """
    pass


@parser(Specs.sysconfig_sshd)
class SshdSysconfig(SysconfigOptions):
    """
    A parser for analyzing the ``/etc/sysconfig/sshd`` configuration file.

    Sample Input::

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

    Examples:
        >>> sshd_syscfg.get('CRYPTO_POLICY')
        ''
        >>> 'NONEXISTENT_VAR' in sshd_syscfg
        False
        >>> 'CRYPTO_POLICY' in sshd_syscfg
        True
    """
    pass


@parser(Specs.puppetserver_config)
class PuppetserverSysconfig(SysconfigOptions):
    """
    Parse the ``/etc/sysconfig/puppetserver`` configuration file.

    Sample configuration file::

        USER="puppet"
        GROUP="puppet"
        INSTALL_DIR="/opt/puppetlabs/server/apps/puppetserver"
        CONFIG="/etc/puppetlabs/puppetserver/conf.d"
        START_TIMEOUT=300

    Examples:
        >>> pps_syscfg['START_TIMEOUT']
        '300'
        >>> 'AUTO' in pps_syscfg
        False
    """
    pass


@parser(Specs.up2date)
class Up2DateSysconfig(SysconfigOptions):
    """
    Class to parse the ``/etc/sysconfig/rhn/up2date``

    Typical content example::

        serverURL[comment]=Remote server URL
        #serverURL=https://rhnproxy.glb.tech.markit.partners
        serverURL=https://rhnproxy.glb.tech.markit.partners/XMLRPC

    Examples:
        >>> 'serverURL' in u2d_syscfg
        True
        >>> u2d_syscfg['serverURL']
        'https://rhnproxy.glb.tech.markit.partners/XMLRPC'
    """
    def parse_content(self, content):
        up2date_info = {}
        for line in get_active_lines(content):
            if "[comment]" not in line and '=' in line:
                key, val = line.split('=')
                up2date_info[key.strip()] = val.strip()
        self.data = up2date_info


@parser(Specs.sysconfig_virt_who)
class VirtWhoSysconfig(SysconfigOptions):
    """
    A parser for analyzing the ``/etc/sysconfig/virt-who`` configuration file.

    Sample Input::

        # Register ESX machines using vCenter
        # VIRTWHO_ESX=0
        # Register guests using RHEV-M
        VIRTWHO_RHEVM=1

        # Options for RHEV-M mode
        VIRTWHO_RHEVM_OWNER=
        TEST_OPT="A TEST"

    Examples:
        >>> vwho_syscfg['VIRTWHO_RHEVM']
        '1'
        >>> vwho_syscfg.get('VIRTWHO_RHEVM_OWNER')
        ''
        >>> vwho_syscfg.get('NO_SUCH_OPTION') is None
        True
        >>> 'NOSUCHOPTION' in vwho_syscfg
        False
        >>> vwho_syscfg.get('TEST_OPT')  # Quotes are stripped
        'A TEST'
    """
    pass


@parser(Specs.ifcfg_static_route)
class IfCFGStaticRoute(SysconfigOptions):
    """
    IfCFGStaticRoute is a parser for the static route network interface
    definition files in ``/etc/sysconfig/network-scripts``.  These are
    pulled into the network scripts using ``source``, so they are mainly
    ``bash`` environment declarations of the form **KEY=value**.  These
    are stored in the ``data`` property as a dictionary.  Quotes surrounding
    the value

    Because this parser reads multiple files, the interfaces are stored as a
    list within the parser and need to be iterated through in order to find
    specific interfaces.

    Sample configuration from a static connection in file ``/etc/sysconfig/network-scripts/rute-test-net``::

        ADDRESS0=10.65.223.0
        NETMASK0=255.255.254.0
        GATEWAY0=10.65.223.1

    Examples:

        >>> conn_info['ADDRESS0']
        '10.65.223.0'
        >>> conn_info.static_route_name
        'test-net'

    Attributes:
        static_route_name (str): static route name

    """
    def parse_content(self, content):
        self.static_route_name = self.file_name.split("route-", 1)[1]
        super(IfCFGStaticRoute, self).parse_content(content)


@parser(Specs.sysconfig_grub)
class GrubSysconfig(SysconfigOptions):
    """
    Class to parse the ``/etc/sysconfig/grub``

    ``/etc/sysconfig/grub`` is a symlink of ``/etc/default/grub`` file

    Typical content example::

        GRUB_TIMEOUT=1
        GRUB_DISTRIBUTOR="$(sed 's, release .*$,,g' /etc/system-release)"
        GRUB_DEFAULT=saved
        GRUB_DISABLE_SUBMENU=true
        GRUB_TERMINAL_OUTPUT="console"
        GRUB_CMDLINE_LINUX="console=ttyS0 console=ttyS0,115200n8 no_timer_check net.ifnames=0 crashkernel=auto"
        GRUB_DISABLE_RECOVERY="true"
        GRUB_ENABLE_BLSCFG=true

    Examples:
        >>> grub_syscfg.get('GRUB_ENABLE_BLSCFG')
        'true'
        >>> 'NONEXISTENT_VAR' in grub_syscfg
        False
        >>> 'GRUB_ENABLE_BLSCFG' in grub_syscfg
        True

    """
    pass


@parser(Specs.sysconfig_oracleasm)
class OracleasmSysconfig(SysconfigOptions):
    """
    Class to parse the ``/etc/sysconfig/oracleasm``

    Typical content example::

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

    Examples:
        >>> oracleasm_syscfg.get('ORACLEASM_SCANBOOT')
        'true'
        >>> 'ORACLEASM_SCANORDER' in oracleasm_syscfg
        True
        >>> 'ORACLEASM_SCANEXCLUDE_1' in oracleasm_syscfg
        False

    """
    pass
