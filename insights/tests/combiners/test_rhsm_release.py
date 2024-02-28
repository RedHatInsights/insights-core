import doctest

import insights.combiners.rhsm_release as rhsm_release_module
from insights.combiners.rhsm_release import RhsmRelease
from insights.parsers.rhsm_releasever import RhsmReleaseVer
from insights.parsers.subscription_manager_release import SubscriptionManagerReleaseShow
from insights.parsers.rhui_release import RHUIReleaseVer
from insights.tests import context_wrap

RHSM_RELEASE = """
{"releaseVer": "7.6"}
""".strip()

RHSM_RELEASE_EMPTY = """
{"releaseVer": null}
""".strip()

SUBSCRIPTION_MANAGER_RELEASE = """
Release: 7.2
""".strip()

EMPTY_SUBSCRIPTION_MANAGER_RELEASE = """Release not set"""

RHUI_RELEASE = """8.6"""

RHUI_EMPTY_RELEASE = ""

SM_PARSER = SubscriptionManagerReleaseShow(context_wrap(SUBSCRIPTION_MANAGER_RELEASE))
RHSM_PARSER = RhsmReleaseVer(context_wrap(RHSM_RELEASE))
RHSM_EMPTY_PARSER = RhsmReleaseVer(context_wrap(RHSM_RELEASE_EMPTY))
SM_EMPTY_PARSER = SubscriptionManagerReleaseShow(context_wrap(EMPTY_SUBSCRIPTION_MANAGER_RELEASE))
RHUI_PARSER = RHUIReleaseVer(context_wrap(RHUI_RELEASE))
RHUI_EMPTY_PARSER = RHUIReleaseVer(context_wrap(RHUI_EMPTY_RELEASE))


def test_with_rhsm():
    rhsm_release = RhsmRelease(RHSM_PARSER, None, None)
    assert rhsm_release.set == '7.6'
    assert rhsm_release.major == 7
    assert rhsm_release.minor == 6


def test_with_sub_mgr():
    rhsm_release = RhsmRelease(None, SM_PARSER, None)
    assert rhsm_release.set == '7.2'
    assert rhsm_release.major == 7
    assert rhsm_release.minor == 2


def test_with_rhui_release():
    rhsm_release = RhsmRelease(None, None, RHUI_PARSER)
    assert rhsm_release.set == '8.6'
    assert rhsm_release.major == 8
    assert rhsm_release.minor == 6


def test_with_both():
    rhsm_release = RhsmRelease(RHSM_PARSER, SM_PARSER, None)
    assert rhsm_release.set == '7.6'
    assert rhsm_release.major == 7
    assert rhsm_release.minor == 6


def test_with_three():
    rhsm_release = RhsmRelease(RHSM_PARSER, SM_PARSER, RHUI_PARSER)
    assert rhsm_release.set == '7.6'
    assert rhsm_release.major == 7
    assert rhsm_release.minor == 6


def test_with_three_but_rhsm_is_empty():
    rhsm_release = RhsmRelease(RHSM_EMPTY_PARSER, SM_EMPTY_PARSER, RHUI_PARSER)
    assert rhsm_release.set == '8.6'
    assert rhsm_release.major == 8
    assert rhsm_release.minor == 6


def test_all_empty():
    rhsm_release = RhsmRelease(RHSM_EMPTY_PARSER, SM_EMPTY_PARSER, RHUI_EMPTY_PARSER)
    assert rhsm_release.set is None
    assert rhsm_release.major is None
    assert rhsm_release.minor is None

    rhsm_release = RhsmRelease(RHSM_EMPTY_PARSER, SM_EMPTY_PARSER, None)
    assert rhsm_release.set is None
    assert rhsm_release.major is None
    assert rhsm_release.minor is None


def test_doc_examples():
    env = {
        'rhsm_release': RhsmRelease(RHSM_PARSER, None, None),
    }
    failed, total = doctest.testmod(rhsm_release_module, globs=env)
    assert failed == 0
