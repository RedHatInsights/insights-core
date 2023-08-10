"""
OSRelease
=========
The ``OSRelease`` combiner uses the following parsers to try to identify if the
current host is installed with a "Red Hat Enterprise Linux" (RHEL) system.

    - :py:class:`insights.parsers.installed_rpms.InstalledRpms`
    - :py:class:`insights.parsers.uname.Uname`
    - :py:class:`insights.parsers.dmesg.DmesgLineList`
    - :py:class:`insights.parsers.os_release.OSRelease`
    - :py:class:`insights.parsers.redhat_release.RedhatRelease`

It provides an attribute `is_rhel` that indicates if the host is RHEL or not.
It also provides an attribute `release` which returns the estimated OS release
name of the system, "Unknown" will be returned by default when cannot identify
the OS.

* TODO::

    The lists of keywords to identify NON-RHEL system of each sub-combiners are
    based on our current knowledge, and may be not sufficient. It needs to be
    updated timely according to new found Linux Distributions.
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
"""Known NON-RHEL Linux Distributions."""
# TODO:
# Update the CONVERT2RHEL_SUPPORTED list when necessary
CONVERT2RHEL_SUPPORTED = ['CentOS']
# Get "Linux version" from `dmesg`
DMESG_LINUX_BUILD_INFO = 'Linux version'
add_filter(DmesgLineList, DMESG_LINUX_BUILD_INFO)
DmesgLineList.keep_scan("linux_version", DMESG_LINUX_BUILD_INFO, num=1)
# Must-install packages for minimum RHEL system
MINIMUM_RHEL_PKGS = [
    # 'kernel' is checked individually (booting kernel)
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
"""Threshold of the must-install packages to identify NON-RHEL."""


def _get_release(names):
    names = names if isinstance(names, list) else [names]
    for rel in OTHER_LINUX_KEYS:
        if any(rel.lower() in name.lower() for name in names):
            return rel
    return names[-1].split()[0]


def _from_os_release(osr):
    """
    Identify RHEL by checking the `/etc/os-release`.
    """
    def _filter(name):
        """Remove falsy or items contain RHEL info"""
        if not name or any(k in name.lower() for k in RHEL_KEYS):
            return False
        return name

    if osr:
        names = list(filter(_filter, [osr.get('ID'), osr.get('NAME'),
                                      osr.get('PRETTY_NAME')]))
        if names:
            # NON-RHEL: /etc/os-release
            return dict(other_linux=_get_release(names),
                        reason='NON-RHEL: os-release')
        return dict(other_linux='RHEL')


def _from_redhat_release(rhr):
    """
    Identify RHEL by checking the `/etc/redhat-release`.
    """
    if rhr:
        if not rhr.is_rhel:
            return dict(other_linux=_get_release(rhr.product),
                        reason='NON-RHEL: redhat-release')
        return dict(other_linux='RHEL')


def _from_uname(uname):
    """
    Identify RHEL by checking the `uname -a`.

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
    if uname:
        kernel = uname.kernel
        ret = dict(other_linux='Unknown')
        for rel, keys in LINUX_UNAME_KEYS:
            if any(key in kernel for key in keys):
                ret.update(other_linux=rel)
                break
        if ret.get('other_linux') != 'RHEL':
            ret.update(kernel=kernel)
        return ret


def _from_dmesg(dmesg):
    """
    Identify RHEL by checking the `dmesg`.

    The `dmesg` includes a line containing the kernel build information,
    e.g. the build host and GCC version.
    If this line doesn't contain 'redhat.com' then we can assume the kernel
    wasn't built on a Red Hat machine and this should be flagged.
    """
    if dmesg and dmesg.linux_version:
        line = dmesg.linux_version[0]['raw_message']
        low_line = line.lower()
        if 'redhat.com' not in low_line:
            release = 'Unknown'
            for rel, keys in OTHER_LINUX_KEYS.items():
                if any(kw in low_line for kw in keys[0]):
                    release = rel
                    break
            return dict(other_linux=release, build_info=line)
        else:
            return dict(other_linux='RHEL')


def _from_installed_rpms(rpms, uname):
    """
    Identify RHEL by checking the `installed_rpms`.

    Two parts are included, see below:
    """
    if not rpms:
        return
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
                release = _get_release(vendor.split(sep)[0].strip())
                ret.update(other_linux=release)
        return ret
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
        >>> 'kernel' in osr.reasons.keys()
        False
        >>> 'faulty_packages' in osr.reasons.keys()
        True
        >>> 'glibc-2.28-211.el8' in osr.reasons['faulty_packages']
        True
    """
    def __init__(self, uname, dmesg, rpms, osr, rhr):

        def __identify_non_rhel(ret):
            if ret and 'other_linux' in ret:
                self._release = ret.pop('other_linux')
                self._reasons = ret
                if self._release == 'Unknown':
                    return None  # Continue to identify when unknown
                return self._release != 'RHEL'  # see OTHER_LINUX_KEYS
            return None  # Nothing to check

        self._release = 'Unknown'
        self._reasons = dict(reason='Nothing available to check')

        # 1. Check `installed_rpms` first.
        ret = _from_installed_rpms(rpms, uname)
        #    We trust the check result of `installed_rpms`: RHEL or NON-RHEL,
        #    expect for "Unknown".
        #    `None` indicates "Unknown" or `installed_rpms` is not available
        if __identify_non_rhel(ret) is None:
            # 2. Only when `installed_rpms` cannot identify it
            #    a. installed_rpms is not available
            #    b. identify result is "Unknown"
            #
            #    Check below items with order:
            #    - uname, dmesg, os_release, and redhat_release
            #    and any `False` which indicates NON-RHEL to stop.
            check_points_funcs = [
                (_from_uname, [uname]),
                (_from_dmesg, [dmesg]),
                (_from_os_release, [osr]),
                (_from_redhat_release, [rhr]),
            ]

            for chk_func, args in check_points_funcs:
                if __identify_non_rhel(chk_func(*args)):
                    break

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
        Returns True if Convert2RHEL could convert
        """
        return self._release in CONVERT2RHEL_SUPPORTED

    @property
    def release(self):
        """
        Returns the estimated release name of the running Linux.  It's RHEL or
        one key of the :const:`OTHER_LINUX_KEYS` when it's NON-RHEL.
        """
        return self._release

    @property
    def name(self):
        """
        Returns the name of the OS. Generally it's the ``NAME`` of the
        `/etc/os-release` file, or it's the same as the `release` when
        the `/etc/os-release` is not available.
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

    def __repr__(self):
        if self.is_rhel:
            return "<release: {0}, name: {1}>".format(self.release, self.name)
        return "<release: {0}, name: {1}, reasons: {2}>".format(
                self.release, self.name, self.reasons)
