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

from insights.core.exceptions import SkipComponent
from insights.core.plugins import combiner
from insights.core.serde import deserializer, serializer
from insights.parsers.redhat_release import RedhatRelease as rht_release
from insights.parsers.uname import Uname


Release = namedtuple("Release", field_names=["major", "minor"])
"""namedtuple: Type for storing the release information."""


@serializer(Release)
def serialize(obj, root=None):
    return {"major": obj.major, "minor": obj.minor}


@deserializer(Release)
def deserialize(_type, obj, root=None):
    return Release(**obj)


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
        rhel9 (str): The RHEL version when it's RHEL9, otherwise None

    Raises:
        SkipComponent: If the version can't be determined even though a Uname
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
        self.major = self.minor = self.rhel = None
        if uname and uname.redhat_release.major != -1:
            self.major = uname.redhat_release.major
            self.minor = uname.redhat_release.minor
            self.rhel = '{0}.{1}'.format(self.major, self.minor)
        elif rh_rel and rh_rel.is_rhel:
            self.major = rh_rel.major
            self.minor = rh_rel.minor
            self.rhel = rh_rel.version

        if self.rhel is None:
            raise SkipComponent("Unable to determine release.")

        self.rhel6 = self.rhel if self.major == 6 else None
        self.rhel7 = self.rhel if self.major == 7 else None
        self.rhel8 = self.rhel if self.major == 8 else None
        self.rhel9 = self.rhel if self.major == 9 else None


@serializer(RedHatRelease)
def serialize_RedHatRelease(obj, root=None):
    return {
            "major": obj.major,
            "minor": obj.minor,
            "rhel": obj.rhel,
            "rhel6": obj.rhel6,
            "rhel7": obj.rhel7,
            "rhel8": obj.rhel8,
            "rhel9": obj.rhel9,
    }


@deserializer(RedHatRelease)
def deserialize_RedHatRelease(_type, obj, root=None):
    foo = _type.__new__(_type)
    foo.major = obj.get("major")
    foo.minor = obj.get("minor")
    foo.rhel = obj.get("rhel")
    foo.rhel6 = obj.get("rhel6")
    foo.rhel7 = obj.get("rhel7")
    foo.rhel8 = obj.get("rhel8")
    foo.rhel9 = obj.get("rhel9")
    return foo
