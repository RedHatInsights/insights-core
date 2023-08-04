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
# TODO: replace DmesgLineList with '/proc/version' (not collected yet)
from insights.parsers.dmesg import DmesgLineList
from insights.parsers.installed_rpms import InstalledRpm, InstalledRpms
from insights.parsers.os_release import OsRelease
from insights.parsers.redhat_release import RedhatRelease
from insights.parsers.uname import Uname

RHEL_KEYS = ['rhel', 'red hat enterprise linux']
OTHER_LINUX_KEYS = {
    # other_linux: (dmesg-keywords, release-packages)
    'Fedora': (
        ['fedora'],
        ['fedora-release']),
    'CentOS': (
        ['centos'],
        ['centos-stream-release', 'centos-release']),
    'Oracle': (
        ['oracle'],
        ['enterprise-release', 'oraclelinux-release']),
    'CloudLinux': (
        ['cloudlinux'],
        ['cloudlinux-release']),
    'ClearOS': (
        ['clearos'],
        ['clearos-release']),
    'AlmaLinux': (
        ['almalinux'],
        ['almalinux-release']),
    'Rocky': (
        ['rockylinux', 'rocky'],
        ['rocky-release']),
    'Scientific': (
        [],  # Empty
        ['sl-release']),
    'SUSE': (
        ['suse', 'sles', 'novell'],
        ['sles-release', 'sles_es-release-server']),
}
# TODO:
# Update the CONVERT2RHEL_SUPPORTED list when necessary
CONVERT2RHEL_SUPPORTED = ['CentOS']
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
THRESHOLD = 0.75
"""Threshold of the must-install packages to identify NON-RHEL"""


def _from_os_release(osr):
    """
    Internal function to check the `/etc/os-release`.
    """
    def _filter(name):
        """Remove falsy or items contain RHEL info"""
        if not name or any(k in name.lower() for k in RHEL_KEYS):
            return False
        return name

    names = list(filter(_filter, [osr.get('ID'), osr.get('NAME'),
                                  osr.get('PRETTY_NAME')]))
    if names:
        # NON-RHEL: /etc/os-release
        return dict(other_linux=names[-1])
    # RHEL
    return dict(other_linux='RHEL')


def _from_redhat_release(rhr):
    """
    Internal function to check the `/etc/redhat-release`.
    """
    if not rhr.is_rhel:
        return dict(other_linux=rhr.product)
    # RHEL
    return dict(other_linux='RHEL')


def _from_uname(uname):
    """
    Internal function to check the `uname -a` output.

    1. Oracle kernels may contain 'uek' or 'ol' in the kernel NVR.
    2. Fedora kernels contains 'fc' in the NVR.
    3. RHEL kernels have '.el' in the NVR
       RHEL based Linux kernels may also have the '.el' in the NVR,
       but they are also checked in other sub-combiners.
    4. Otherwise, flag it as an "Unknown"
    """
    LINUX_UNAME_KEYS = [
        ('Oracle', ['uek', 'ol']),
        ('Fedora', ['fc']),
        ('RHEL', ['.el']),  # the last item
    ]
    kernel = uname.kernel
    release = 'Unknown'
    for rel, keys in LINUX_UNAME_KEYS:
        if any(key in kernel for key in keys):
            release = rel
            break
    if 'RHEL' != release:
        return dict(other_linux=release, kernel=kernel)
    # Not Sure
    return dict()


def _from_dmesg(dmesg):
    """
    Internal function to check the `dmesg` output.

    The `dmesg` includes a line containing the kernel build information,
    e.g. the build host and GCC version.
    If this line doesn't contain 'redhat.com' then we can assume the kernel
    wasn't built on a Red Hat machine and this should be flagged.
    """
    line = dmesg.linux_version[0]['raw_message']
    low_line = line.lower()
    if 'redhat.com' not in low_line:
        release = 'Unknown'
        for rel, keys in OTHER_LINUX_KEYS.items():
            if any(kw in low_line for kw in keys[0]):
                release = rel
                break
        return dict(other_linux=release, build_info=line)
    # Not Sure
    return dict()


