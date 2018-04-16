import doctest

from insights.parsers import ls_var_tmp
from insights.parsers.ls_var_tmp import LsVarTmp
from insights.tests import context_wrap

LS_VAR_TMP = """
/var/tmp:
total 20
drwxrwxrwt.  5 0 0 4096 Apr 28  2018 .
drwxr-xr-x. 24 0 0 4096 Oct 15  2015 ..
drwxr-xr-x.  2 0 0 4096 Mar 26 02:25 a1
drwxr-xr-x.  2 0 0 4096 Mar 26 02:25 a2
drwxr-xr-x.  3 0 0 4096 Apr  3 02:50 foreman-ssh-cmd-fc3f65c9-2b35-480d-87e3-1d971433d6ad

/var/tmp/a1:
total 8
drwxr-xr-x. 2 0 0 4096 Mar 26 02:25 .
drwxrwxrwt. 5 0 0 4096 Apr 28  2018 ..

/var/tmp/a2:
total 8
drwxr-xr-x. 2 0 0 4096 Mar 26 02:25 .
drwxrwxrwt. 5 0 0 4096 Apr 28  2018 ..

/var/tmp/foreman-ssh-cmd-fc3f65c9-2b35-480d-87e3-1d971433d6ad:
total 36
drwxr-xr-x. 3 0 0  4096 Apr  3 02:50 .
drwxrwxrwt. 5 0 0  4096 Apr 28  2018 ..
drwxr-xr-x. 2 0 0  4096 Apr  3 02:50 dir1
-rw-r--r--. 1 0 0     2 Apr 28  2018 exit_code
-rw-r--r--. 1 0 0 15606 Apr 28  2018 output
-rwxr-xr-x. 1 0 0    14 Apr 28  2018 script
-rw-r--r--. 1 0 0     0 Apr  3 02:50 test

/var/tmp/foreman-ssh-cmd-fc3f65c9-2b35-480d-87e3-1d971433d6ad/dir1:
total 8
drwxr-xr-x. 2 0 0 4096 Apr  3 02:50 .
drwxr-xr-x. 3 0 0 4096 Apr  3 02:50 ..
"""


def test_ls_var_tmp():
    ls_var_tmp = LsVarTmp(context_wrap(LS_VAR_TMP))
    assert "/var/tmp/foreman-ssh-cmd-fc3f65c9-2b35-480d-87e3-1d971433d6ad" in ls_var_tmp
    assert len(ls_var_tmp.files_of("/var/tmp/foreman-ssh-cmd-fc3f65c9-2b35-480d-87e3-1d971433d6ad")) == 4
    assert ls_var_tmp.files_of("/var/tmp/foreman-ssh-cmd-fc3f65c9-2b35-480d-87e3-1d971433d6ad") == ['exit_code', 'output', 'script', 'test']
    assert ls_var_tmp.dirs_of("/var/tmp/foreman-ssh-cmd-fc3f65c9-2b35-480d-87e3-1d971433d6ad") == ['.', '..', 'dir1']
    assert ls_var_tmp.total_of("/var/tmp/foreman-ssh-cmd-fc3f65c9-2b35-480d-87e3-1d971433d6ad") == 36
    foreman = ls_var_tmp.dir_entry("/var/tmp", "foreman-ssh-cmd-fc3f65c9-2b35-480d-87e3-1d971433d6ad")
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
