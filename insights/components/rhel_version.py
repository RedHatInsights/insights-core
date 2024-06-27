"""
IsRhel - components to check RHEL version
=========================================

``IsRhel#``,  ``IsGtRhel#``, ``IsGtOrRhel#`` component are included in this
module.

The component is valid if the RHEL version got from the
:py:class:`insights.combiners.redhat_release.RedHatRelease` of the current
host satisfies the requirements.  Otherwise, it raises a
:py:class:`insights.core.exceptions.SkipComponent` to prevent dependent
components from triggering.

In particular, the component can be added as a dependency of another
components, e.g. Specs or Parsers parser to limit it to a given version.
"""
from insights.combiners.redhat_release import RedHatRelease
from insights.core.exceptions import SkipComponent
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
    def __init__(self, rhel, major=None):
        if rhel.major != major:
            raise SkipComponent("Not RHEL {0}".format(major))
        self.minor = rhel.minor


class IsGtRhel(object):
    """
    This component uses ``RedHatRelease`` combiner to determine the RHEL
    version. It then checks if the major version matches the version argument,
    if it doesn't it raises ``SkipComponent``.

    When `equal` is set to True, it checks "greater than or equal".  Otherwise,
    it only checks "greater than".

    Attributes:
        major (int): The major version of RHEL.
        minor (int): The minor version of RHEL.

    Raises:
        SkipComponent: When RHEL version does not match the specified version.
    """
    def __init__(self, rhel, major, minor, equal=False):
        if rhel.major < major:
            raise SkipComponent("Not RHEL newer than {0}.{1}".format(major, minor))
        if equal:
            if rhel.major == major and rhel.minor < minor:
                raise SkipComponent("Not RHEL newer than or equal {0}.{1}".format(major, minor))
        else:
            if rhel.major == major and rhel.minor <= minor:
                raise SkipComponent("Not RHEL newer than {0}.{1}".format(major, minor))
        self.major = rhel.major
        self.minor = rhel.minor


@component(RedHatRelease)
class IsRhel6(IsRhel):
    """
    This component checks if it's RHEL 6.

    Attributes:
        minor (int): The minor version of RHEL 6.

    Raises:
        SkipComponent: When RHEL version is not RHEL 6.
    """
    def __init__(self, rhel):
        super(IsRhel6, self).__init__(rhel, 6)


@component(RedHatRelease)
class IsRhel7(IsRhel):
    """
    This component checks if it's RHEL 7.

    Attributes:
        minor (int): The minor version of RHEL 7.

    Raises:
        SkipComponent: When RHEL version is not RHEL 7.
    """
    def __init__(self, rhel):
        super(IsRhel7, self).__init__(rhel, 7)


@component(RedHatRelease)
class IsRhel8(IsRhel):
    """
    This component checks if it's RHEL 8.

    Attributes:
        minor (int): The minor version of RHEL 8.

    Raises:
        SkipComponent: When RHEL version is not RHEL 8.
    """
    def __init__(self, rhel):
        super(IsRhel8, self).__init__(rhel, 8)


@component(RedHatRelease)
class IsRhel9(IsRhel):
    """
    This component checks if it's RHEL 9.

    Attributes:
        minor (int): The minor version of RHEL 9.

    Raises:
        SkipComponent: When RHEL version is not RHEL 9.
    """
    def __init__(self, rhel):
        super(IsRhel9, self).__init__(rhel, 9)


@component(RedHatRelease)
class IsGtOrRhel86(IsGtRhel):
    """
    This component checks if the RHEL version is 8.6 or grater than 8.6.

    Attributes:
        major (int): The major version of RHEL.
        minor (int): The minor version of RHEL.

    Raises:
        SkipComponent: When RHEL version is not 8.6 and less than 8.6
    """
    def __init__(self, rhel):
        super(IsGtOrRhel86, self).__init__(rhel, 8, 6, equal=True)


@component(RedHatRelease)
class IsGtRhel86(IsGtRhel):
    """
    This component checks if the RHEL version is grater than 8.6.

    Attributes:
        major (int): The major version of RHEL.
        minor (int): The minor version of RHEL.

    Raises:
        SkipComponent: When RHEL version is 8.6 or less than 8.6
    """
    def __init__(self, rhel):
        super(IsGtRhel86, self).__init__(rhel, 8, 6, equal=False)
