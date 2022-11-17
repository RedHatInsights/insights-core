import doctest

from insights.parsers import ls_var_lib_pcp
from insights.parsers.ls_var_lib_pcp import LsVarLibPcp
from insights.tests import context_wrap

LS_VAR_LIB_PCP = """
total 16
drwxr-xr-x.  4 root root  33 Dec 15 08:12 .
drwxr-xr-x. 20 root root 278 Dec 15 08:12 ..
drwxr-xr-x.  2 root root   6 Oct  3 09:37 pmcd
drwxr-xr-x.  2 root root   6 Oct  3 09:37 pmie
drwxrwxr-x.  4 root root 128 Aug 22 17:55 pmdas
"""


def test_ls_var_lib_pcp():
    ls_var_lib_pcp = LsVarLibPcp(context_wrap(LS_VAR_LIB_PCP, path="insights_commands/ls_-la_.var.lib.pcp"))
    assert ls_var_lib_pcp.dirs_of('/var/lib/pcp') == ['.', '..', 'pmcd', 'pmie', 'pmdas']
    journal = ls_var_lib_pcp.dir_entry('/var/lib/pcp', 'pmdas')
    assert journal is not None


def test_ls_var_lib_pcp_doc_examples():
    env = {
        'ls_var_lib_pcp': LsVarLibPcp(context_wrap(LS_VAR_LIB_PCP, path="insights_commands/ls_-la_.var.lib.pcp")),
    }
    failed, total = doctest.testmod(ls_var_lib_pcp, globs=env)
    assert failed == 0
