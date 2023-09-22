import doctest
import pytest

from insights.core.exceptions import ParseException, SkipComponent
from insights.parsers import proc_keyusers
from insights.parsers.proc_keyusers import ProcKeyUsers
from insights.tests import context_wrap

PROC_KEYUSERS = """
    0:   106 105/105 95/1000000 1909/25000000
  862:     4 4/4 4/200 40/20000
  980:     9 9/9 9/200 138/20000
  983:     1 1/1 1/200 9/20000
 5090:   192 192/192 192/200 990/20000
 7502:     8 8/8 8/200 66/20000
 7563:     4 4/4 4/200 46/20000
 7637:     4 4/4 4/200 46/20000
""".strip()

PROC_KEYUSERS_INVALID_1 = """
    0    106 105/105 95/1000000 1909/25000000
  983:     1 1/1 1/200 9/20000
""".strip()

PROC_KEYUSERS_INVALID_2 = """
    0:   106: 105/105 95/1000000 1909/25000000
""".strip()

PROC_KEYUSERS_INVALID_3 = """
    0:   106 105/105 95/1000000 1909/25000000
  862:     4 4/4 4/200 40/20000
  980:     9/9 9/9 9/200 138/20000
  983:     1 1/1 1/200 9/20000
""".strip()

PROC_KEYUSERS_INVALID_4 = """
    0:   106 105/105 95/1000000 1909/25000000
  980:     9 9/9 9/2s0 138/20000
  983:     1 1/1 1/200 9/20000
""".strip()

PROC_KEYUSERS_EMPTY = """
""".strip()


def test_proc_keyusers_valid():
    key_users = ProcKeyUsers(context_wrap(PROC_KEYUSERS))
    assert len(key_users) == 8
    assert key_users[4]['uid'] == '5090'
    assert key_users[4]['usage'] == 192
    assert key_users[4]['nkeys'] == 192
    assert key_users[4]['nikeys'] == 192
    assert key_users[4]['qnkeys'] == 192
    assert key_users[4]['maxkeys'] == 200
    assert key_users[4]['qnbytes'] == 990
    assert key_users[4]['maxbytes'] == 20000
    assert key_users[6]['uid'] == '7563'


def test_proc_keyusers_invalid():
    with pytest.raises(SkipComponent):
        ProcKeyUsers(context_wrap(PROC_KEYUSERS_EMPTY))

    for input in [PROC_KEYUSERS_INVALID_1,
                    PROC_KEYUSERS_INVALID_2,
                    PROC_KEYUSERS_INVALID_3,
                    PROC_KEYUSERS_INVALID_4]:
        with pytest.raises(ParseException) as e:
            ProcKeyUsers(context_wrap(input))
        assert "Unparsable line: " in str(e)


def test_proc_keyusers_docstrings():
    env = {
        'proc_keyusers': ProcKeyUsers(context_wrap(PROC_KEYUSERS))
    }
    failed, total = doctest.testmod(proc_keyusers, globs=env)
    assert failed == 0
