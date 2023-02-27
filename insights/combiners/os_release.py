"""
OSRelease
=========
The ``OSRelease`` combiner uses the following parsers to try to identify if the
current host is installed with a "Red Hat Enterprise Linux" system.

    - :py:class:`insights.parsers.os_release.OsRelease`
    - :py:class:`insights.parsers.redhat_release.RedhatRelease`
    - :py:class:`insights.parsers.installed_rpms.InstalledRpms`

It provides an attribute `is_rhel` that indicates if the host is "RHEL" or not.
It also provides an attribute `product` which returns the estimated OS name of
the system, "Unknown" will be returned by default when cannot identify the OS.
"""
from insights.core.plugins import combiner
from insights.parsers.installed_rpms import InstalledRpm, InstalledRpms
from insights.parsers.os_release import OsRelease
from insights.parsers.redhat_release import RedhatRelease
from insights.parsers.uname import Uname

RHEL_STR = "Red Hat Enterprise Linux"
RHEL_KEYS = ['rhel', 'red hat enterprise linux']
"""Keywords in 'os-release' or 'redhat-release' that indicates an RHEL system."""
NON_RHEL_KEYS = ['oracle', 'suse', 'sles', 'fedora', 'centos']
"""Keywords in 'os-release' or 'redhat-release' that indicates a NON-RHEL system."""
MIN_RHEL_PKGS = [
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
    'redhat-release',
    'redhat-release-server',  # RHEL 6/7
    'systemd',  # RHEL 7+
    'util-linux',
    'yum',  # RHEL 6/7
]
"""Must-install packages for minimum installed RHEL system."""
THRESHOLD = 0.7
"""Threshold rate of the required "MIN_RHEL_PKGS" to identify RHEL system"""


@combiner(optional=[InstalledRpms, RedhatRelease, OsRelease, Uname])
class OSRelease(object):
    """
    This combiner can be used to identify if the host an RHEL host by
    checking the following parsers:

        - :py:class:`insights.parsers.os_release.OsRelease`
        - :py:class:`insights.parsers.redhat_release.RedhatRelease`
        - :py:class:`insights.parsers.installed_rpms.InstalledRpms`

    If none of the above parsers is available, NON-RHEL will be returned.

    The :py:class:`insights.parsers.uname.Uname` parser is used to get the
    booting kernel package.
    """
    def __init__(self, rpms, rhr, osr, uname):
        self._is_rhel = False
        self._product = "Unknown"
        self._ng_pkgs = set()
        if osr:
            names = list(filter(None,
                                [osr.get('ID'), osr.get('NAME'),
                                 osr.get('PRETTY_NAME')]))
            if names and any(nr in nm.lower() for nm in names
                                              for nr in NON_RHEL_KEYS):
                self._product = names[-1]
                # NON-RHEL Assertion 1: NG /etc/os-release
                return
        if rhr and any(nr in rhr.raw.lower() for nr in NON_RHEL_KEYS):
            self._product = rhr.product
            # NON-RHEL Assertion 2: NG /etc/redhat-release
            return
        if rpms and rpms.packages:
            installed_packages = 1  # kernel is must-installed
            # check the booting 'kernel' first
            boot_kn = InstalledRpm.from_package(
                    'kernel-{0}'.format(uname.kernel)) if uname else None
            if boot_kn:
                # check the booting kernel only when Uname is available
                for pkg in rpms.packages.get('kernel', []):
                    if pkg == boot_kn:
                        if not (pkg.redhat_signed and
                                pkg.vendor and pkg.vendor == 'Red Hat, Inc.'):
                            self._ng_pkgs.add(pkg.nvr)
                        break
            # check other packages
            for pkg_name in MIN_RHEL_PKGS:
                pkg = rpms.newest(pkg_name)
                if pkg:
                    installed_packages += 1  # count the package only when it's installed
                    if not (pkg.redhat_signed and
                            pkg.vendor and pkg.vendor == 'Red Hat, Inc.'):
                        self._ng_pkgs.add(pkg.nvr)
            if len(self._ng_pkgs) < round(THRESHOLD * installed_packages):
                # RHEL: less than THRESHOLD packages are NOT from Red Hat
                self._is_rhel = True
                self._product = RHEL_STR
        elif ((rhr and rhr.is_rhel) or
                (osr and names and
                 any(k in v.lower() for k in RHEL_KEYS for v in names))):
            # backup plan when "rpm" command is corrupt or blocked
            # RHEL: when `os-release` *OR* `redhat-release` are for RHEL
            self._is_rhel = True
            self._product = RHEL_STR
        # else: Unknown OS Product

    @property
    def is_rhel(self):
        """
        Returns True if it's RHEL, False for NON-RHEL.
        """
        return self._is_rhel

    @property
    def product(self):
        """
        Returns the estimated product name of this host. "Unknown" by default.
        """
        return self._product

    @property
    def issued_packages(self):
        """
        Returns the list of issued must-install packages that are not signed
        by Red Hat or not provided by Red Hat.
        """
        return sorted(self._ng_pkgs)
