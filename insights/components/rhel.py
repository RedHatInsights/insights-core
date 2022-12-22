"""
RHEL
====

The ``RHEL`` component provides an attribute `is_rhel` that indicates if the
host is an "Red Hat Enterprise Linux" or not.
"""
from insights.core.plugins import component
from insights.parsers.installed_rpms import InstalledRpm, InstalledRpms
from insights.parsers.subscription_manager import SubscriptionManagerID
from insights.parsers.uname import Uname


@component(optional=[Uname, SubscriptionManagerID, InstalledRpms])
class RHEL(object):
    """
    This component can be used to identify if the host an RHEL host by
    checking the following parsers:

        - :py:class:`insights.parsers.uname.Uname`
        - :py:class:`insights.parsers.subscription_manager.SubscriptionManagerID`
        - :py:class:`insights.parsers.installed_rpms.InstalledRpms`

    If none of the 3 parsers is available, NON-RHEL will be returned.

    Attributes:
        is_rhel (bool): True if it's RHEL, False for NON-RHEL.
    """
    def __init__(self, uname, rhsm_id, rpms, version=None):
        self.is_rhel = False
        if rhsm_id:
            # It is registered with RHSM; Or
            self.is_rhel = True
        elif uname and rpms:
            # Its booting kernel is signed by Red Hat
            boot_kn = InstalledRpm.from_package('kernel-{}'.format(uname.kernel))
            for pkg in rpms.packages['kernel']:
                if (pkg == boot_kn and
                        pkg.redhat_signed and
                        pkg.vendor and "Red Hat" in pkg.vendor):
                    self.is_rhel = True
