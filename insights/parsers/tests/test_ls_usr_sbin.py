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

from insights.core.filters import add_filter
from insights.parsers import ls_usr_sbin
from insights.parsers.ls_usr_sbin import LsUsrSbin
from insights.specs import Specs
from insights.tests import context_wrap

LS_USR_SBIN = """
total 41472
-rwxr-xr-x. 1 0  0   11720 Mar 18  2014 accessdb
-rwxr-xr-x. 1 0  0    3126 Oct  4  2013 addgnupghome
-rwxr-xr-x. 1 0  0   20112 Jun  1  2017 addpart
-rwxr-xr-x. 1 0  0  371912 Jan 27  2014 postconf
-rwxr-sr-x. 1 0 90  218552 Jan 27  2014 postdrop
"""


def test_ls_usr_sbin():
    ls_usr_sbin = LsUsrSbin(context_wrap(LS_USR_SBIN, path='insights_commands/ls_-ln_.usr.sbin'))
    assert ls_usr_sbin.files_of('/usr/sbin') == ['accessdb', 'addgnupghome', 'addpart', 'postconf', 'postdrop']
    postdrop = ls_usr_sbin.dir_entry('/usr/sbin', 'postdrop')
    assert postdrop is not None
    assert postdrop == {
        'group': '90',
        'name': 'postdrop',
        'links': 1,
        'perms': 'rwxr-sr-x.',
        'raw_entry': '-rwxr-sr-x. 1 0 90  218552 Jan 27  2014 postdrop',
        'owner': '0',
        'date': 'Jan 27  2014',
        'type': '-',
        'size': 218552,
        'dir': '/usr/sbin'}


def test_ls_usr_sbin_doc_examples():
    env = {
        'Specs': Specs,
        'add_filter': add_filter,
        'LsUsrSbin': LsUsrSbin,
        'ls_usr_sbin': LsUsrSbin(context_wrap(LS_USR_SBIN, path='insights_commands/ls_-ln_.usr.sbin')),
    }
    failed, total = doctest.testmod(ls_usr_sbin, globs=env)
    assert failed == 0
