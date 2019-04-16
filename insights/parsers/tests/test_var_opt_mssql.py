import doctest
import pytest
from insights.parsers import SkipException
from insights.parsers import var_opt_mssql
from insights.tests import context_wrap

VAR_OPT_MSSQL_WRONG_PERM = """
{"owner": "root", "group": "root"}
""".strip()

VAR_OPT_MSSQL_WRONG_PERM_2 = """
{"owner": "root", "group": "mssql"}
""".strip()


def test_var_opt_mssql():
    incorrect_ownership = var_opt_mssql.BadOwnershipOfVarOptMSSql(context_wrap(VAR_OPT_MSSQL_WRONG_PERM))
    assert incorrect_ownership.data.get('owner') != "mssql"
    assert incorrect_ownership.data.get('group') != "mssql"

    incorrect_ownership = var_opt_mssql.BadOwnershipOfVarOptMSSql(context_wrap(VAR_OPT_MSSQL_WRONG_PERM_2))
    assert incorrect_ownership.data.get('owner') != "mssql"
    assert incorrect_ownership.data.get('group') == "mssql"


def test_no_data():
    with pytest.raises(SkipException) as ex:
        var_opt_mssql.BadOwnershipOfVarOptMSSql(context_wrap(''))
    assert 'Correct ownership of /var/opt/mssql.' in str(ex)


def test_var_opt_mssql_docs():
    failed_count, tests = doctest.testmod(
        var_opt_mssql,
        globs={'var_opt_mssql': var_opt_mssql.BadOwnershipOfVarOptMSSql(context_wrap(VAR_OPT_MSSQL_WRONG_PERM))}
    )
    assert failed_count == 0
