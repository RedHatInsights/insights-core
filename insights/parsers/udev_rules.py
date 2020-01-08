"""
UdevRulesFCWWPN - file ``/usr/lib/udev/rules.d/59-fc-wwpn-id.rules``
====================================================================

The parser UdevRulesFCWWPN returns the content of the file "/usr/lib/udev/rules.d/59-fc-wwpn-id.rules"

Examples:

    >>> type(udev_rules)
    <class 'insights.parsers.udev_rules.UdevRules'>
    >>> 'ENV{FC_TARGET_WWPN}!="$*"; GOTO="fc_wwpn_end"' in udev_rules.lines
    True
"""
from insights import parser
from insights.core import LogFileOutput
from insights.specs import Specs


@parser(Specs.udev_fc_wwpn_id_rules)
class UdevRulesFCWWPN(LogFileOutput):
    """
    Parse data from the ``/usr/lib/udev/rules.d/59-fc-wwpn-id.rules`` file.
    For current rule, we just need to check if there is wrong syntax in this file, and don't need to
    parse the content, so we use LogFileOutput here.
    """
    pass
