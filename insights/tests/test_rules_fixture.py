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

from insights.core.plugins import make_pass, make_fail
from insights.specs import Specs
from insights.plugins import rules_fixture_plugin


UNAME = {
    'spec': Specs.uname,
    'data': """
Linux testbox.redhat.com 2.6.32-642.el6.x86_64 #1 SMP Tue Sep 16 01:56:35 EDT 2014 x86_64 x86_64 x86_64 GNU/Linux
""".strip()
}
RPMS = {
    'spec': Specs.installed_rpms,
    'path': '/etc/yum.repos.d/stuff',
    'data': """
kernel-2.6.32-573.el6.x86_64
bash-4.1.23-6.fc29.x86_64
rh-nginx112-nginx-1.12.1-2.el7.x86_64
""".strip()
}


def test_rules_fixture(run_rule):
    input_data = [UNAME, RPMS]
    expected = make_pass('PASS', bash_ver='bash-4.1.23-6.fc29', uname_ver='2.6.32')
    results = run_rule('test_pass', rules_fixture_plugin.report, input_data)
    assert results == expected

    input_data = [RPMS]
    expected = make_fail('FAIL', bash_ver='bash-4.1.23-6.fc29', path=RPMS['path'])
    results = run_rule('test_fail_list', rules_fixture_plugin.report, input_data)
    assert results == expected

    input_data = RPMS
    expected = make_fail('FAIL', bash_ver='bash-4.1.23-6.fc29', path=RPMS['path'])
    results = run_rule('test_fail_dict', rules_fixture_plugin.report, input_data)
    assert results == expected

    input_data = []
    expected = None
    results = run_rule('test_ret_none', rules_fixture_plugin.report, input_data)
    assert results == expected
