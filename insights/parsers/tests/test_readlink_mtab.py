import pytest
import doctest

from insights.tests import context_wrap
from insights.parsers import readlink_e_mtab, SkipException

REAL_FILE_PATH = '''
/proc/4578/mounts
'''.strip()

BAD_FILE_PATH = ""


def test_doc_examples():
    env = {
        'mtab': readlink_e_mtab.ReadLinkEMtab(
            context_wrap(REAL_FILE_PATH)),
    }
    failed, total = doctest.testmod(readlink_e_mtab, globs=env)
    assert failed == 0


def test_readlink_e_mtab():
    mtab = readlink_e_mtab.ReadLinkEMtab(context_wrap(REAL_FILE_PATH))
    assert len(mtab.path) > 0
    assert mtab.path == REAL_FILE_PATH


def test_fail():
    with pytest.raises(SkipException) as e:
        readlink_e_mtab.ReadLinkEMtab(context_wrap(BAD_FILE_PATH))
    assert "No Data from command: readlink -e /etc/mtab" in str(e)
