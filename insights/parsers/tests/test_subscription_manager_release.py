from insights.parsers import SkipException, subscription_manager_release
from insights.parsers.subscription_manager_release import SubscriptionManagerReleaseShow
from insights.tests import context_wrap
import pytest
import doctest

INPUT_NORMAL_1 = """
Release: 7.2
""".strip()

INPUT_NORMAL_2 = """
Release: 6Server
""".strip()

INPUT_NOT_SET = """
Release not set
""".strip()

INPUT_NG_1 = """
XYC
Release not set
""".strip()

INPUT_NG_2 = """
Release: 7.x
""".strip()

INPUT_NG_3 = """
Release: 7.x DUMMY
""".strip()

INPUT_NG_4 = """
Release: 7x
""".strip()


def test_subscription_manager_release_show_ok():
    ret = SubscriptionManagerReleaseShow(context_wrap(INPUT_NORMAL_1))
    assert ret.set == '7.2'
    assert ret.major == 7
    assert ret.minor == 2

    ret = SubscriptionManagerReleaseShow(context_wrap(INPUT_NORMAL_2))
    assert ret.set == '6Server'
    assert ret.major == 6
    assert ret.minor is None


def test_subscription_manager_release_show_not_set():
    ret = SubscriptionManagerReleaseShow(context_wrap(INPUT_NOT_SET))
    assert ret.set is None
    assert ret.major is None
    assert ret.minor is None


def test_subscription_manager_release_show_ng():
    with pytest.raises(SkipException) as e_info:
        SubscriptionManagerReleaseShow(context_wrap(INPUT_NG_1))
    assert "Content takes at most 1 line (2 given)." in str(e_info.value)

    with pytest.raises(SkipException) as e_info:
        SubscriptionManagerReleaseShow(context_wrap(INPUT_NG_2))
    assert "Incorrect content: Release: 7.x" in str(e_info.value)

    with pytest.raises(SkipException) as e_info:
        SubscriptionManagerReleaseShow(context_wrap(INPUT_NG_3))
    assert "Incorrect content: Release: 7.x DUMMY" in str(e_info.value)

    with pytest.raises(SkipException) as e_info:
        SubscriptionManagerReleaseShow(context_wrap(INPUT_NG_4))
    assert "Incorrect content: Release: 7x" in str(e_info.value)


def test_doc_examples():
    env = {
            'rhsm_rel':
            SubscriptionManagerReleaseShow(context_wrap(INPUT_NORMAL_1)),
          }
    failed, total = doctest.testmod(subscription_manager_release, globs=env)
    assert failed == 0
