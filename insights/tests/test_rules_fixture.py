from insights.core.plugins import make_pass, make_fail
from insights.specs import Specs
from insights.plugins import rules_fixture_plugin
from insights.tests import InputData


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
    input_data = InputData('test_pass')
    input_data.add(UNAME['spec'], UNAME['data'])
    input_data.add(RPMS['spec'], RPMS['data'], path=RPMS['path'])
    expected = make_pass('PASS', bash_ver='bash-4.1.23-6.fc29', uname_ver='2.6.32')
    results = run_rule(rules_fixture_plugin.report, input_data)
    assert results == expected

    input_data = InputData('test_fail')
    input_data.add(RPMS['spec'], RPMS['data'], path=RPMS['path'])
    expected = make_fail('FAIL', bash_ver='bash-4.1.23-6.fc29', path=RPMS['path'])
    results = run_rule(rules_fixture_plugin.report, input_data)
    assert results == expected

    input_data = InputData('test_ret_none')
    results = run_rule(rules_fixture_plugin.report, input_data)
    assert results is None
