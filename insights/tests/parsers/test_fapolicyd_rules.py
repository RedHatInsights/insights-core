import doctest
from insights.parsers import fapolicyd_rules
from insights.parsers.fapolicyd_rules import FapolicydRules
from insights.tests import context_wrap

CONTENT = """
# This file contains the list of all patterns. Only the ld_so pattern
# is enabled by default.

deny_audit perm=any pattern=ld_so : all
#deny_audit perm=any pattern=ld_preload : all
#deny_audit perm=any pattern=static : all
"""


def test_udev_rules():
    FapolicydRules.last_scan('test_deny_audit_lo_so1', 'deny_audit perm=any pattern=ld_so : all')
    result = FapolicydRules(context_wrap(CONTENT, path='/etc/fapolicyd/rules.d/30-patterns.rules'))
    assert result.test_deny_audit_lo_so1.get('raw_message') == 'deny_audit perm=any pattern=ld_so : all'


def test_doc():
    FapolicydRules.last_scan('ld_so_deny_audit_test', 'deny_audit perm=any pattern=ld_so : all')
    env = {'fapolicyd_rules': FapolicydRules(context_wrap(CONTENT, path='/etc/fapolicyd/rules.d/30-patterns.rules'))}
    failed, total = doctest.testmod(fapolicyd_rules, globs=env)
    assert failed == 0
