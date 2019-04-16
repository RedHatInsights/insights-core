import doctest

from insights.parsers import ls_var_opt_mssql
from insights.tests import context_wrap

LS_VAR_OPT_MSSQL_WRONG_PERM = """
/var/opt/mssql:
total 0
drwxr-xr-x. 2 root root  6 Apr 16 09:42 .
drwxr-xr-x. 3 root root 19 Apr 16 09:42 ..
""".strip()

LS_VAR_OPT_MSSQL = """
/var/opt/mssql:
total 0
drwxr-xr-x. 2 mssql mssql  6 Apr 16 09:42 .
drwxr-xr-x. 3 root  root  19 Apr 16 09:42 ..
""".strip()


def test_ls_var_opt_mssql():
    incorrect_ownership = ls_var_opt_mssql.LsVarOptMSSql(context_wrap(LS_VAR_OPT_MSSQL_WRONG_PERM))
    listing_of_var_opt_mssql = incorrect_ownership.listing_of("/var/opt/mssql").get(".")
    assert listing_of_var_opt_mssql.get('owner') != "mssql"
    assert listing_of_var_opt_mssql.get('group') != "mssql"

    correct_ownership = ls_var_opt_mssql.LsVarOptMSSql(context_wrap(LS_VAR_OPT_MSSQL))
    listing_of_var_opt_mssql = correct_ownership.listing_of("/var/opt/mssql").get(".")
    assert listing_of_var_opt_mssql.get('owner') == "mssql"
    assert listing_of_var_opt_mssql.get('group') == "mssql"


def test_ls_var_opt_mssql_docs():
    failed_count, tests = doctest.testmod(
        ls_var_opt_mssql,
        globs={'ls_var_opt_mssql': ls_var_opt_mssql.LsVarOptMSSql(context_wrap(LS_VAR_OPT_MSSQL))}
    )
    assert failed_count == 0
