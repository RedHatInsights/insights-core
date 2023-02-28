"""
OSRelease
=========
The ``OSRelease`` combiner uses the following parsers to try to identify if the
current host is installed with a "Red Hat Enterprise Linux" system.

    - :py:class:`insights.parsers.uname.Uname`
    - :py:class:`insights.parsers.dmesg.DmesgLineList`
    - :py:class:`insights.parsers.installed_rpms.InstalledRpms`

It provides an attribute `is_rhel` that indicates if the host is "RHEL" or not.
It also provides an attribute `release` which returns the estimated OS release
name of the system, "Unknown" will be returned by default when cannot identify
the OS.

* TODO:
  The lists of keywords to identify NON-RHEL system of each sub-combiners are
  based on our current knowledge, and maybe not sufficient. It needs to be
  updated timely according to new found Linux distributions.
"""
from insights.core.filters import add_filter
from insights.core.plugins import combiner
from insights.parsers.dmesg import DmesgLineList
from insights.parsers.installed_rpms import InstalledRpm, InstalledRpms
from insights.parsers.uname import Uname

# Get "Linux version" from `dmesg`
DMESG_LINUX_BUILD_INFO = 'Linux version'
add_filter(DmesgLineList, DMESG_LINUX_BUILD_INFO)
DmesgLineList.keep_scan("linux_version", DMESG_LINUX_BUILD_INFO, num=1)
# Must-install packages for minimum RHEL system
MINIMUM_RHEL_PKGS = [
    # 'kernel' is must-install too, it's checked individually (booting kernel)
    'audit-libs',
    'basesystem',
    'bash',
    'coreutils',
    'dbus',
    'dmidecode',
    'dnf',  # RHEL 8+
    'dracut',
    'filesystem',
    'firewalld',
    'glibc',
    'gmp',
    'krb5-libs',
    'libacl',
    'libgcc',
    'libselinux',
    'NetworkManager',
    'openssl-libs',
    'passwd',
    'redhat-release',  # RHEL 8+
    'redhat-release-server',  # RHEL 6/7
    'systemd',  # RHEL 7+
    'util-linux',
    'yum',  # RHEL 6/7
]
"""Must-install packages for minimum installed RHEL system."""
THRESHOLD = 0.7
"""Threshold rate of the required "MINIMUM_RHEL_PKGS" to identify RHEL system"""


def _from_uname(uname):
    """
    Internal function to check the `uname -a` output.

    1. Oracle kernels may contain 'uek' or 'ol' in the kernel NVR.
    2. Fedora kernels contains 'fc' in the NVR.
    3. RHEL kernels have '.el' in the NVR
       CentOS/Oracle/RockyLinux kernels may also have the '.el' in the NVR,
       but they are also checked in other sub-combiners.
    4. Otherwise, flag it as an "Unknown"
    """
    LINUX_UNAME_KEYS = [
        ('Oracle', ['uek', 'ol']),
        ('Fedora', ['fc']),
        ('RHEL', ['.el']),  # the last item
    ]
    kernel = uname.kernel
    other_linux = 'Unknown'
    for release, keys in LINUX_UNAME_KEYS:
        if any(key in kernel for key in keys):
            other_linux = release
            break
    if 'RHEL' != other_linux:
        return dict(other_linux=other_linux, kernel=kernel)
    # Not Sure
    return dict()


def _from_dmesg(dmesg):
    """
    Internal function to check the `dmesg` output.

    The `dmesg` includes a line containing the kernel build information,
    e.g. the build host and GCC version.
    If this line doesn't contain 'redhat.com' then we can assume the kernel
    wasn't built on a Red Hat machine and this should be flagged::

        'centos'                    -> CentOS Linux
        'oracle'                    -> Oracle Linux
        'suse', 'sles', or 'novell' -> SUSE Linux
        'fedora'                    -> Fedora Linux
        'rockylinux'                -> Rocky Linux
        others                      -> Unknown
    """
    OTHER_LINUX_KEYS = {
        'Oracle': ['oracle'],
        'Fedora': ['fedora'],
        'CentOS': ['centos'],
        'Rocky': ['rockylinux', 'rocky'],
        'SUSE': ['suse', 'sles', 'novell'],
    }
    line = dmesg.linux_version[0]['raw_message']
    low_line = line.lower()
    if 'redhat.com' not in low_line:
        other_linux = 'Unknown'
        for release, keys in OTHER_LINUX_KEYS.items():
            if any(kw in low_line for kw in keys):
                other_linux = release
                break
        return dict(other_linux=other_linux, build_info=line)
    # Not Sure
    return dict()


