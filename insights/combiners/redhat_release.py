"""
Red Hat Release
===============

Combiner for Red Hat Release information. It uses the results of
the ``Uname`` parser and the ``rht_release`` parser to determine the release
major and minor version.  ``Uname`` is the preferred source of data. The Red
Hat Release is in obtained from the system in the form major.minor.  For
example for a Red Hat Enterprise Linux 7.2 system, the release would be
major = 7 and minor = 2.  The returned values are in integer format.Re

Examples:
    >>> rh_release = shared[redhat_release]
    >>> rh_release.major
    7
    >>> rh_release.minor
    2
    >>> rh_release
    Release(major=7, minor=2)

"""

from collections import namedtuple
from insights.core.plugins import combiner
from insights.parsers.redhat_release import RedhatRelease as rht_release
from insights.parsers.uname import Uname
from insights.core.serde import deserializer, serializer

Release = namedtuple("Release", field_names=["major", "minor"])
"""namedtuple: Type for storing the release information."""


@serializer(Release)
def serialize(obj):
    return {"major": obj.major, "minor": obj.minor}


@deserializer(Release)
def deserialize(_type, obj):
    return Release(**obj)


@combiner([rht_release, Uname])
def redhat_release(rh_release, un):
    """Check uname and redhat-release for rhel major/minor version.

    Prefer uname to redhat-release.

    Returns:
        Release: A named tuple with `major` and `minor` version
        components.

    Raises:
        Exeption: If the version can't be determined even though a Uname
            or RedhatRelease was provided.
    """

    if un and un.release_tuple[0] != -1:
        return Release(*un.release_tuple)

    if rh_release:
        return Release(rh_release.major, rh_release.minor)

    raise Exception("Unabled to determine release.")
