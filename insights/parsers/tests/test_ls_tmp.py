import doctest

from insights.parsers import ls_tmp
from insights.parsers.ls_tmp import LsTmp
from insights.tests import context_wrap

LS_LD_TMP = """
drwxrwxrwt. 8 root root 160 Apr 16 12:37 /tmp
""".strip()


def test_ls_tmp():
    ls_tmp = LsTmp(context_wrap(LS_LD_TMP, path='ls_-ld_.tmp'))
    assert ls_tmp.listing_of("/dummy-sysroot")['tmp'] == {'group': 'root', 'name': 'tmp', 'links': 8, 'perms': 'rwxrwxrwt.', 'raw_entry': 'drwxrwxrwt. 8 root root 160 Apr 16 12:37 tmp', 'owner': 'root', 'date': 'Apr 16 12:37', 'type': 'd', 'dir': '/dummy-sysroot', 'size': 160}
    assert ls_tmp.dir_entry("/dummy-sysroot", 'tmp')['perms'] == 'rwxrwxrwt.'


def test_ls_tmp_doc_examples():
    env = {
        'LsTmp': LsTmp,
        'ls_tmp': LsTmp(context_wrap(LS_LD_TMP, path='ls_-ld_.tmp')),
    }
    failed, total = doctest.testmod(ls_tmp, globs=env)
    assert failed == 0
