import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import proc_keys
from insights.parsers.proc_keys import ProcKeys
from insights.tests import context_wrap

PROC_KEYS = """
009a2028 I--Q---   1 perm 3f010000  1000  1000 user     krb_ccache:primary: 12
1806c4ba I--Q---   1 perm 3f010000  1000  1000 keyring  _pid: 2
25d3a08f I--Q---   1 perm 1f3f0000  1000 65534 keyring  _uid_ses.1000: 1
28576bd8 I--Q---   3 perm 3f010000  1000  1000 keyring  _krb: 1
2c546d21 I--Q--- 190 perm 3f030000  1000  1000 keyring  _ses: 2
30a4e0be I------   4   2d 1f030000  1000 65534 keyring  _persistent.1000: 1
32100fab I--Q---   4 perm 1f3f0000  1000 65534 keyring  _uid.1000: 2
32a387ea I--Q---   1 perm 3f010000  1000  1000 keyring  _pid: 2
3ce56aea I--Q---   5 perm 3f030000  1000  1000 keyring  _ses: 1
""".strip()

PROC_KEYS_INVALID = """
unknow_case
""".strip()

PROC_KEYS_EMPTY = """
""".strip()


def test_etc_systemd():
    proc_keys_content = ProcKeys(context_wrap(PROC_KEYS))
    assert proc_keys_content[1]['id'] == '1806c4ba'
    assert proc_keys_content[1]['flags'] == 'I--Q---'
    assert proc_keys_content[1]['usage'] == '1'
    assert proc_keys_content[1]['timeout'] == 'perm'
    assert proc_keys_content[2]['permissions'] == '1f3f0000'
    assert proc_keys_content[2]['uid'] == '1000'
    assert proc_keys_content[2]['gid'] == '65534'
    assert proc_keys_content[2]['type'] == 'keyring'
    assert proc_keys_content[2]['description'] == '_uid_ses.1000: 1'

    assert proc_keys_content.search(timeout='perm')[0] == proc_keys_content[0]
    assert proc_keys_content.search(description__contains='pid')[0] == proc_keys_content[1]


def test_empty():
    with pytest.raises(SkipComponent) as e:
        ProcKeys(context_wrap(PROC_KEYS_EMPTY))
    assert 'No Contents' in str(e)

    with pytest.raises(SkipComponent) as e:
        ProcKeys(context_wrap(PROC_KEYS_INVALID))
    assert "Invalid Contents: unknow_case" in str(e)


def test_systemd_examples():
    env = {
        'proc_keys': ProcKeys(context_wrap(PROC_KEYS))
    }
    failed, total = doctest.testmod(proc_keys, globs=env)
    assert failed == 0
