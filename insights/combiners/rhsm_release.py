"""
Red Hat Subscription Manager Release
====================================

Combiner provides the Red Hat Subscription Manager release information from
the parsers :class:`insights.parsers.rhsm_releasever.RhsmReleaseVer`
and :class:`insights.parsers.subscription_manager_release.SubscriptionManagerReleaseShow`
and :class:`insights.parsers.rhui_release.RHUIReleaseVer`.
"""
from insights.core.plugins import combiner
from insights.parsers.rhsm_releasever import RhsmReleaseVer
from insights.parsers.subscription_manager_release import SubscriptionManagerReleaseShow
from insights.parsers.rhui_release import RHUIReleaseVer


@combiner([RhsmReleaseVer, SubscriptionManagerReleaseShow, RHUIReleaseVer])
class RhsmRelease(object):
    """
    Combiner for parsers RhsmReleaseVer and SubscriptionManagerReleaseShow and RHUIReleaseVer.

    Examples:
        >>> type(rhsm_release)
        <class 'insights.combiners.rhsm_release.RhsmRelease'>
        >>> rhsm_release.set == '7.6'
        True
        >>> rhsm_release.major
        7
        >>> rhsm_release.minor
        6
    """
    def __init__(self, rhsm_release, sm_release, rhui_release):
        self.set = None
        """ str: Release version string returned from the parsers """

        self.major = None
        """ int: Major version of the release """

        self.minor = None
        """ int: Minor version of the release """
        if rhsm_release is not None and rhsm_release.set:
            self.set = rhsm_release.set
            self.major = rhsm_release.major
            self.minor = rhsm_release.minor

        elif sm_release is not None and sm_release.set:
            self.set = sm_release.set
            self.major = sm_release.major
            self.minor = sm_release.minor
        elif rhui_release is not None and rhui_release.set:
            self.set = rhui_release.set
            self.major = rhui_release.major
            self.minor = rhui_release.minor
