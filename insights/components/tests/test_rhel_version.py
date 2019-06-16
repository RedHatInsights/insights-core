#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from insights.components.rhel_version import IsRhel6, IsRhel7, IsRhel8
from insights.combiners.redhat_release import RedHatRelease as RR
from insights.parsers.uname import Uname
from insights.parsers.redhat_release import RedhatRelease
from insights.tests import context_wrap
from insights.core.dr import SkipComponent
import pytest


UNAME = "Linux localhost.localdomain 3.10.0-327.rt56.204.el7.x86_64 #1 SMP PREEMPT RT Thu Oct 29 21:54:23 EDT 2015 x86_64 x86_64 x86_64 GNU/Linux"

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
Red Hat Enterprise Linux release 8.0 (Ootpa)
""".strip()


# RHEL6 Tests
def test_is_rhel6():
    rr = RedhatRelease(context_wrap(REDHAT_RELEASE1))
    rel = RR(None, rr)
    result = IsRhel6(rel)
    assert isinstance(result, IsRhel6)


def test_not_rhel6():
    rr = RedhatRelease(context_wrap(REDHAT_RELEASE2))
    rel = RR(None, rr)
    with pytest.raises(SkipComponent) as e:
        IsRhel6(rel)
    assert "Not RHEL6" in str(e)


# RHEL7 Server Tests
def test_is_rhel7s():
    rr = RedhatRelease(context_wrap(REDHAT_RELEASE2))
    rel = RR(None, rr)
    result = IsRhel7(rel)
    assert isinstance(result, IsRhel7)


def test_not_rhel7s():
    rr = RedhatRelease(context_wrap(REDHAT_RELEASE1))
    rel = RR(None, rr)
    with pytest.raises(SkipComponent) as e:
        IsRhel7(rel)
    assert "Not RHEL7" in str(e)


# RHEL7 Tests
def test_uname_is_rhel7():
    uname = Uname(context_wrap(UNAME))
    rr = RedhatRelease(context_wrap(REDHAT_RELEASE3))
    rel = RR(uname, rr)
    result = IsRhel7(rel)
    assert isinstance(result, IsRhel7)


def test_is_rhel7():
    rr = RedhatRelease(context_wrap(REDHAT_RELEASE3))
    rel = RR(None, rr)
    result = IsRhel7(rel)
    assert isinstance(result, IsRhel7)


def test_not_rhel7():
    rr = RedhatRelease(context_wrap(REDHAT_RELEASE1))
    rel = RR(None, rr)
    with pytest.raises(SkipComponent) as e:
        IsRhel7(rel)
    assert "Not RHEL7" in str(e)


# RHEL8 Tests
def test_is_rhel8():
    rr = RedhatRelease(context_wrap(REDHAT_RELEASE4))
    rel = RR(None, rr)
    result = IsRhel8(rel)
    assert isinstance(result, IsRhel8)


def test_not_rhel8():
    rr = RedhatRelease(context_wrap(REDHAT_RELEASE2))
    rel = RR(None, rr)
    with pytest.raises(SkipComponent) as e:
        IsRhel8(rel)
    assert "Not RHEL8" in str(e)
