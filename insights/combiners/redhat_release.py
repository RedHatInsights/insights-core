"""
Red Hat Release
===============

Combiner for Red Hat Release information. It uses the results of
the ``Uname`` parser and the ``RedhatRelease`` parser to determine the release
major and minor version.  ``Uname`` is the preferred source of data.
The Red Hat Release is in obtained from the system in the form major.minor.
For example, for a Red Hat Enterprise Linux 7.2 system, the release would be
major = 7, minor = 2 and rhel = '7.2'.

"""

from collections import namedtuple
from insights.core.plugins import combiner
from insights.parsers.redhat_release import RedhatRelease as rht_release
from insights.parsers.uname import Uname
from insights.core.serde import serializer, deserializer
from insights.parsers import ParseException

Release = namedtuple("Release", field_names=["major", "minor", "rhel"])
"""namedtuple: Type for storing the release information."""


@serializer(Release)
def serialize(obj, root=None):
    return {"major": obj.major, "minor": obj.minor, "rhel": obj.rhel}


@deserializer(Release)
def deserialize(_type, obj, root=None):
    return Release(**obj)


@combiner([rht_release, Uname])
def redhat_release(rh_release, un):
    """
    Combiner method to check uname and redhat-release for rhel major/minor
    version.

    Prefer uname to redhat-release.

    Returns:
        Release: A named tuple with the following items:
            - major: integer
            - minor: integer
            - rhel: string

    Raises:
        ParseException: If the version can't be determined even though a Uname
            or RedhatRelease was provided.

    Examples:
        >>> rh_release.major
        7
        >>> rh_release.minor
        2
        >>> rh_release.rhel
        '7.2'
        >>> rh_release
        Release(major=7, minor=2, rhel='7.2')

    """

    if un and un.release_tuple[0] != -1:
        return Release(
                un.redhat_release.major,
                un.redhat_release.minor,
                '{0}.{1}'.format(un.redhat_release.major, un.redhat_release.minor))

    if rh_release:
        return Release(rh_release.major, rh_release.minor, rh_release.version)

    raise ParseException("Unabled to determine release.")


@combiner([Uname, rht_release])
class RedHatRelease(object):
    """
    Combiner class to check uname and redhat-release for RHEL major/minor
    version.
    Prefer uname to redhat-release.

    Attributes:
        major (int): The major RHEL version.
        minor (int): The minor RHEL version.
        rhel (str): The RHEL version, e.g. '7.2', '7.5-0.14'
        rhel6 (str): The RHEL version when it's RHEL6, otherwise None
        rhel7 (str): The RHEL version when it's RHEL7, otherwise None
        rhel8 (str): The RHEL version when it's RHEL8, otherwise None

    Raises:
        ParseException: If the version can't be determined even though a Uname
            or RedhatRelease was provided.

    Examples:
        >>> rh_rel.rhel
        '7.2'
        >>> rh_rel.major
        7
        >>> rh_rel.minor
        2
        >>> rh_rel.rhel6 is None
        True
        >>> rh_rel.rhel7
        '7.2'
        >>> rh_rel.rhel8 is None
        True
    """
    def __init__(self, uname, rh_rel):
        self.major = self.minor = None
        self.rhel = self.rhel6 = self.rhel7 = self.rhel8 = None
        if uname and uname.redhat_release.major != -1:
            self.major = uname.redhat_release.major
            self.minor = uname.redhat_release.minor
            self.rhel = '{0}.{1}'.format(self.major, self.minor)
        elif rh_rel and rh_rel.is_rhel:
            self.major = rh_rel.major
            self.minor = rh_rel.minor
            self.rhel = rh_rel.version

        if self.rhel is None:
            raise ParseException("Unable to determine release.")

        self.rhel6 = self.rhel if self.major == 6 else None
        self.rhel7 = self.rhel if self.major == 7 else None
        self.rhel8 = self.rhel if self.major == 8 else None
