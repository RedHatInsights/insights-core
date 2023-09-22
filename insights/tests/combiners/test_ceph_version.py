from insights.parsers.ceph_version import CephVersion as CephV
from insights.parsers.ceph_insights import CephInsights
from insights.parsers.ceph_cmd_json_parsing import CephReport
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

CEPH_REPORT = """
report 1188805303
{
    "cluster_fingerprint": "0d5f8f7a-0241-4a2e-8401-9dcf37a1039b",
    "version": "12.2.8-52.el7cp",
    "commit": "3af3ca15b68572a357593c261f95038d02f46201",
    "timestamp": "2019-06-05 23:33:08.514032",
    "tag": "",
    "health": {
        "checks": {
            "POOL_APP_NOT_ENABLED": {
                "severity": "HEALTH_WARN",
                "summary": {
                    "message": "application not enabled on 1 pool(s)"
                },
                "detail": [
                    {
                        "message": "application not enabled on pool 'pool-a'"
                    },
                    {
                        "message": "use 'ceph osd pool application enable <pool-name> <app-name>', where <app-name> is 'cephfs', 'rbd', 'rgw', or freeform for custom applications."
                    }
                ]
            },
            "MON_DOWN": {
                "severity": "HEALTH_WARN",
                "summary": {
                    "message": "1/3 mons down, quorum ceph2,ceph_1"
                },
                "detail": [
                    {
                        "message": "mon.ceph3 (rank 0) addr 10.72.37.76:6789/0 is down (out of quorum)"
                    }
                ]
            }
        },
        "status": "HEALTH_WARN",
        "summary": [
            {
                "severity": "HEALTH_WARN",
                "summary": "'ceph health' JSON format has changed in luminous. If you see this your monitoring system is scraping the wrong fields. Disable this with 'mon health preluminous compat warning = false'"
            }
        ],
        "overall_status": "HEALTH_WARN",
        "detail": [
            "'ceph health' JSON format has changed in luminous. If you see this your monitoring system is scraping the wrong fields. Disable this with 'mon health preluminous compat warning = false'"
        ]
    },
    "monmap_first_committed": 1,
    "monmap_last_committed": 1,
    "quorum": [
        1,
        2
    ],
    "osdmap_first_committed": 1,
    "osdmap_last_committed": 92
}
""".strip()


def test_ceph_version():
    cv = CephV(context_wrap(CEPH_VERSION))
    ret = CephVersion(cv, None, None)
    assert ret.version == "3.2"
    assert ret.major == "3"
    assert ret.minor == "2"
    assert not ret.is_els
    assert ret.downstream_release == "0"
    assert ret.upstream_version["release"] == 12
    assert ret.upstream_version["major"] == 2
    assert ret.upstream_version["minor"] == 8


def test_ceph_version_2():
    cv = CephV(context_wrap(CEPH_VERSION))
    ci = CephInsights(context_wrap(CEPH_INSIGHTS))
    ret = CephVersion(cv, ci, None)
    assert ret.version == "3.2"
    assert ret.major == "3"
    assert ret.minor == "2"
    assert not ret.is_els
    assert ret.downstream_release == "0"
    assert ret.upstream_version["release"] == 12
    assert ret.upstream_version["major"] == 2
    assert ret.upstream_version["minor"] == 8


def test_ceph_insights():
    ci = CephInsights(context_wrap(CEPH_INSIGHTS))
    ret = CephVersion(None, ci, None)
    assert ret.version == "3.2"
    assert ret.major == "3"
    assert ret.minor == "2"
    assert not ret.is_els
    assert ret.downstream_release == "0"
    assert ret.upstream_version["release"] == 12
    assert ret.upstream_version["major"] == 2
    assert ret.upstream_version["minor"] == 8


def test_ceph_report():
    cr = CephReport(context_wrap(CEPH_REPORT))
    ret = CephVersion(None, None, cr)
    assert ret.version == "3.2"
    assert ret.major == "3"
    assert ret.minor == "2"
    assert not ret.is_els
    assert ret.downstream_release == "0"
    assert ret.upstream_version["release"] == 12
    assert ret.upstream_version["major"] == 2
    assert ret.upstream_version["minor"] == 8


def test_ceph_version_doc_examples():
    env = {
        'cv': CephVersion(CephV(context_wrap(CEPH_VERSION)), None, None)
    }
    failed, total = doctest.testmod(ceph_version, globs=env)
    assert failed == 0
