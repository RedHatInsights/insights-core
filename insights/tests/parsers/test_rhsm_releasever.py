import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import rhsm_releasever as rhsm_releasever_module
from insights.parsers.rhsm_releasever import RhsmReleaseVer
from insights.tests import context_wrap
from insights.tests.parsers import skip_component_check

RHEL_MAJ_MIN = '{"releaseVer": "6.10"}'
RHEL_MAJ_1 = '{"releaseVer": "7Server"}'
RHEL_MAJ_2 = '{"releaseVer": "8"}'
RHEL_NONE = '{"releaseVer": ""}'
RHEL_NONE_2 = '{"releaseVer": null}'
RHEL_EMPTY = '{}'


def test_rhsm_releasever():
    relver = RhsmReleaseVer(context_wrap(RHEL_MAJ_MIN))
    assert relver['releaseVer'] == '6.10'
    assert relver.set == '6.10'
    assert relver.major == 6
    assert relver.minor == 10

    relver = RhsmReleaseVer(context_wrap(RHEL_MAJ_1))
    assert relver['releaseVer'] == '7Server'
    assert relver.set == '7Server'
    assert relver.major == 7
    assert relver.minor is None

    relver = RhsmReleaseVer(context_wrap(RHEL_MAJ_2))
    assert relver['releaseVer'] == '8'
    assert relver.set == '8'
    assert relver.major == 8
    assert relver.minor is None

    relver = RhsmReleaseVer(context_wrap(RHEL_NONE))
    assert relver['releaseVer'] == ''
    assert relver.set is None
    assert relver.major is None
    assert relver.minor is None

    relver = RhsmReleaseVer(context_wrap(RHEL_NONE_2))
    assert relver['releaseVer'] is None
    assert relver.set is None
    assert relver.major is None
    assert relver.minor is None

    with pytest.raises(SkipComponent) as e_info:
        RhsmReleaseVer(context_wrap(RHEL_EMPTY))
    assert "releaseVer is not in data" in str(e_info.value)


def test_empty():
    assert 'Empty output.' in skip_component_check(RhsmReleaseVer)


def test_doc_examples():
    env = {
        'rhsm_releasever': RhsmReleaseVer(context_wrap(RHEL_MAJ_MIN)),
    }
    failed, total = doctest.testmod(rhsm_releasever_module, globs=env)
    assert failed == 0