def _from_installed_rpms(rpms, uname):
    """
    Internal function to check the `rpm -qa --qf ...` output.

    Two parts are included, see below:
    """
    # Part-1: the known non-rhel-release packages exists
    for rel, pkgs in OTHER_LINUX_KEYS.items():
        for pkg_name in pkgs[1]:
            pkg = rpms.newest(pkg_name)
            if pkg:
                return dict(other_linux=rel, release=pkg.nvr)
    # Part-2: too many must-install packages are NOT from Red Hat
    # - more than THRESHOLD packages are not signed and not provided by Red Hat
    #   faulty_packages >= THRESHOLD * must-install packages
    installed_packages = 0
    vendor, ng_pkgs = '', set()
    if uname:
        # check the booting 'kernel' first
        installed_packages += 1
        boot_kn = InstalledRpm.from_package('kernel-{0}'.format(uname.kernel))
        for pkg in rpms.packages.get('kernel', []):
            if pkg == boot_kn:
                vendor = pkg.vendor
                if pkg.redhat_signed is False and vendor != 'Red Hat, Inc.':
                    ng_pkgs.add(pkg.nvr)
                # check the booting kernel only
                break
    # check other packages
    for pkg_name in MINIMUM_RHEL_PKGS:
        pkg = rpms.newest(pkg_name)
        if pkg:
            # count the package only when it's installed
            installed_packages += 1
            if pkg.redhat_signed is False and pkg.vendor != 'Red Hat, Inc.':
                ng_pkgs.add(pkg.nvr)
    # check the result
    if len(ng_pkgs) >= round(THRESHOLD * installed_packages) > 0:
        # NON-RHEL: more than THRESHOLD packages are NOT from Red Hat
        ret = dict(other_linux='Unknown', faulty_packages=sorted(ng_pkgs))
        if vendor:
            ret.update(kernel_vendor=vendor)
            # try to get the release from kernel vendor
            if 'red hat' not in vendor.lower():
                sep = ',' if ',' in vendor else ' '
                release = vendor.split(sep)[0].strip()
                ret.update(other_linux=release)
        return ret
    # RHEL
    return dict(other_linux='RHEL')


@combiner(optional=[Uname, DmesgLineList, InstalledRpms,
                    OsRelease, RedhatRelease])
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
        >>> osr.name == "Oracle Linux Server"
        True
        >>> osr.is_rhel_compatible
        False
        >>> sorted(osr.reasons.keys())
        ['build_info', 'faulty_packages', 'kernel', 'kernel_vendor']
        >>> 'version kernel-4.18.0-372.19.1.el8_6uek' in osr.reasons['build_info']
        True
        >>> osr.reasons['kernel']
        '4.18.0-372.19.1.el8_6uek.x86_64'
        >>> osr.reasons['kernel_vendor'] == 'Oracle America'
        True
        >>> 'glibc-2.28-211.el8' in osr.reasons['faulty_packages']
        True
    """
    def __init__(self, uname, dmesg, rpms, osr, rhr):
        def _update_other_linux(ret, data):
            if data.get('other_linux') == 'Unknown' and 'other_linux' in ret:
                # Don't update 'other_linux' to 'Unknown' if identified already
                data.pop('other_linux')
            ret.update(data)
            return ret

        self._release = 'RHEL'
        self._reasons = {}
        _dmesg = dmesg.linux_version if dmesg else dmesg
        if not list(filter(None, [uname, _dmesg, rpms])):
            # When uname, dmesg, and rpms are all unavailable
            if osr or rhr:
                # Use 'os-release' and 'redhat-release
                ret = _from_os_release(osr) if osr else dict()
                if ret.get('other_linux', 'RHEL') == 'RHEL':
                    ret.update(_from_redhat_release(rhr)) if rhr else None
                if ret.get('other_linux', 'RHEL') != 'RHEL':
                    self._release = ret['other_linux']
                    self._reasons = {'reason': 'NON-RHEL: os-release/redhat-release'}
            else:
                # Nothing means NON-RHEL
                self._release = 'Unknown'
                self._reasons = {'reason': 'Nothing available to check'}
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
                self._release = result.pop('other_linux')
                self._reasons = result
        self._name = osr.get('NAME', self._release) if osr else self._release

    @property
    def is_rhel(self):
        """
        Returns True if it's RHEL, False for NON-RHEL.
        """
        return self._release == 'RHEL'

    @property
    def is_rhel_compatible(self):
        """
        Returns True if convert2rhel could convert
        """
        return self._release in CONVERT2RHEL_SUPPORTED

    @property
    def release(self):
        """
        Returns the estimated release name of the running Linux.
        """
        return self._release

    @property
    def name(self):
        """
        Returns the name of the OS. Generally it's the "NAME" of the
        '/etc/os-release' file, or it's the same as the `release` when
        the '/etc/os-release' is not available.
        """
        return self._name

    @property
    def reasons(self):
        """
        Returns a dict indicating why the host is a NON-RHEL.  Empty when
        it's an RHEL. The keys include::

            kernel (str): the kernel package
            build_info (str): the kernel build information
            release (str): the release package
            faulty_packages (list): the packages that are not signed and not
                provided by Red Hat
            reason (str): a string when nothing is available to check
        """
        return self._reasons

    @property
    def product(self):
        """ Alias of `release`. Keep backward compatible """
        return self._release
