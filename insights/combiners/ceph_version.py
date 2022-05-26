"""
Ceph Version
============

Combiner for Ceph Version information. It uses the results of
the ``CephVersion``, ``CephInsights`` and ``CephReport`` parsers.
The order from most preferred to least preferred is `CephVersion``, ``CephInsights``, ``CephReport``.

"""

from insights import combiner
from insights.parsers.ceph_version import (CephVersion as CephV,
        get_community_version, get_ceph_version)
from insights.parsers.ceph_insights import CephInsights
from insights.parsers.ceph_cmd_json_parsing import CephReport


@combiner([CephV, CephInsights, CephReport])
class CephVersion(object):
    """
    Combiner for Ceph Version information. It uses the results of
    the ``CephVersion``, ``CephInsights`` and ``CephReport`` parsers.

    The prefered parsing order is `CephVersion``, ``CephInsights``, ``CephReport``.

    Attributes:
        version (str): The Red Hat release version
        major (str): The major version of Red Hat release version
        minor (str): The minor version of Red Hat release version
        is_els (boolean): If the verion in 'Extended life cycle support (ELS) add-on' phase
        downstream_release (str): The downstream release info
        upstream_version (dict): The detailed upstream version info with the
            following keys `release (int)`, `major (int)` and `minor (int)`.

    Examples:
        >>> type(cv)
        <class 'insights.combiners.ceph_version.CephVersion'>
        >>> cv.version
        '3.2'
        >>> cv.major
        '3'
        >>> cv.minor
        '2'
        >>> cv.is_els
        False
        >>> cv.downstream_release
        '0'
        >>> cv.upstream_version["release"]
        12
        >>> cv.upstream_version["major"]
        2
        >>> cv.upstream_version["minor"]
        8
    """

    def __init__(self, cv, ci, cr):
        if cv:
            self.version = cv.version
            self.major = cv.major
            self.minor = cv.minor
            self.is_els = cv.is_els
            self.downstream_release = cv.downstream_release
            self.upstream_version = cv.upstream_version
        elif ci:
            community_full = get_community_version(ci.data["version"]["full"].strip())
            cv = get_ceph_version(community_full)
            self.version = cv.get('version')
            self.major = cv.get('major')
            self.minor = cv.get('minor')
            self.is_els = cv.get('els', False)
            self.downstream_release = cv.get('downstream_release')
            self.upstream_version = cv.get('upstream_version')
        else:
            cv = get_ceph_version(cr["version"].strip())
            self.version = cv.get('version')
            self.major = cv.get('major')
            self.minor = cv.get('minor')
            self.is_els = cv.get('els', False)
            self.downstream_release = cv.get('downstream_release')
            self.upstream_version = cv.get('upstream_version')
