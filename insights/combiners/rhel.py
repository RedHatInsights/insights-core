"""
RHEL
====

The ``RHEL`` combiner provides an attribute `is_rhel` that indicates if the
host is an "Red Hat Enterprise Linux" or not.
"""
from insights.core.plugins import combiner
from insights.parsers.installed_rpms import InstalledRpm, InstalledRpms
from insights.parsers.os_release import OsRelease
from insights.parsers.redhat_release import RedhatRelease
from insights.parsers.uname import Uname


@combiner(optional=[Uname, InstalledRpms, RedhatRelease, OsRelease])
class RHEL(object):
    """
    This combiner can be used to identify if the host an RHEL host by
    checking the following parsers:

        - :py:class:`insights.parsers.uname.Uname`
        - :py:class:`insights.parsers.os_release.OsRelease`
        - :py:class:`insights.parsers.redhat_release.RedhatRelease`
        - :py:class:`insights.parsers.installed_rpms.InstalledRpms`

    If none of the above parsers is available, NON-RHEL will be returned.

    Attributes:
        is_rhel (bool): True if it's RHEL, False for NON-RHEL.
    """
    def __init__(self, uname, rpms, rhr, osr):
        self.is_rhel = False
        if all(arg is None for arg in [uname, rpms, rhr, osr]):
            return
        if rpms:
            boot_kn = InstalledRpm.from_package('kernel-{0}'.format(uname.kernel)) if uname else None
            flag = False
            for pkg in rpms.packages['kernel']:
                if pkg == boot_kn:
                    # check the booting kernel when Uname is available
                    if not (pkg.redhat_signed and pkg.vendor and
                            "Red Hat" in pkg.vendor):
                        flag = True
                    break
            pkg = rpms.newest('systemd')
            if flag and pkg and not (pkg.redhat_signed and pkg.vendor and
                                     "Red Hat" in pkg.vendor):
                # NON-RHEL: BOTH booting kernel and systemd are NOT siged by Red Hat
                return
        if uname and uname.redhat_release.major == -1:
            # NON-RHEL: unknown uname
            # - https://access.redhat.com/articles/3078
            return
        if rhr and rhr.is_rhel is False:
            # NON-RHEL: /etc/redhat-release doesn't contain "Red Hat Enterprise Linux"
            return
        if (osr and
                not (osr.get('ID') == "rhel" and
                     osr.get('NAME', '').startswith('Red Hat Enterprise Linux'))):
            # NON-RHEL: /etc/os-release doesn't contain "Red Hat Enterprise Linux"
            return
        # It's RHEL
        self.is_rhel = True
