from falafel.mappers.redhat_release import RedhatRelease
from falafel.tests import context_wrap

REDHAT_RELEASE1 = """
Red Hat Enterprise Linux Server release 6.7 (Santiago)
""".strip()

REDHAT_RELEASE2 = """
Red Hat Enterprise Linux Server release 7.2 (Maipo)
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
    assert release.is_rhel is True, release.product
    assert release.product == "Red Hat Enterprise Linux Server", release.product


def test_rhe7():
    release = RedhatRelease(context_wrap(REDHAT_RELEASE2))
    assert release.raw == REDHAT_RELEASE2
    assert release.major == 7
    assert release.minor == 2
    assert release.version == "7.2"
    assert release.is_rhel is True
    assert release.product == "Red Hat Enterprise Linux Server", release.product


def test_fedora23():
    release = RedhatRelease(context_wrap(FEDORA))
    assert release.raw == FEDORA
    assert release.major == 23
    assert release.minor is None
    assert release.version == "23"
    assert release.is_rhel is False
    assert release.product == "Fedora"
