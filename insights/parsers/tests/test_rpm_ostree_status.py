# -*- coding: utf-8 -*-
import doctest
from insights.parsers import rpm_ostree_status
from insights.parsers.rpm_ostree_status import RpmOstreeStatus
from insights.tests import context_wrap


GOOD = """
    {
    "deployments" : [
        {
        "base-commit-meta" : {
            "rpmostree.inputhash" : "d272136f0a700a049da30520591205fec5474125474a58a4c9a63ecc8243f227"
        },
        "requested-local-packages" : [
        ],
        "base-removals" : [
        ],
        "unlocked" : "none",
        "booted" : true,
        "initramfs-etc" : [
        ],
        "id" : "rhel-f0c0294860db563e5906db8c9f257d2bfebe40c93e0320b0e380b879f545e267.0",
        "osname" : "rhel",
        "origin" : "edge:rhel/8/x86_64/edge",
        "pinned" : false,
        "regenerate-initramfs" : false,
        "base-local-replacements" : [
        ],
        "checksum" : "f0c0294860db563e5906db8c9f257d2bfebe40c93e0320b0e380b879f545e267",
        "requested-base-local-replacements" : [
        ],
        "timestamp" : 1614717652,
        "requested-packages" : [
        ],
        "serial" : 0,
        "packages" : [
        ],
        "gpg-enabled" : false,
        "requested-base-removals" : [
        ]
        }
    ],
    "transaction" : null,
    "cached-update" : null
    }
""".strip()


def test_good_data():
    data = context_wrap(GOOD)
    status = RpmOstreeStatus(data)
    assert status.data["deployments"][0]["booted"]
    assert len(status.query.deployments.where("booted", True)) == 1


def test_doc_examples():
    data = context_wrap(GOOD)
    env = {
        'status': RpmOstreeStatus(data)
    }
    failed, _ = doctest.testmod(rpm_ostree_status, globs=env)
    assert failed == 0
