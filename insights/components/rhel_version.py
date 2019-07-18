"""
IsRhel6, IsRhel7 and IsRhel8
===============================

An ``IsRhel*`` component is valid if the
:py:class:`insights.combiners.redhat_release.RedHatRelease` combiner indicates
the major RHEL version represented by the component. Otherwise, it raises a
:py:class:`insights.core.dr.SkipComponent` to prevent dependent components from
executing.

In particular, an ``IsRhel*`` component can be added as a dependency of a
parser to limit it to a given version.
"""

from insights.core.plugins import component
from insights.combiners.redhat_release import RedHatRelease
from insights.core.dr import SkipComponent


@component(RedHatRelease)
class IsRhel6(object):
    """
    This component uses ``RedHatRelease`` combiner
    to determine RHEL version. It checks if RHEL6, if not
    RHEL6 it raises ``SkipComponent``.

    Raises:
        SkipComponent: When RHEL version is not RHEL6.
    """
    def __init__(self, rhel):
        if rhel.major != 6:
            raise SkipComponent('Not RHEL6')


@component(RedHatRelease)
class IsRhel7(object):
    """
    This component uses ``RedHatRelease`` combiner
    to determine RHEL version. It checks if RHEL7, if not \
    RHEL7 it raises ``SkipComponent``.

    Raises:
        SkipComponent: When RHEL version is not RHEL7.
    """
    def __init__(self, rhel):
        if rhel.major != 7:
            raise SkipComponent('Not RHEL7')


@component(RedHatRelease)
class IsRhel8(object):
    """
    This component uses ``RedhatRelease`` combiner
    to determine RHEL version. It checks if RHEL8, if not
    RHEL8 it raises ``SkipComponent``.

    Raises:
        SkipComponent: When RHEL version is not RHEL8.
    """
    def __init__(self, rhel):
        if rhel.major != 8:
            raise SkipComponent('Not RHEL8')
