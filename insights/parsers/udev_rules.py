"""
UdevRules - file ``/usr/lib/udev/rules.d/``
===========================================

The parsers included in this module are:

UdevRulesFCWWPN - file ``/usr/lib/udev/rules.d/59-fc-wwpn-id.rules``
--------------------------------------------------------------------

UdevRules40Redhat - files ``/etc/udev/rules.d/40-redhat.rules``, ``/run/udev/rules.d/40-redhat.rules``, ``/usr/lib/udev/rules.d/40-redhat.rules``, ``/usr/local/lib/udev/rules.d/40-redhat.rules``
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
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


@parser(Specs.udev_40_redhat_rules)
class UdevRules40Redhat(LogFileOutput):
    """
    Read the content of ``40-redhat.rules`` file.

    .. note::

        The syntax of the `.rules` file is complex, and no rules require to
        get the serialized parsed result currently.  An only existing rule's
        supposed to check the syntax of some specific line, so here the
        :class:`insights.core.LogFileOutput` is the base class.

    Sample input::

        # do not edit this file, it will be overwritten on update
        # CPU hotadd request
        SUBSYSTEM=="cpu", ACTION=="add", TEST=="online", ATTR{online}=="0", ATTR{online}="1"

        # Memory hotadd request
        SUBSYSTEM!="memory", ACTION!="add", GOTO="memory_hotplug_end"
        PROGRAM="/bin/uname -p", RESULT=="s390*", GOTO="memory_hotplug_end"

        LABEL="memory_hotplug_end"

    Examples:
        >>> 'LABEL="memory_hotplug_end"' in udev_40_redhat_rules.lines
        True
    """
    pass
