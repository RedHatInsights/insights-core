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
    """
    To make the examples readable, it's better to show one of the main usage "last_scan".
    And the last_scan should be called before the parser initialation.
    However, the initialization is done here, so the "last_scan" in the example won't work.
    As a result, it will rasise error when refering the result key.
    So we will not thest the examples, just show the users how to use it.
    """
    pass
