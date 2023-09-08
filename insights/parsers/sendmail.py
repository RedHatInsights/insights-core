"""
Sendmail Commands and Files
===========================

This module contains the following parsers:

SendmailMC - file ``/etc/mail/sendmail.mc``
-------------------------------------------
"""

from insights.specs import Specs
from insights import parser
from insights.core import LogFileOutput


@parser(Specs.sendmail_mc)
class SendmailMC(LogFileOutput):
    """
    Class for parsing ``/etc/mail/sendmail.mc`` file.

    Sample Input::

        define(`confDEF_USER_ID', ``8:12'')dnl
        dnl define(`confAUTO_REBUILD')dnl
        define(`confTO_CONNECT', `1m')dnl
        define(`confTRY_NULL_MX_LIST', `True')dnl
        define(`confDONT_PROBE_INTERFACES', `True')dnl
        define(`PROCMAIL_MAILER_PATH', `/usr/bin/procmail')dnl
        define(`ALIAS_FILE', `/etc/aliases')dnl
        define(`STATUS_FILE', `/var/log/mail/statistics')dnl
        define(`UUCP_MAILER_MAX', `2000000')dnl
        define(`confUSERDB_SPEC', `/etc/mail/userdb.db')dnl
        define(`confPRIVACY_FLAGS', `authwarnings,novrfy,noexpn,restrictqrun')dnl
        define(`confAUTH_OPTIONS', `A')dnl

    Examples:
        >>> from insights.core.filters import add_filter
        >>> from insights.specs import Specs
        >>> add_filter(Specs.sendmail_mc, 'confTRY_NULL_MX_LIST')
        >>> type(sendmail_mc_obj)
        <class 'insights.parsers.sendmail.SendmailMC'>
        >>> sendmail_mc_obj.last_scan("null_mx_list_line", "confTRY_NULL_MX_LIST")
    """
    time_format = None
