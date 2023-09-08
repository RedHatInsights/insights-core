import doctest
from insights.parsers import sendmail
from insights.parsers.sendmail import SendmailMC
from insights.tests import context_wrap


SENDMAIL_MC_CONTENT = """
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
"""

SendmailMC.last_scan('confTO_CONNECT_line', 'confTO_CONNECT')


def test_sendmail_mc():
    sendmail_mc_obj = SendmailMC(context_wrap(SENDMAIL_MC_CONTENT))

    assert sendmail_mc_obj.confTO_CONNECT_line
    assert sendmail_mc_obj.confTO_CONNECT_line.get('raw_message') == "define(`confTO_CONNECT', `1m')dnl"


def test_doc():
    env = {
            'sendmail_mc_obj': SendmailMC(context_wrap(SENDMAIL_MC_CONTENT))
          }
    failures, _ = doctest.testmod(sendmail, globs=env)
    assert failures == 0
