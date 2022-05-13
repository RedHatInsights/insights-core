import doctest
from insights.parsers import rhosp_release
from insights.tests import context_wrap


ROCKY = """
Red Hat OpenStack Platform release 14.0.0 RC (Rocky)
""".strip()


PIKE = """
Red Hat OpenStack Platform release 12.0 Beta (Pike)
""".strip()


def test_rhosp_release():
    rocky = rhosp_release.RhospRelease(context_wrap(ROCKY))
    assert rocky.product == "Red Hat OpenStack Platform"
    assert rocky.version == '14.0.0'
    assert rocky.code_name == "Rocky"

    pike = rhosp_release.RhospRelease(context_wrap(PIKE))
    assert pike.product == "Red Hat OpenStack Platform"
    assert pike.version == '12.0'
    assert pike.code_name == "Pike"


def test_documentation():
    failed_count, tests = doctest.testmod(
        rhosp_release,
        globs={'release': rhosp_release.RhospRelease(context_wrap(ROCKY))})
    assert failed_count == 0
