import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import rhui_release
from insights.parsers.rhui_release import RHUISetRelease, RHUIReleaseVer
from insights.tests import context_wrap

INPUT_NORMAL_1 = """
8.6
""".strip()

INPUT_NORMAL_2 = """
7Server
""".strip()

INPUT_NORMAL_3 = """
8
""".strip()

INPUT_NOT_SET = """""".strip()

INPUT_NG_1 = """
XYC
Release not set
""".strip()

INPUT_NG_2 = """
abc def
""".strip()

INPUT_NG_3 = """
ab.def
""".strip()


def test_rhui_release_ok():
    ret = RHUISetRelease(context_wrap(INPUT_NORMAL_1))
    assert ret.set == '8.6'
    assert ret.major == 8
    assert ret.minor == 6


def test_rhui_release_not_set():
    ret = RHUISetRelease(context_wrap(INPUT_NOT_SET))
    assert ret.set is None
    assert ret.major is None
    assert ret.minor is None


def test_rhui_release_show_ng():
    with pytest.raises(SkipComponent) as e_info:
        RHUISetRelease(context_wrap(INPUT_NG_1))
    assert "Unexpected content" in str(e_info.value)

    with pytest.raises(SkipComponent) as e_info:
        RHUISetRelease(context_wrap(INPUT_NG_2))
    assert "Unexpected content" in str(e_info.value)


def test_rhui_minor_release():
    ret = RHUIReleaseVer(context_wrap(INPUT_NORMAL_1))
    assert ret.set == '8.6'
    assert ret.major == 8
    assert ret.minor == 6


def test_rhui_minor_release_not_set():
    ret = RHUIReleaseVer(context_wrap(INPUT_NOT_SET))
    assert ret.set is None
    assert ret.major is None
    assert ret.minor is None


def test_rhui_release_2():
    ret = RHUIReleaseVer(context_wrap(INPUT_NORMAL_2))
    assert ret.set == '7Server'
    assert ret.major == 7
    assert ret.minor is None


def test_rhui_release_3():
    ret = RHUIReleaseVer(context_wrap(INPUT_NORMAL_3))
    assert ret.set == '8'
    assert ret.major == 8
    assert ret.minor is None

    ret2 = RHUIReleaseVer(context_wrap(INPUT_NG_3))
    assert ret2.set == 'ab.def'
    assert ret2.major is None
    assert ret2.minor is None


def test_rhui_release_wrong_input():
    with pytest.raises(SkipComponent) as e_info:
        RHUIReleaseVer(context_wrap(INPUT_NG_1))
    assert "Unexpected content" in str(e_info.value)


def test_doc_examples():
    env = {
            'rhui_rel': RHUISetRelease(context_wrap(INPUT_NORMAL_1)),
            'rhui_releasever': RHUIReleaseVer(context_wrap(INPUT_NORMAL_1))
          }
    failed, _ = doctest.testmod(rhui_release, globs=env)
    assert failed == 0
