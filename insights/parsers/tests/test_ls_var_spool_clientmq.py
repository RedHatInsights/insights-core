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

from insights.parsers import ls_var_spool_clientmq
from insights.parsers.ls_var_spool_clientmq import LsVarSpoolClientmq
from insights.tests import context_wrap

LS_VAR_SPOOL_CLIENTMQ = """
total 40
-rw-rw---- 1 51 51   4 Jul 11 02:32 dfw6B6Wilr002718
-rw-rw---- 1 51 51   4 Jul 11 02:32 dfw6B6WixJ002715
-rw-rw---- 1 51 51   4 Jul 11 02:32 dfw6B6WjP6002721
-rw-rw---- 1 51 51 817 Jul 11 03:35 dfw6B7Z8BB002906
-rw-rw---- 1 51 51 817 Jul 11 04:02 dfw6B822T0011150
"""


def test_ls_var_spool_clientmq():
    ls_var_spool_clientmq = LsVarSpoolClientmq(context_wrap(LS_VAR_SPOOL_CLIENTMQ, path='insights_commands/ls_-ln_.var.spool.clientmqueue'))
    assert ls_var_spool_clientmq.files_of('/var/spool/clientmqueue') == ['dfw6B6Wilr002718', 'dfw6B6WixJ002715', 'dfw6B6WjP6002721', 'dfw6B7Z8BB002906', 'dfw6B822T0011150']
    onemail = ls_var_spool_clientmq.dir_entry('/var/spool/clientmqueue', 'dfw6B6Wilr002718')
    assert onemail is not None
    assert onemail == {'group': '51', 'name': 'dfw6B6Wilr002718', 'links': 1, 'perms': 'rw-rw----', 'raw_entry': '-rw-rw---- 1 51 51   4 Jul 11 02:32 dfw6B6Wilr002718', 'owner': '51', 'date': 'Jul 11 02:32', 'type': '-', 'dir': '/var/spool/clientmqueue', 'size': 4}


def test_ls_var_spool_clientmq_doc_examples():
    env = {
        'LsVarSpoolClientmq': LsVarSpoolClientmq,
        'ls_var_spool_clientmq': LsVarSpoolClientmq(context_wrap(LS_VAR_SPOOL_CLIENTMQ, path='insights_commands/ls_-ln_.var.spool.clientmqueue')),
    }
    failed, total = doctest.testmod(ls_var_spool_clientmq, globs=env)
    assert failed == 0
