"""
FapolicydRules - file ``/etc/fapolicyd/rules.d/*.rules``
========================================================
"""

from insights import parser
from insights.core import LogFileOutput
from insights.specs import Specs


@parser(Specs.fapolicyd_rules)
class FapolicydRules(LogFileOutput):
    """
    Parse the content of ``/etc/fapolicyd/rules.d/*.rules`` file.

    Sample input::

        deny_audit perm=any pattern=ld_so : all
        deny_audit perm=any pattern=ld_preload : all

    Examples:
        >>> type(fapolicyd_rules)
        <class 'insights.parsers.fapolicyd_rules.FapolicydRules'>
        >>> fapolicyd_rules.ld_so_deny_audit_test.get('raw_message')
        'deny_audit perm=any pattern=ld_so : all'
    """
    pass
