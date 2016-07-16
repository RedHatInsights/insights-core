from falafel.mappers import redhat_release
from falafel.tests import context_wrap

REDHAT_RELEASE1 = """
Red Hat Enterprise Linux Server release 7.2 (Maipo)
""".strip()

REDHAT_RELEASE2 = """
Red Hat Enterprise Linux Server release 6.7 (Santiago)
""".strip()


def test_redhat_release():
    release = redhat_release.redhat_release(context_wrap(REDHAT_RELEASE1))
    assert release.get("file_content") == "Red Hat Enterprise Linux Server release 7.2 (Maipo)"

    release = redhat_release.redhat_release(context_wrap(REDHAT_RELEASE2))
    assert release.get("file_content") == "Red Hat Enterprise Linux Server release 6.7 (Santiago)"
