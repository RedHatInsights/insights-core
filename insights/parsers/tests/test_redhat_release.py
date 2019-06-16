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

from insights.parsers.redhat_release import RedhatRelease
from insights.tests import context_wrap


REDHAT_RELEASE1 = """
Red Hat Enterprise Linux Server release 6.7 (Santiago)
""".strip()

REDHAT_RELEASE2 = """
Red Hat Enterprise Linux Server release 7.2 (Maipo)
""".strip()

REDHAT_RELEASE3 = """
Red Hat Enterprise Linux release 7.5-0.14
""".strip()

RHVH_RHV40 = """
Red Hat Enterprise Linux release 7.3
""".strip()

RHEVH_RHEV35 = """
Red Hat Enterprise Virtualization Hypervisor release 6.7 (20160219.0.el6ev)
""".strip()

FEDORA = """
Fedora release 23 (Twenty Three)
""".strip()


def test_rhe6():
    release = RedhatRelease(context_wrap(REDHAT_RELEASE1))
    assert release.raw == REDHAT_RELEASE1
    assert release.major == 6
    assert release.minor == 7
    assert release.version == "6.7"
    assert release.is_rhel
    assert release.product == "Red Hat Enterprise Linux Server"


def test_rhe7():
    release = RedhatRelease(context_wrap(REDHAT_RELEASE2))
    assert release.raw == REDHAT_RELEASE2
    assert release.major == 7
    assert release.minor == 2
    assert release.version == "7.2"
    assert release.is_rhel
    assert release.product == "Red Hat Enterprise Linux Server"


def test_rhe75_0_14():
    release = RedhatRelease(context_wrap(REDHAT_RELEASE3))
    assert release.raw == REDHAT_RELEASE3
    assert release.major == 7
    assert release.minor == 5
    assert release.version == "7.5-0.14"
    assert release.is_rhel
    assert release.product == "Red Hat Enterprise Linux"


def test_rhevh35():
    release = RedhatRelease(context_wrap(RHEVH_RHEV35))
    assert release.raw == RHEVH_RHEV35
    assert release.major == 6
    assert release.minor == 7
    assert release.version == "6.7"
    assert not release.is_rhel
    assert release.product == "Red Hat Enterprise Virtualization Hypervisor"


def test_rhvh40():
    release = RedhatRelease(context_wrap(RHVH_RHV40))
    assert release.raw == RHVH_RHV40
    assert release.major == 7
    assert release.minor == 3
    assert release.version == "7.3"
    assert release.is_rhel
    assert release.product == "Red Hat Enterprise Linux"


def test_fedora23():
    release = RedhatRelease(context_wrap(FEDORA))
    assert release.raw == FEDORA
    assert release.major == 23
    assert release.minor is None
    assert release.version == "23"
    assert not release.is_rhel
    assert release.product == "Fedora"
