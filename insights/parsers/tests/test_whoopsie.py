import doctest
import pytest

from insights.parsers import whoopsie
from insights.parsers.whoopsie import Whoopsie
from insights.tests import context_wrap

BOTH_MATCHED = """
/var/crash/.reports-1000-user/whoopsie-report
""".strip()

NOT_FIND_MATCHED = """
/usr/bin/find: '/var/crash': No such file or directory
/var/tmp/.reports-1000-user/whoopsie-report
""".strip()

BOTH_NOT_FIND = """
/usr/bin/find: '/var/crash': No such file or directory
/usr/bin/find: '/var/tmp': No such file or directory
""".strip()

BOTH_EMPTY = """
"""

TEST_CASES = [
    (BOTH_MATCHED, "1000", "/var/crash/.reports-1000-user/whoopsie-report"),
    (NOT_FIND_MATCHED, "1000", "/var/tmp/.reports-1000-user/whoopsie-report"),
    (BOTH_NOT_FIND, None, None),
    (BOTH_EMPTY, None, None)
]


@pytest.mark.parametrize("output, uid, file", TEST_CASES)
def test_whoopsie(output, uid, file):
    test = Whoopsie(context_wrap(output))
    assert test.uid == uid
    assert test.file == file


def test_doc_examples():
    env = {
        "whoopsie": Whoopsie(context_wrap(BOTH_MATCHED)),
    }
    failed, total = doctest.testmod(whoopsie, globs=env)
    assert failed == 0
