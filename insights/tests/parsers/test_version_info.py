import doctest

from insights.parsers import version_info
from insights.tests import context_wrap
from insights.tests.parsers import skip_component_check


VER_INFO_1 = """
{"core_version": "3.0.8-dev", "client_version": "3.1.1"}
""".strip()

VER_INFO_2 = """
{"core_version": "3.0.203-1", "client_version": "3.1.1"}
""".strip()


def test_version_info():
    ret = version_info.VersionInfo(context_wrap(VER_INFO_1))
    assert ret.core_version == '3.0.8-dev'
    assert ret.client_version == '3.1.1'

    ret = version_info.VersionInfo(context_wrap(VER_INFO_2))
    assert ret.core_version == '3.0.203-1'
    assert ret.client_version == '3.1.1'


def test_version_info_empty():
    assert 'Empty output.' in skip_component_check(version_info.VersionInfo)


def test_doc_examples():
    env = {
        'ver': version_info.VersionInfo(context_wrap(VER_INFO_2)),
    }
    failed, total = doctest.testmod(version_info, globs=env)
    assert failed == 0
