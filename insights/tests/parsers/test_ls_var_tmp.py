import doctest

from insights.parsers import ls_var_tmp
from insights.parsers.ls_var_tmp import LsVarTmp
from insights.tests import context_wrap

LS_VAR_TMP = """
/var/tmp:
total 20
drwxr-xr-x.  2 0 0 4096 Mar 26 02:25 a1
drwxr-xr-x.  2 0 0 4096 Mar 26 02:25 a2
drwxr-xr-x.  3 0 0 4096 Apr  3 02:50 foreman-ssh-cmd-fc3f65c9-2b35-480d-87e3-1d971433d6ad
"""


def test_ls_var_tmp():
    ls_var_tmp = LsVarTmp(context_wrap(LS_VAR_TMP))
    assert ls_var_tmp.dirs_of('/var/tmp') == ['a1', 'a2', 'foreman-ssh-cmd-fc3f65c9-2b35-480d-87e3-1d971433d6ad']
    foreman = ls_var_tmp.dir_entry('/var/tmp', 'foreman-ssh-cmd-fc3f65c9-2b35-480d-87e3-1d971433d6ad')
    assert foreman is not None
    assert foreman == {
        'group': '0',
        'name': 'foreman-ssh-cmd-fc3f65c9-2b35-480d-87e3-1d971433d6ad',
        'links': 3,
        'perms': 'rwxr-xr-x.',
        'raw_entry': 'drwxr-xr-x.  3 0 0 4096 Apr  3 02:50 foreman-ssh-cmd-fc3f65c9-2b35-480d-87e3-1d971433d6ad',
        'owner': '0',
        'date': 'Apr  3 02:50',
        'type': 'd',
        'size': 4096,
        'dir': '/var/tmp'}


def test_ls_var_tmp_doc_examples():
    env = {
        'LsVarTmp': LsVarTmp,
        'ls_var_tmp': LsVarTmp(context_wrap(LS_VAR_TMP)),
    }
    failed, total = doctest.testmod(ls_var_tmp, globs=env)
    assert failed == 0
