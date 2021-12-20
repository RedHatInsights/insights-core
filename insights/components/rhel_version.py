"""
IsRhel6, IsRhel7, IsRhel8, and IsRhel9
======================================

An ``IsRhel*`` component is valid if the
:py:class:`insights.combiners.redhat_release.RedHatRelease` combiner indicates
the major RHEL version represented by the component. Otherwise, it raises a
:py:class:`insights.core.dr.SkipComponent` to prevent dependent components from
executing.

In particular, an ``IsRhel*`` component can be added as a dependency of a
parser to limit it to a given version.
"""
from insights.combiners.redhat_release import RedHatRelease
from insights.core.dr import SkipComponent
from insights.core.plugins import component


class IsRhel(object):
    """
    This component uses ``RedHatRelease`` combiner to determine the RHEL
    major version. It then checks if the major version matches the version
    argument, if it doesn't it raises ``SkipComponent``.

    Attributes:
        minor (int): The minor version of RHEL.

    Raises:
        SkipComponent: When RHEL major version does not match version.
    """
    def __init__(self, rhel, version=None):
        if rhel.major != version:
            raise SkipComponent("Not RHEL{vers}".format(vers=version))
        self.minor = rhel.minor


@component(RedHatRelease)
class IsRhel6(IsRhel):
    """
    This component uses ``RedHatRelease`` combiner
    to determine RHEL version. It checks if RHEL6, if not
    RHEL6 it raises ``SkipComponent``.

    Attributes:
        minor (int): The minor version of RHEL 6.

    Raises:
        SkipComponent: When RHEL version is not RHEL6.
    """
    def __init__(self, rhel):
        super(IsRhel6, self).__init__(rhel, 6)


@component(RedHatRelease)
class IsRhel7(IsRhel):
    """
    This component uses ``RedHatRelease`` combiner
    to determine RHEL version. It checks if RHEL7, if not
    RHEL7 it raises ``SkipComponent``.

    Attributes:
        minor (int): The minor version of RHEL 7.

    Raises:
        SkipComponent: When RHEL version is not RHEL7.
    """
    def __init__(self, rhel):
        super(IsRhel7, self).__init__(rhel, 7)


@component(RedHatRelease)
class IsRhel8(IsRhel):
    """
    This component uses ``RedhatRelease`` combiner
    to determine RHEL version. It checks if RHEL8, if not
    RHEL8 it raises ``SkipComponent``.

    Attributes:
        minor (int): The minor version of RHEL 8.

    Raises:
        SkipComponent: When RHEL version is not RHEL8.
    """
    def __init__(self, rhel):
        super(IsRhel8, self).__init__(rhel, 8)


@component(RedHatRelease)
class IsRhel9(IsRhel):
    """
    This component uses ``RedhatRelease`` combiner
    to determine RHEL version. It checks if RHEL9, if not
    RHEL9 it raises ``SkipComponent``.

    Attributes:
        minor (int): The minor version of RHEL 9.

    Raises:
        SkipComponent: When RHEL version is not RHEL9.
    """
    def __init__(self, rhel):
        super(IsRhel9, self).__init__(rhel, 9)
