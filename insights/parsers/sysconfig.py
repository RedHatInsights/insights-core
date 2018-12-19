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

NtpdSysconfig - file ``/etc/sysconfig/ntpd``
--------------------------------------------

PrelinkSysconfig - file ``/etc/sysconfig/prelink``
--------------------------------------------------

PuppetserverSysconfig - file ``/etc/sysconfig/puppetserver``
------------------------------------------------------------

Up2DateSysconfig - file ``/etc/sysconfig/rhn/up2date``
------------------------------------------------------

VirtWhoSysconfig - file ``/etc/sysconfig/virt-who``
---------------------------------------------------

IfCFGStaticRoute - files ``/etc/sysconfig/network-scripts/route-*``
-------------------------------------------------------------------
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

        >>> conn_info.static_route
        'test-net'

    """
    @property
    def static_route(self):
        """(str): static route file name derived from file path"""
        return self.file_name.split("route-", 1)[1]
