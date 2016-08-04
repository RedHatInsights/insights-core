from falafel.mappers import redhat_release
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
    release = redhat_release.redhat_release(context_wrap(REDHAT_RELEASE1))
    assert release.data == REDHAT_RELEASE1
    assert release.major == 6
    assert release.minor == 7
    assert release.version == 6.7
    assert release.is_rhel is True, release.product
    assert release.product == "Red Hat Enterprise Linux Server", release.product


def test_rhe7():
    release = redhat_release.redhat_release(context_wrap(REDHAT_RELEASE2))
    assert release.data == REDHAT_RELEASE2
    assert release.major == 7
    assert release.minor == 2
    assert release.version == 7.2
    assert release.is_rhel is True
    assert release.product == "Red Hat Enterprise Linux Server", release.product


def test_fedora23():
    release = redhat_release.redhat_release(context_wrap(FEDORA))
    assert release.data == FEDORA
    assert release.major == 23
    assert release.minor is None
    assert release.version == 23.0
    assert release.is_rhel is False
    assert release.product == "Fedora"
