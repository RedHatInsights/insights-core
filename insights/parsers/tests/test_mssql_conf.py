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
from insights.parsers import mssql_conf
from insights.tests import context_wrap

MSSQL_CONF = """
[sqlagent]
enabled = false

[EULA]
accepteula = Y

[memory]
memorylimitmb = 3328
""".strip()


def test_mssql_conf():
    conf = mssql_conf.MsSQLConf(context_wrap(MSSQL_CONF))
    assert conf.has_option('memory', 'memorylimitmb') is True
    assert conf.get('memory', 'memorylimitmb') == '3328'


def test_documentation():
    env = {'conf': mssql_conf.MsSQLConf(context_wrap(MSSQL_CONF))}
    failed_count, tests = doctest.testmod(mssql_conf, globs=env)
    assert failed_count == 0
