import doctest

from insights.parsers import redhat_release
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

REDHAT_RELEASE8 = """
Red Hat Enterprise Linux release 8.2 (Ootpa)
""".strip()

REDHAT_RELEASE10 = """
Red Hat Enterprise Linux Server release 6.10(Santiago)
""".strip()

REDHAT_RELEASE_BETA = """
Red Hat Enterprise Linux Server release 8.5 Beta (Ootpa)
""".strip()

CENTOS_STREAM = """
CentOS Stream release 8
""".strip()

CENTOS_7 = """
CentOS Linux release 7.6.1810 (Core)
""".strip()

REDHAT_RELEASE_ALPHA = """
Red Hat Enterprise Linux release 9.0 Alpha (Plow)
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
    assert release.is_fedora
    assert release.product == "Fedora"


def test_rhel6_10():
    release = RedhatRelease(context_wrap(REDHAT_RELEASE10))
    assert release.raw == REDHAT_RELEASE10
    assert release.major == 6
    assert release.minor == 10
    assert release.version == "6.10"
    assert release.is_rhel
    assert release.product == "Red Hat Enterprise Linux Server"


def test_rhel8():
    release = RedhatRelease(context_wrap(REDHAT_RELEASE8))
    assert release.raw == REDHAT_RELEASE8
    assert release.major == 8
    assert release.minor == 2
    assert release.version == "8.2"
    assert release.is_rhel
    assert release.product == "Red Hat Enterprise Linux"


def test_rhel_alpha():
    release = RedhatRelease(context_wrap(REDHAT_RELEASE_ALPHA))
    assert release.raw == REDHAT_RELEASE_ALPHA
    assert release.major == 9
    assert release.minor == 0
    assert release.version == "9.0"
    assert release.is_rhel
    assert release.is_alpha
    assert not release.is_beta
    assert release.parsed['code_name'] == 'Plow'
    assert release.product == "Red Hat Enterprise Linux"


def test_rhel_beta():
    release = RedhatRelease(context_wrap(REDHAT_RELEASE_BETA))
    assert release.raw == REDHAT_RELEASE_BETA
    assert release.major == 8
    assert release.minor == 5
    assert release.version == "8.5"
    assert release.is_rhel
    assert release.is_beta
    assert not release.is_alpha
    assert release.parsed['code_name'] == 'Ootpa'
    assert release.product == "Red Hat Enterprise Linux Server"


def test_centos_stream():
    release = RedhatRelease(context_wrap(CENTOS_STREAM))
    assert release.major == 8
    assert release.minor is None
    assert release.product == 'CentOS Stream'
    assert release.is_centos
    assert not release.is_rhel


def test_centos_7():
    release = RedhatRelease(context_wrap(CENTOS_7))
    assert release.major == 7
    assert release.minor == 6
    assert release.product == 'CentOS Linux'
    assert release.code_name == 'Core'
    assert release.is_centos
    assert not release.is_rhel


def test_examples():
    release = RedhatRelease(context_wrap(REDHAT_RELEASE2))
    globs = {
        'rh_release': release
    }
    failed, tested = doctest.testmod(redhat_release, globs=globs)
    assert failed == 0