def _from_installed_rpms(rpms, uname):
    """
    Internal function to check the `rpm -qa ...` output.

    Two parts are included, see below:
    """
    # Part-1 of RPMs
    """
    # Part-1: the following packages exists
        'centos-release'        -> CentOS Linux
        'centos-stream-release' -> CentOS Stream
        'fedora-release'        -> Fedora
        'enterprise-release'    -> Oracle
        'oraclelinux-release'   -> Oracle
        'rocky-release'         -> Rocky Linux,
        'sl-release'            -> Scientific Linux
        'sles-release'          -> SUSE
    """
    OTHER_LINUX_RELEASE_PKGS = {
        'CentOS': ['centos-release', 'centos-stream-release'],
        'Fedora': ['fedora-release'],
        'Oracle': ['enterprise-release', 'oraclelinux-release'],
        'Rocky': ['rocky-release'],
        'Scientific': ['sl-release'],
        'SUSE': ['sles-release'],
    }
    for release, pkgs in OTHER_LINUX_RELEASE_PKGS.items():
        for pkg_name in pkgs:
            pkg = rpms.newest(pkg_name)
            if pkg:
                return dict(other_linux=release, release=pkg.nvr)

    # Part-2 of RPMs
    """
    # Part-2: too many must-install packages are not signed or provided by Red Hat
    # - faulty_packages >= (THRESHOLD * must-install packages)
    """
    KERNEL_VENDORS = {
        'Oracle': ['oracle'],
        'Rocky': ['rocky'],
        'SUSE': ['suse', 'novell'],
    }
    installed_packages = 0
    vendor, _ng_pkgs = '', set()
    if uname:
        # check the booting 'kernel' first
        installed_packages += 1
        boot_kn = InstalledRpm.from_package('kernel-{0}'.format(uname.kernel))
        for pkg in rpms.packages.get('kernel', []):
            if pkg == boot_kn:
                vendor = pkg.vendor
                if not (pkg.redhat_signed and
                        vendor and vendor == 'Red Hat, Inc.'):
                    _ng_pkgs.add(pkg.nvr)
                # check the booting kernel only
                break
    # check other packages
    for pkg_name in MINIMUM_RHEL_PKGS:
        pkg = rpms.newest(pkg_name)
        if pkg:
            # count the package only when it's installed
            installed_packages += 1
            if not (pkg.redhat_signed and
                    pkg.vendor and pkg.vendor == 'Red Hat, Inc.'):
                _ng_pkgs.add(pkg.nvr)
    if len(_ng_pkgs) >= round(THRESHOLD * installed_packages) > 0:
        # Unknown Linux: more than THRESHOLD packages are NOT from Red Hat
        other_linux = 'Unknown'
        for release, keys in KERNEL_VENDORS.items():
            if any(kw in vendor.lower() for kw in keys):
                # Known NON-RHEL from kernel vendor
                other_linux = release
                break
        ret = dict(other_linux=other_linux, faulty_packages=sorted(_ng_pkgs))
        ret.update(kernel_vendor=vendor) if vendor else None
        return ret
    # RHEL
    return dict(other_linux='RHEL')


@combiner(optional=[Uname, DmesgLineList, InstalledRpms])
class OSRelease(object):
    """
    A Combiner identifies whether the current Linux a Red Hat Enterprise Linux
    or not.

    Examples:
        >>> type(osr)
        <class 'insights.combiners.os_release.OSRelease'>
        >>> osr.is_rhel
        False
        >>> osr.release == "Oracle"
        True
        >>> sorted(osr.reasons.keys())
        ['build_info', 'faulty_packages', 'kernel', 'kernel_vendor']
        >>> 'Linux version kernel-4.18.0-372' in osr.reasons['build_info']
        True
        >>> osr.reasons['kernel']
        '4.18.0-372.19.1.el8_6uek.x86_64'
        >>> osr.reasons['kernel_vendor'] == 'Oracle America'
        True
        >>> 'glibc-2.28-211.el8' in osr.reasons['faulty_packages']
        True
    """
    def __init__(self, uname, dmesg, rpms):
        def _update_other_linux(ret, data):
            if data.get('other_linux') == 'Unknown' and 'other_linux' in ret:
                # Do not update the 'other_linux' if it's identified already
                data.pop('other_linux')
            ret.update(data)
            return ret

        self._is_rhel = True
        self._release = 'Red Hat Enterprise Linux'
        self._reasons = {}
        _dmesg = dmesg.linux_version if dmesg else dmesg
        if not list(filter(None, [uname, _dmesg, rpms])):
            # Nothing means NON-RHEL
            self._is_rhel = False
            self._release = 'Unknown'
            self._reasons = {'reason': 'Nothing to check'}
        else:
            # Uname -> Dmesg -> RPMs
            result = _from_uname(uname) if uname else dict()
            if dmesg and dmesg.linux_version:
                result.update(_update_other_linux(result, _from_dmesg(dmesg)))
            if rpms:
                result.update(_update_other_linux(
                                result, _from_installed_rpms(rpms, uname)))
            # 'other_linux' means NON-RHEL
            if 'other_linux' in result and result['other_linux'] != 'RHEL':
                self._is_rhel = False
                self._release = result.pop('other_linux')
                self._reasons = result

    @property
    def is_rhel(self):
        """
        Returns True if it's RHEL, False for NON-RHEL.
        """
        return self._is_rhel

    @property
    def release(self):
        """
        Returns the estimated release name of the running Linux.
        """
        return self._release

    @property
    def reasons(self):
        """
        Returns a dict indicating why the host is a NON-RHEL.  Empty when
        it's an RHEL. The keys include::

            kernel (str): the kernel package
            build_info (str): the kernel build information
            release (str): the release package
            faulty_packages (list): the packages that are not signed or provided by Red Hat
            reason (str): a string when nothing is available to check
        """
        return self._reasons

    @property
    def product(self):
        """ Alias of `release`. Keep backward compatible """
        return self._release
