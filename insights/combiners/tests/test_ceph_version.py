from insights.parsers.ceph_version import CephVersion as CephV
from insights.parsers.ceph_insights import CephInsights
from insights.combiners import ceph_version
from insights.combiners.ceph_version import CephVersion
from insights.tests import context_wrap
import doctest

CEPH_INSIGHTS = """
{
  "version": {
    "release": 12,
    "major": 2,
    "full": "ceph version 12.2.8-52.el7cp (3af3ca15b68572a357593c261f95038d02f46201) luminous (stable)",
    "minor": 8
  }
}
""".strip()

CEPH_VERSION = "ceph version 12.2.8-52.el7cp (3af3ca15b68572a357593c261f95038d02f46201) luminous (stable)".strip()


def test_ceph_version():
    cv = CephV(context_wrap(CEPH_VERSION))
    ret = CephVersion(cv, None)
    assert ret.version == "3.2"
    assert ret.major == "3"
    assert ret.minor == "2"
    assert ret.downstream_release == "0"
    assert ret.upstream_version["release"] == 12
    assert ret.upstream_version["major"] == 2
    assert ret.upstream_version["minor"] == 8


def test_ceph_version_2():
    cv = CephV(context_wrap(CEPH_VERSION))
    ci = CephInsights(context_wrap(CEPH_INSIGHTS))
    ret = CephVersion(cv, ci)
    assert ret.version == "3.2"
    assert ret.major == "3"
    assert ret.minor == "2"
    assert ret.downstream_release == "0"
    assert ret.upstream_version["release"] == 12
    assert ret.upstream_version["major"] == 2
    assert ret.upstream_version["minor"] == 8


def test_ceph_insights():
    ci = CephInsights(context_wrap(CEPH_INSIGHTS))
    ret = CephVersion(None, ci)
    assert ret.version == "3.2"
    assert ret.major == "3"
    assert ret.minor == "2"
    assert ret.downstream_release == "0"
    assert ret.upstream_version["release"] == 12
    assert ret.upstream_version["major"] == 2
    assert ret.upstream_version["minor"] == 8


def test_ceph_version_doc_examples():
    env = {
        'cv': CephVersion(CephV(context_wrap(CEPH_VERSION)), None)
    }
    failed, total = doctest.testmod(ceph_version, globs=env)
    assert failed == 0
