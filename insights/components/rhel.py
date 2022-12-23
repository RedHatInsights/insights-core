"""
RHEL
====

The ``RHEL`` component provides an attribute `is_rhel` that indicates if the
host is an "Red Hat Enterprise Linux" or not.
"""
from insights.core.plugins import component
from insights.parsers.installed_rpms import InstalledRpm, InstalledRpms
from insights.parsers.os_release import OsRelease
from insights.parsers.redhat_release import RedhatRelease
from insights.parsers.subscription_manager import SubscriptionManagerID
from insights.parsers.uname import Uname


@component(optional=[Uname, RedhatRelease, OsRelease, SubscriptionManagerID,
                     InstalledRpms])
class RHEL(object):
    """
    This component can be used to identify if the host an RHEL host by
    checking the following parsers:

        - :py:class:`insights.parsers.uname.Uname`
        - :py:class:`insights.parsers.os_release.OsRelease`
        - :py:class:`insights.parsers.redhat_release.RedhatRelease`
        - :py:class:`insights.parsers.subscription_manager.SubscriptionManagerID`
        - :py:class:`insights.parsers.installed_rpms.InstalledRpms`

    If none of the above parsers is available, NON-RHEL will be returned.

    Attributes:
        is_rhel (bool): True if it's RHEL, False for NON-RHEL.
    """
    def __init__(self, uname, rhr, osr, rhsm_id, rpms):
        self.is_rhel = False
        if rhr and rhr.is_rhel is False:
            # /etc/redhat-release does not contain "Red Hat Enterprise Linux"
            return
        if (osr and
                not (osr.get('ID') == "rhel" and
                     osr.get('NAME', '').startswith('Red Hat Enterprise Linux'))):
            # /etc/os-release does not contain "Red Hat Enterprise Linux"
            return
        if uname and uname.redhat_release.major == -1:
            # Failed to check the booting kernel version:
            # - https://access.redhat.com/articles/3078
            return
        if rhsm_id:
            # It is registered with RHSM
            self.is_rhel = True
            return
        if rpms:
            # Its booting kernel is signed by Red Hat
            boot_kn = InstalledRpm.from_package('kernel-{}'.format(uname.kernel))
            for pkg in rpms.packages['kernel']:
                if (pkg == boot_kn and
                        pkg.redhat_signed and
                        pkg.vendor and "Red Hat" in pkg.vendor):
                    self.is_rhel = True
