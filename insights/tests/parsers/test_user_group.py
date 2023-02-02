import doctest
import pytest

from insights.core.exceptions import ParseException, SkipComponent
from insights.parsers import user_group
from insights.parsers.user_group import GroupInfo
from insights.tests import context_wrap

GRP = """
wheel:x:10:admin,tester
mem:x:8:
""".strip()
GRP_NG = """
unknow_case
""".strip()
GRP_EMPTY = ""


def test_grp():
    grp = GroupInfo(context_wrap(GRP))
    assert grp[0]['id'] == 10
    assert grp[0]['name'] == 'wheel'
    assert grp[0]['users'] == ['admin', 'tester']
    assert grp[1]['id'] == 8
    assert grp[1]['name'] == 'mem'
    assert grp[1]['users'] == []
    assert grp.search(users__contains='tester')[0] == grp[0]


def test_ab():
    with pytest.raises(SkipComponent):
        GroupInfo(context_wrap(GRP_EMPTY))

    with pytest.raises(ParseException):
        GroupInfo(context_wrap(GRP_NG))


def test_doc_examples():
    env = {
        'grp': GroupInfo(context_wrap(GRP))
    }
    failed, total = doctest.testmod(user_group, globs=env)
    assert failed == 0
