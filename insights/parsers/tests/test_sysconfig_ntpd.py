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

from insights.tests import context_wrap
from insights.parsers.sysconfig import NtpdSysconfig

NTPD = """
OPTIONS="-x -g"
#HIDE="me"
""".strip()


def test_sysconfig_ntpd():
    result = NtpdSysconfig(context_wrap(NTPD))
    assert result['OPTIONS'] == '-x -g'
    assert result.get('HIDE') is None
