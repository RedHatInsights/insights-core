"""
FapolicydRules - file ``/etc/fapolicyd/rules.d/*.rules``
========================================================
"""

from insights import parser
from insights.core import TextFileOutput
from insights.specs import Specs


@parser(Specs.fapolicyd_rules)
class FapolicydRules(TextFileOutput):
    """
    Parse the content of ``/etc/fapolicyd/rules.d/*.rules`` file.

    .. note::

        The rules do not require to get the parsed result currently.
        It just need to check if it contains specific lines, so use
        :class:`insights.core.TextFileOutput` as the base class.

    Sample input::

        deny_audit perm=any pattern=ld_so : all
        deny_audit perm=any pattern=ld_preload : all

    Examples:
        >>> from insights.parsers.fapolicyd_rules import FapolicydRules
        >>> FapolicydRules.last_scan('ld_so_deny_audit_test', 'deny_audit perm=any pattern=ld_so : all')
        >>> type(fapolicyd_rules)
        <class 'insights.parsers.fapolicyd_rules.FapolicydRules'>
        >>> fapolicyd_rules.ld_so_deny_audit_test.get('raw_line')
        'deny_audit perm=any pattern=ld_so : all'
    """
    pass
