from insights.components.rhel_version import Is_Rhel6, Is_Rhel7, Is_Rhel8
from insights.parsers.redhat_release import RedhatRelease as RR
from insights.tests import context_wrap
from insights.core.dr import SkipComponent
import pytest


REDHAT_RELEASE1 = """
Red Hat Enterprise Linux Server release 6.7 (Santiago)
""".strip()

REDHAT_RELEASE2 = """
Red Hat Enterprise Linux Server release 7.2 (Maipo)
""".strip()

REDHAT_RELEASE3 = """
Red Hat Enterprise Linux release 7.5-0.14
""".strip()

REDHAT_RELEASE4 = """
RedHat Enterprise Linux release 8.0 (Ootpa)
""".strip()


# RHEL6 Tests
def test_is_rhel6():
    rel = RR(context_wrap(REDHAT_RELEASE1))
    expected = '6.7'
    result = Is_Rhel6(rel)
    assert result.rhel_version == expected


def test_not_rhel6():
    rel = RR(context_wrap(REDHAT_RELEASE2))
    with pytest.raises(SkipComponent) as e:
        Is_Rhel6(rel)
    assert "Not RHEL6" in str(e)


# RHEL7 Server Tests
def test_is_rhel7s():
    rel = RR(context_wrap(REDHAT_RELEASE2))
    expected = '7.2'
    result = Is_Rhel7(rel)
    assert result.rhel_version == expected


def test_not_rhel7s():
    rel = RR(context_wrap(REDHAT_RELEASE1))
    with pytest.raises(SkipComponent) as e:
        Is_Rhel7(rel)
    assert "Not RHEL7" in str(e)


# RHEL7 Tests
def test_is_rhel7():
    rel = RR(context_wrap(REDHAT_RELEASE3))
    expected = '7.5-0.14'
    result = Is_Rhel7(rel)
    assert result.rhel_version == expected


def test_not_rhel7():
    rel = RR(context_wrap(REDHAT_RELEASE1))
    with pytest.raises(SkipComponent) as e:
        Is_Rhel7(rel)
    assert "Not RHEL7" in str(e)


# RHEL8 Tests
def test_is_rhel8():
    rel = RR(context_wrap(REDHAT_RELEASE4))
    expected = '8.0'
    result = Is_Rhel8(rel)
    assert result.rhel_version == expected


def test_not_rhel8():
    rel = RR(context_wrap(REDHAT_RELEASE2))
    with pytest.raises(SkipComponent) as e:
        Is_Rhel8(rel)
    assert "Not RHEL8" in str(e)
