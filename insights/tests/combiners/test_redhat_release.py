import doctest
import pytest

from insights.combiners import redhat_release as rr
from insights.combiners.redhat_release import RedHatRelease, serialize_RedHatRelease, deserialize_RedHatRelease
from insights.core.exceptions import SkipComponent
from insights.parsers.redhat_release import RedhatRelease as RRParser
from insights.parsers.uname import Uname
from insights.tests import context_wrap

UNAME = "Linux localhost.localdomain 3.10.0-327.rt56.204.el7.x86_64 #1 SMP PREEMPT RT Thu Oct 29 21:54:23 EDT 2015 x86_64 x86_64 x86_64 GNU/Linux"
BAD_UNAME = "Linux localhost.localdomain 2.6.24.7-101.el5rt.x86_64 #1 SMP PREEMPT RT Thu Oct 29 21:54:23 EDT 2015 x86_64 x86_64 x86_64 GNU/Linux"
UNAME_10 = "Linux localhost.localdomain 6.12.0-55.14.1.el10_0.x86_64 #1 SMP PREEMPT_DYNAMIC Mon May 26 04:24:13 EDT 2025 x86_64 GNU/Linux"

REDHAT_RELEASE = """
Red Hat Enterprise Linux Server release 7.2 (Maipo)
""".strip()

FEDORA = """
Fedora release 23 (Twenty Three)
""".strip()

REDHAT_RELEASE_8_CONTAINER_1 = """
Red Hat Enterprise Linux Server release 8.4 (Ootpa)
""".strip()

REDHAT_RELEASE_8_CONTAINER_2 = """
Red Hat Enterprise Linux Server release 8.6 (Ootpa)
""".strip()

REDHAT_RELEASE_10_0 = """
Red Hat Enterprise Linux release 10.0 (Coughlan)
""".strip()


def test_RedHatRelease_uname():
    un = Uname(context_wrap(UNAME))
    expected = (7, 2)
    result = RedHatRelease(un, None)
    assert result.major == expected[0]
    assert result.minor == expected[1]
    assert result.rhel == result.rhel7 == '7.2'
    assert result.rhel6 is None


def test_RedHatRelease_uname_10():
    un = Uname(context_wrap(UNAME_10))
    expected = (10, 0)
    result = RedHatRelease(un, None)
    assert result.major == expected[0]
    assert result.minor == expected[1]
    assert result.rhel == result.rhel10 == '10.0'
    assert result.rhel9 is None


def test_RedHatRelease_redhat_release():
    rel = RRParser(context_wrap(REDHAT_RELEASE))
    expected = (7, 2)
    result = RedHatRelease(None, rel)
    assert result.major == expected[0]
    assert result.minor == expected[1]
    assert result.rhel == result.rhel7 == '7.2'
    assert result.rhel8 is None
    assert result.rhel9 is None


def test_RedHatRelease_both():
    un = Uname(context_wrap(UNAME))
    rel = RRParser(context_wrap(REDHAT_RELEASE))
    expected = (7, 2)
    result = RedHatRelease(un, rel)
    assert result.major == expected[0]
    assert result.minor == expected[1]
    assert result.rhel == result.rhel7 == '7.2'
    assert result.rhel6 is None
    assert result.rhel8 is None
    assert result.rhel9 is None


def test_RedHatRelease_serialize_deserialize():
    rel = RedHatRelease(None, RRParser(context_wrap(REDHAT_RELEASE_10_0)))
    serialized = serialize_RedHatRelease(rel)
    assert serialized == {
            "major": 10,
            "minor": 0,
            "rhel": "10.0",
            "rhel6": None,
            "rhel7": None,
            "rhel8": None,
            "rhel9": None,
            "rhel10": "10.0",
    }

    deserialized = deserialize_RedHatRelease(RedHatRelease, serialized)
    expected = (10, 0)
    assert deserialized.major == expected[0]
    assert deserialized.minor == expected[1]
    assert deserialized.rhel6 is None
    assert deserialized.rhel7 is None
    assert deserialized.rhel8 is None
    assert deserialized.rhel9 is None
    assert deserialized.rhel == deserialized.rhel10 == '10.0'


def test_raise():
    un = Uname(context_wrap(BAD_UNAME))

    with pytest.raises(SkipComponent):
        RedHatRelease(un, None)

    with pytest.raises(SkipComponent):
        RedHatRelease(None, None)


def test_doc_examples():
    env = {
            'rh_rel': RedHatRelease(Uname(context_wrap(UNAME)), None),
          }
    failed, total = doctest.testmod(rr, globs=env)
    assert failed == 0
