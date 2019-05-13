"""
IsRhel6, IsRhel7 and IsRhel8
===============================

The ``IsRhel*`` components each use the ``RedhatRelease`` combiner to
retrieve the RHEL version information.
Each component checks if the release version matches the version it represents,
if the version does not match what is expected the class raises ``SkipComponent``
so that the dependent component will not fire.
Can be added as a dependency of a parser so that the parser only fires if the
``IsRhel*`` dependency is met.

An example from the following ``/etc/redhat_release`` file output::

    Red Hat Enterprise Linux release 8.0 (Ootpa)

Example:

    >>> type(IsRhel8)
    <class 'insights.components.rhel_version.Is_Rhel8'>
    >>> is_rhel8.rhel_version
    '8.0'
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
