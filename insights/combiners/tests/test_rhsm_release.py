import doctest

import insights.combiners.rhsm_release as rhsm_release_module
from insights.combiners.rhsm_release import RhsmRelease
from insights.parsers.rhsm_releasever import RhsmReleaseVer
from insights.parsers.subscription_manager_release import SubscriptionManagerReleaseShow
from insights.tests import context_wrap

RHSM_RELEASE = """
{"releaseVer": "7.6"}
""".strip()

SUBSCRIPTION_MANAGER_RELEASE = """
Release: 7.2
""".strip()

SM_PARSER = SubscriptionManagerReleaseShow(context_wrap(SUBSCRIPTION_MANAGER_RELEASE))
RHSM_PARSER = RhsmReleaseVer(context_wrap(RHSM_RELEASE))


def test_with_rhsm():
    rhsm_release = RhsmRelease(RHSM_PARSER, None)
    assert rhsm_release.set == '7.6'
    assert rhsm_release.major == 7
    assert rhsm_release.minor == 6


def test_with_sub_mgr():
    rhsm_release = RhsmRelease(None, SM_PARSER)
    assert rhsm_release.set == '7.2'
    assert rhsm_release.major == 7
    assert rhsm_release.minor == 2


def test_with_both():
    rhsm_release = RhsmRelease(RHSM_PARSER, SM_PARSER)
    assert rhsm_release.set == '7.6'
    assert rhsm_release.major == 7
    assert rhsm_release.minor == 6


def test_doc_examples():
    env = {
        'rhsm_release': RhsmRelease(RHSM_PARSER, None),
    }
    failed, total = doctest.testmod(rhsm_release_module, globs=env)
    assert failed == 0
