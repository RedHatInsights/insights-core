import pytest

from insights.combiners.redhat_release import RedHatRelease as RR
from insights.components.rhel_version import (
    IsRhel6, IsRhel7, IsRhel8, IsRhel9,
    IsGtRhel86, IsGtOrRhel86)
from insights.core.exceptions import SkipComponent
from insights.parsers.redhat_release import RedhatRelease
from insights.parsers.uname import Uname
from insights.tests import context_wrap


UNAME = "Linux localhost.localdomain 3.10.0-327.rt56.204.el7.x86_64 #1 SMP PREEMPT RT Thu Oct 29 21:54:23 EDT 2015 x86_64 x86_64 x86_64 GNU/Linux"

REDHAT_RELEASE_67 = """
Red Hat Enterprise Linux Server release 6.7 (Santiago)
""".strip()

REDHAT_RELEASE_72 = """
Red Hat Enterprise Linux Server release 7.2 (Maipo)
""".strip()

REDHAT_RELEASE_75_014 = """
Red Hat Enterprise Linux release 7.5-0.14
""".strip()

REDHAT_RELEASE_80 = """
Red Hat Enterprise Linux release 8.0 (Ootpa)
""".strip()

REDHAT_RELEASE_86 = """
Red Hat Enterprise Linux release 8.6 (Ootpa)
""".strip()

REDHAT_RELEASE_90 = """
Red Hat Enterprise Linux release 9.0 (Plow)
""".strip()


# RHEL6 Tests
def test_is_rhel6():
    rr = RedhatRelease(context_wrap(REDHAT_RELEASE_67))
    rel = RR(None, rr)
    result = IsRhel6(rel)
    assert isinstance(result, IsRhel6)

    rr = RedhatRelease(context_wrap(REDHAT_RELEASE_72))
    rel = RR(None, rr)
    with pytest.raises(SkipComponent) as e:
        IsRhel6(rel)
    assert "Not RHEL 6" in str(e)


# RHEL7 Server Tests
def test_is_rhel7():
    rr = RedhatRelease(context_wrap(REDHAT_RELEASE_72))
    rel = RR(None, rr)
    result = IsRhel7(rel)
    assert isinstance(result, IsRhel7)

    rr = RedhatRelease(context_wrap(REDHAT_RELEASE_67))
    rel = RR(None, rr)
    with pytest.raises(SkipComponent) as e:
        IsRhel7(rel)
    assert "Not RHEL 7" in str(e)

    uname = Uname(context_wrap(UNAME))
    rr = RedhatRelease(context_wrap(REDHAT_RELEASE_75_014))
    rel = RR(uname, rr)
    result = IsRhel7(rel)
    assert isinstance(result, IsRhel7)

    rr = RedhatRelease(context_wrap(REDHAT_RELEASE_75_014))
    rel = RR(None, rr)
    result = IsRhel7(rel)
    assert isinstance(result, IsRhel7)

    rr = RedhatRelease(context_wrap(REDHAT_RELEASE_67))
    rel = RR(None, rr)
    with pytest.raises(SkipComponent) as e:
        IsRhel7(rel)
    assert "Not RHEL 7" in str(e)


# RHEL8 Tests
def test_is_rhel8():
    rr = RedhatRelease(context_wrap(REDHAT_RELEASE_80))
    rel = RR(None, rr)
    result = IsRhel8(rel)
    assert isinstance(result, IsRhel8)

    rr = RedhatRelease(context_wrap(REDHAT_RELEASE_72))
    rel = RR(None, rr)
    with pytest.raises(SkipComponent) as e:
        IsRhel8(rel)
    assert "Not RHEL 8" in str(e)


# RHEL9 Tests
def test_is_rhel9():
    rr = RedhatRelease(context_wrap(REDHAT_RELEASE_90))
    rel = RR(None, rr)
    result = IsRhel9(rel)
    assert isinstance(result, IsRhel9)

    rr = RedhatRelease(context_wrap(REDHAT_RELEASE_80))
    rel = RR(None, rr)
    with pytest.raises(SkipComponent) as e:
        IsRhel9(rel)
    assert "Not RHEL 9" in str(e)


# Great Than or Equal
def test_gt_or_eq_rhel86():
    rr = RedhatRelease(context_wrap(REDHAT_RELEASE_80))
    rel = RR(None, rr)
    with pytest.raises(SkipComponent) as e:
        IsGtOrRhel86(rel)
    assert "Not RHEL newer than or equal 8.6" in str(e)

    rr = RedhatRelease(context_wrap(REDHAT_RELEASE_86))
    rel = RR(None, rr)
    ret = IsGtOrRhel86(rel)
    assert ret.major == 8
    assert ret.minor == 6

    rr = RedhatRelease(context_wrap(REDHAT_RELEASE_90))
    rel = RR(None, rr)
    ret = IsGtOrRhel86(rel)
    assert ret.major == 9
    assert ret.minor == 0


# Great Than
def test_gt_rhel86():
    rr = RedhatRelease(context_wrap(REDHAT_RELEASE_80))
    rel = RR(None, rr)
    with pytest.raises(SkipComponent) as e:
        IsGtRhel86(rel)
    assert "Not RHEL newer than 8.6" in str(e)

    rr = RedhatRelease(context_wrap(REDHAT_RELEASE_86))
    rel = RR(None, rr)
    with pytest.raises(SkipComponent) as e:
        IsGtRhel86(rel)
    assert "Not RHEL newer than 8.6" in str(e)

    rr = RedhatRelease(context_wrap(REDHAT_RELEASE_90))
    rel = RR(None, rr)
    ret = IsGtRhel86(rel)
    assert ret.major == 9
    assert ret.minor == 0
