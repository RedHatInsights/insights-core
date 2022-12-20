from insights.parsers.uname import Uname
from insights.parsers.os_release import OsRelease
from insights.parsers.redhat_release import RedhatRelease
from insights.combiners.redhat_release import RedHatRelease
from insights.combiners import redhat_release as rr
from insights.tests import context_wrap
from insights.parsers import SkipComponent
import pytest
import doctest

UNAME = "Linux localhost.localdomain 3.10.0-327.rt56.204.el7.x86_64 #1 SMP PREEMPT RT Thu Oct 29 21:54:23 EDT 2015 x86_64 x86_64 x86_64 GNU/Linux"
BAD_UNAME = "Linux localhost.localdomain 2.6.24.7-101.el5rt.x86_64 #1 SMP PREEMPT RT Thu Oct 29 21:54:23 EDT 2015 x86_64 x86_64 x86_64 GNU/Linux"

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

RHEL_OS_RELEASE = """
NAME="Red Hat Enterprise Linux"
VERSION="8.5 (Ootpa)"
ID="rhel"
ID_LIKE="fedora"
VERSION_ID="8.5"
PRETTY_NAME="Red Hat Enterprise Linux 8.5 (Ootpa)"
"""

ORACLE_LINUX_OS_RELEASE = """
NAME="Oracle Linux Server"
VERSION="8.3"
ID="ol"
ID_LIKE="fedora"
VARIANT="Server"
VARIANT_ID="server"
VERSION_ID="8.3"
PLATFORM_ID="platform:el8"
PRETTY_NAME="Oracle Linux Server 8.3"
ANSI_COLOR="0;31"
CPE_NAME="cpe:/o:oracle:linux:8:3:server"
HOME_URL="https://linux.oracle.com/"
BUG_REPORT_URL="https://bugzilla.oracle.com/"
"""


def test_RedHatRelease_uname():
    un = Uname(context_wrap(UNAME))
    expected = (7, 2)
    result = RedHatRelease(un, None, None)
    assert result.major == expected[0]
    assert result.minor == expected[1]
    assert result.rhel == result.rhel7 == '7.2'
    assert result.rhel6 is None


def test_RedHatRelease_redhat_release():
    rel = RedhatRelease(context_wrap(REDHAT_RELEASE))
    expected = (7, 2)
    result = RedHatRelease(None, rel, None)
    assert result.major == expected[0]
    assert result.minor == expected[1]
    assert result.rhel == result.rhel7 == '7.2'
    assert result.rhel8 is None
    assert result.rhel9 is None


def test_RedHatRelease_redhat_release_with_os_release():
    rel = RedhatRelease(context_wrap(REDHAT_RELEASE))
    os_rel = OsRelease(context_wrap(RHEL_OS_RELEASE))
    expected = (7, 2)
    result = RedHatRelease(None, rel, os_rel)
    assert result.major == expected[0]
    assert result.minor == expected[1]
    assert result.rhel == result.rhel7 == '7.2'
    assert result.rhel8 is None
    assert result.rhel9 is None


def test_RedHatRelease_redhat_release_with_oracle_os_release():
    rel = RedhatRelease(context_wrap(REDHAT_RELEASE))
    os_rel = OsRelease(context_wrap(ORACLE_LINUX_OS_RELEASE))
    with pytest.raises(SkipComponent):
        RedHatRelease(None, rel, os_rel)


def test_RedHatRelease_both():
    un = Uname(context_wrap(UNAME))
    rel = RedhatRelease(context_wrap(REDHAT_RELEASE))
    expected = (7, 2)
    result = RedHatRelease(un, rel, None)
    assert result.major == expected[0]
    assert result.minor == expected[1]
    assert result.rhel == result.rhel7 == '7.2'
    assert result.rhel6 is None
    assert result.rhel8 is None
    assert result.rhel9 is None


def test_raise():
    un = Uname(context_wrap(BAD_UNAME))

    with pytest.raises(SkipComponent):
        RedHatRelease(un, None, None)

    with pytest.raises(SkipComponent):
        RedHatRelease(None, None, None)


def test_doc_examples():
    env = {
        'rh_rel': RedHatRelease(Uname(context_wrap(UNAME)), None, None),
    }
    failed, total = doctest.testmod(rr, globs=env)
    assert failed == 0
