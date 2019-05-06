"""
Is_Rhel6, Is_Rhel7 and Is_Rhel8
===============================

The ``Is_Rhel*`` components each use the ``RedhatRelease`` parser to
retrieve the RHEL version information from file ``/etc/redhat_release``.
Each component checks if the release version matches the version it represents,
and if so returns the full version. If the version does not match what
is expected the class raises ``SkipComponent`` so that the dependent
component will not fire.
Can be added as a dependency of a parser so that the parser only fires if the
``Is_Rhel*`` dependency is met.

An example from the following ``/etc/redhat_release`` file output::

    Red Hat Enterprise Linux release 8.0 (Ootpa)

Example:

    >>> type(Is_Rhel8)
    <class 'insights.components.rhel_version.Is_Rhel8'>
    >>> is_rhel8.rhel_version
    '8.0'
"""

from insights.core.plugins import component
from insights.parsers.redhat_release import RedhatRelease
from insights.core.dr import SkipComponent


@component(RedhatRelease)
class Is_Rhel6(object):
    """
    This component uses ``RedhatRelease`` parsers version information
    to determine RHEL version. It checks if RHEL6, if so
    it assigns the ``rhel_version`` attribute the value in the
    ``version`` attrubute in RedhatRelease``. If not RHEL6
    it raises ``SkipComponent``.

    Attributes:
        rhel_version (string): Version number returned in the ``version``
            attribute of the ``RedhatRelease`` parser.

    Raises:
        SkipComponent: When RHEL version is not RHEL6.
    """
    def __init__(self, rhel):
        if rhel.major == 6:
            self.rhel_version = rhel.version
        else:
            raise SkipComponent('Not RHEL6')


@component(RedhatRelease)
class Is_Rhel7(object):
    """
    This component uses ``RedhatRelease`` parsers version information
    to determine RHEL version. It checks if RHEL7, if so
    it assigns the ``rhel_version`` attribute the value in the
    ``version`` attrubute in RedhatRelease``. If not RHE:7
    it raises ``SkipComponent``.

    Attributes:
        rhel_version (string): Version number returned in the ``version``
            attribute of the ``RedhatRelease`` parser.
    Raises:
        SkipComponent: When RHEL version is not RHEL7.
    """
    def __init__(self, rhel):
        if rhel.major == 7:
            self.rhel_version = rhel.version
        else:
            raise SkipComponent('Not RHEL7')


@component(RedhatRelease)
class Is_Rhel8(object):
    """
    This component uses ``RedhatRelease`` parsers version information
    to determine RHEL version. It checks if RHEL8, if so
    it assigns the ``rhel_version`` attribute the value in the
    ``version`` attrubute in RedhatRelease``. If not RHEL8
    it raises ``SkipComponent``.

    Attributes:
        rhel_version (string): Version number returned in the ``version``
            attribute of the ``RedhatRelease`` parser.
    Raises:
        SkipComponent: When RHEL version is not RHEL7.
    """
    def __init__(self, rhel):
        if rhel.major == 8:
            self.rhel_version = rhel.version
        else:
            raise SkipComponent('Not RHEL8')
