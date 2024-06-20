import doctest
import pytest

from insights.combiners import redhat_release as rr
from insights.combiners.redhat_release import RedHatRelease
from insights.core.exceptions import SkipComponent
from insights.parsers.redhat_release import RedhatRelease
from insights.parsers.uname import Uname
from insights.tests import context_wrap

UNAME = "Linux localhost.localdomain 3.10.0-327.rt56.204.el7.x86_64 #1 SMP PREEMPT RT Thu Oct 29 21:54:23 EDT 2015 x86_64 x86_64 x86_64 GNU/Linux"
BAD_UNAME = "Linux localhost.localdomain 2.6.24.7-101.el5rt.x86_64 #1 SMP PREEMPT RT Thu Oct 29 21:54:23 EDT 2015 x86_64 x86_64 x86_64 GNU/Linux"
UNAME_CENTOS_7_9 = "Linux kvm-01-guest17.lab.eng.brq2.redhat.com 3.10.0-1160.el7.x86_64 #1 SMP Mon Oct 19 16:18:59 UTC 2020 x86_64 x86_64 x86_64 GNU/Linux"
UNAME_CENTOS_8_5 = "Linux kvm-02-guest12.rhts.eng.brq.redhat.com 4.18.0-348.7.1.el8_5.x86_64 #1 SMP Wed Dec 22 13:25:12 UTC 2021 x86_64 x86_64 x86_64 GNU/Linux"
UNAME_CENTOS_9STR = "Linux hpe-apollo-cn99xx-15-vm-17.khw4.lab.eng.bos.redhat.com 5.14.0-316.el9.aarch64 #1 SMP PREEMPT_DYNAMIC Fri May 19 12:15:43 UTC 2023 aarch64 aarch64 aarch64 GNU/Linux"

REDHAT_RELEASE = "Red Hat Enterprise Linux Server release 7.2 (Maipo)"
REDHAT_RELEASE_CENTOS_7_9 = "CentOS Linux release 7.9.2009 (Core)"
REDHAT_RELEASE_CENTOS_8_5 = "CentOS Linux release 8.5.2111"
REDHAT_RELEASE_CENTOS_9STR = "CentOS Stream release 9"
REDHAT_RELEASE_8_CONTAINER_1 = "Red Hat Enterprise Linux Server release 8.4 (Ootpa)"
REDHAT_RELEASE_8_CONTAINER_2 = "Red Hat Enterprise Linux Server release 8.6 (Ootpa)"

FEDORA = "Fedora release 23 (Twenty Three)"


def test_RedHatRelease_uname():
    un = Uname(context_wrap(UNAME))
    expected = (7, 2)
    result = RedHatRelease(un, None)
    assert result.major == expected[0]
    assert result.minor == expected[1]
    assert result.rhel == result.rhel7 == '7.2'
    assert result.rhel6 is None


def test_RedHatRelease_redhat_release():
    rel = RedhatRelease(context_wrap(REDHAT_RELEASE))
    expected = (7, 2)
    result = RedHatRelease(None, rel)
    assert result.major == expected[0]
    assert result.minor == expected[1]
    assert result.rhel == result.rhel7 == '7.2'
    assert result.rhel8 is None
    assert result.rhel9 is None


def test_RedHatRelease_both():
    un = Uname(context_wrap(UNAME))
    rel = RedhatRelease(context_wrap(REDHAT_RELEASE))
    expected = (7, 2)
    result = RedHatRelease(un, rel)
    assert result.major == expected[0]
    assert result.minor == expected[1]
    assert result.rhel == result.rhel7 == '7.2'
    assert result.rhel6 is None
    assert result.rhel8 is None
    assert result.rhel9 is None


def test_RedHatRelease_centos_7_9():
    rel = RedhatRelease(context_wrap(REDHAT_RELEASE_CENTOS_7_9))
    result = RedHatRelease(None, rel)
    assert result.major == 7
    assert result.minor == 9
    assert result.rhel == result.rhel7 == '7.9.2009'
    assert result.rhel8 is None
    assert result.rhel9 is None


def test_RedHatRelease_centos_7_9_both():
    un = Uname(context_wrap(UNAME_CENTOS_7_9))
    rel = RedhatRelease(context_wrap(REDHAT_RELEASE_CENTOS_7_9))
    result = RedHatRelease(un, rel)
    assert result.major == 7
    assert result.minor == 9
    assert result.rhel == result.rhel7 == '7.9'  # Not as nice as just /etc/redhat_release
    assert result.rhel8 is None
    assert result.rhel9 is None


def test_RedHatRelease_centos_8_5():
    rel = RedhatRelease(context_wrap(REDHAT_RELEASE_CENTOS_8_5))
    result = RedHatRelease(None, rel)
    assert result.major == 8
    assert result.minor == 5
    assert result.rhel7 is None
    assert result.rhel == result.rhel8 == '8.5.2111'
    assert result.rhel9 is None


def test_RedHatRelease_centos_8_5_both():
    un = Uname(context_wrap(UNAME_CENTOS_8_5))
    rel = RedhatRelease(context_wrap(REDHAT_RELEASE_CENTOS_8_5))
    result = RedHatRelease(un, rel)
    assert result.major == 8
    assert result.minor == 5
    assert result.rhel7 is None
    assert result.rhel == result.rhel8 == '8.5'  # Not as nice as just /etc/redhat_release
    assert result.rhel9 is None


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
