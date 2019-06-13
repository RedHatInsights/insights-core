"""
Ceph Version
============

Combiner for Ceph Version information. It uses the results of
the ``CephVersion``, ``CephInsights`` and ``CephReport`` parsers.
The order from most preferred to least preferred is `CephVersion``, ``CephInsights``, ``CephReport``.

Examples:
    >>> type(cv)
    <class 'insights.combiners.ceph_version.CephVersion'>
    >>> cv.version
    '3.2'
    >>> cv.major
    '3'
    >>> cv.minor
    '2'
    >>> cv.downstream_release
    '0'
    >>> cv.upstream_version["release"]
    12
    >>> cv.upstream_version["major"]
    2
    >>> cv.upstream_version["minor"]
    8
"""

from insights import combiner
from insights.parsers.ceph_version import CephVersion as CephV
from insights.parsers.ceph_insights import CephInsights
from insights.parsers.ceph_cmd_json_parsing import CephReport
from insights.core.context import Context


@combiner([CephV, CephInsights, CephReport])
class CephVersion(object):
    """
    Combiner for Ceph Version information. It uses the results of
    the ``CephVersion``, ``CephInsights`` and ``CephReport`` parsers.
    The order from most preferred to least preferred is `CephVersion``, ``CephInsights``, ``CephReport``.
    """

    def __init__(self, cv, ci, cr):
        if cv:
            self.version = cv.version
            self.major = cv.major
            self.minor = cv.minor
            self.downstream_release = cv.downstream_release
            self.upstream_version = cv.upstream_version
        elif ci:
            context = Context(content=ci.data["version"]["full"].strip().splitlines())
            cv = CephV(context)
            self.version = cv.version
            self.major = cv.major
            self.minor = cv.minor
            self.downstream_release = cv.downstream_release
            self.upstream_version = cv.upstream_version
        else:
            context = Context(content=cr["version"].strip().splitlines())
            cv = CephV(context)
            self.version = cv.version
            self.major = cv.major
            self.minor = cv.minor
            self.downstream_release = cv.downstream_release
            self.upstream_version = cv.upstream_version
