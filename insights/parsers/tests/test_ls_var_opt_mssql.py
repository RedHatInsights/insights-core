#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import doctest
from insights.parsers import ls_var_opt_mssql
from insights.tests import context_wrap


LS_VAR_OPT_MSSQL_WRONG_PERM = """
drwxrwx---. 5 root root 58 Apr 16 07:20 /var/opt/mssql
""".strip()

LS_VAR_OPT_MSSQL_WRONG_PERM_2 = """
drwxrwx---. 5 mssql root 58 Apr 16 07:20 /var/opt/mssql
""".strip()

LS_VAR_OPT_MSSQL = """
drwxrwx---. 5 mssql mssql 58 Apr 16 07:20 /var/opt/mssql
""".strip()


def test_ls_var_opt_mssql():
    content = ls_var_opt_mssql.LsDVarOptMSSql(context_wrap(LS_VAR_OPT_MSSQL_WRONG_PERM, path='ls_-ld_.var.opt.mssql'))
    content_attr = content.listing_of('/var/opt/mssql').get('/var/opt/mssql')
    assert content_attr.get('owner') != "mssql"
    assert content_attr.get('group') != "mssql"

    content = ls_var_opt_mssql.LsDVarOptMSSql(context_wrap(LS_VAR_OPT_MSSQL_WRONG_PERM_2, path='ls_-ld_.var.opt.mssql'))
    content_attr = content.listing_of('/var/opt/mssql').get('/var/opt/mssql')
    assert content_attr.get('owner') == "mssql"
    assert content_attr.get('group') != "mssql"

    content = ls_var_opt_mssql.LsDVarOptMSSql(context_wrap(LS_VAR_OPT_MSSQL, path='ls_-ld_.var.opt.mssql'))
    content_attr = content.listing_of('/var/opt/mssql').get('/var/opt/mssql')
    assert content_attr.get('owner') == "mssql"
    assert content_attr.get('group') == "mssql"


def _failed_without_insights_command_as_path():
    # Fails with KeyError: '/var/opt/mssql'" unless path is defined
    foo = ls_var_opt_mssql.LsDVarOptMSSql(context_wrap(LS_VAR_OPT_MSSQL_WRONG_PERM_2))
    content_attr = foo.listing_of('/var/opt/mssql').get('/var/opt/mssql')
    assert content_attr.get('owner') != "mssql"
    assert content_attr.get('group') != "mssql"


def _failed_with_standard_path():
    # Fails with KeyError: '/var/opt/mssql'".
    bar = ls_var_opt_mssql.LsDVarOptMSSql(context_wrap(LS_VAR_OPT_MSSQL_WRONG_PERM_2, path='/var/opt/mssql'))
    content_attr = bar.listing_of('/var/opt/mssql').get('/var/opt/mssql')
    assert content_attr.get('owner') != "mssql"
    assert content_attr.get('group') != "mssql"


def test_ls_var_opt_mssql_docs():
    failed_count, tests = doctest.testmod(
        ls_var_opt_mssql,
        globs={'content': ls_var_opt_mssql.LsDVarOptMSSql(context_wrap(LS_VAR_OPT_MSSQL_WRONG_PERM, path='ls_-ld_.var.opt.mssql'))}
    )
    assert failed_count == 0
