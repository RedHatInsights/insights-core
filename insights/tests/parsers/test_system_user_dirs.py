import doctest
import pytest

from insights.parsers import system_user_dirs
from insights.parsers.system_user_dirs import SystemUserDirs
from insights.tests import context_wrap


TEST_CASES = [
    (
        '{"pcp-testsuite-5.3.3-1.fc33.x86_64": ["/var/lib/pcp/testsuite"]}',
        {
            "pcp-testsuite-5.3.3-1.fc33.x86_64": ["/var/lib/pcp/testsuite"]
        }
    ),
    (
        '{}',
        {}
    )
]


@pytest.mark.parametrize("output, expected", TEST_CASES)
def test_system_user_dirs(output, expected):
    test = SystemUserDirs(context_wrap(output))
    assert test.data == expected


def test_doc_examples():
    env = {
        "system_user_dirs": SystemUserDirs(context_wrap(TEST_CASES[0][0]))
    }
    failed, total = doctest.testmod(system_user_dirs, globs=env)
    assert failed == 0
