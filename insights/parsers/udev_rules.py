"""
UdevRules - file ``/usr/lib/udev/rules.d/``
===========================================

The parsers included in this module are:

UdevRulesFCWWPN - file ``/usr/lib/udev/rules.d/59-fc-wwpn-id.rules``
--------------------------------------------------------------------
"""
from insights import parser
from insights.core import LogFileOutput
from insights.specs import Specs


@parser(Specs.udev_fc_wwpn_id_rules)
class UdevRulesFCWWPN(LogFileOutput):
    """
    Read the content of ``/usr/lib/udev/rules.d/59-fc-wwpn-id.rules`` file.

    .. note::

        The syntax of the `.rules` file is complex, and no rules require to
        get the serialized parsed result currently.  An only existing rule's
        supposed to check the syntax of some specific line, so here the
        :class:`insights.core.LogFileOutput` is the base class.

    Examples:
        >>> type(udev_rules)
        <class 'insights.parsers.udev_rules.UdevRulesFCWWPN'>
        >>> 'ENV{FC_TARGET_WWPN}!="$*"; GOTO="fc_wwpn_end"' in udev_rules.lines
        True
    """
    pass
