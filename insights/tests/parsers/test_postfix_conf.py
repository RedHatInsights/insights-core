from insights.core.exceptions import SkipComponent
from insights.parsers import postfix_conf
from insights.parsers.postfix_conf import PostfixMaster
from insights.tests import context_wrap
import doctest
import pytest

POSTFIXMASTER = """
# ==========================================================================
# service type  private unpriv  chroot  wakeup  maxproc command + args
#               (yes)   (yes)   (no)    (never) (100)
# ==========================================================================
smtp      inet  n       -       n       -       -       smtpd
#smtp      inet  n       -       n       -       1       postscreen
pickup    unix  n       -       n       60      1       pickup
cleanup   unix  n       -       n       -       0       cleanup
qmgr      unix  n       -       n       300     1       qmgr
#qmgr     unix  n       -       n       300     1       oqmgr
tlsmgr    unix  -       -       n       1000?   1       tlsmgr
rewrite   unix  -       -       n       -       -       trivial-rewrite
bounce    unix  -       -       n       -       0       bounce
defer     unix  -       -       n       -       0       bounce
trace     unix  -       -       n       -       0       bounce
verify    unix  -       -       n       -       1       verify
flush     unix  n       -       n       1000?   0       flush
proxymap  unix  -       -       n       -       -       proxymap
proxywrite unix -       -       n       -       1       proxymap
smtp      unix  -       -       n       -       -       smtp
submission inet n       -       n       -       -       smtpd
  -o syslog_name=postfix/submission
  -o smtpd_tls_security_level=encrypt
  -o smtpd_sasl_auth_enable=yes
  -o smtpd_tls_auth_only=yes
  -o smtpd_reject_unlisted_recipient=no
  -o smtpd_client_restrictions=$mua_client_restrictions
  -o smtpd_helo_restrictions=$mua_helo_restrictions
  -o smtpd_sender_restrictions=$mua_sender_restrictions
  -o smtpd_recipient_restrictions=
  -o smtpd_relay_restrictions=permit_sasl_authenticated,reject
  -o milter_macro_daemon_name=ORIGINATING
relay     unix  -       -       n       -       -       smtp
        -o syslog_name=postfix/$service_name
#       -o smtp_helo_timeout=5 -o smtp_connect_timeout=5
showq     unix  n       -       n       -       -       showq
error     unix  -       -       n       -       -       error
retry     unix  -       -       n       -       -       error
discard   unix  -       -       n       -       -       discard
local     unix  -       n       n       -       -       local
virtual   unix  -       n       n       -       -       virtual
lmtp      unix  -       -       n       -       -       lmtp
anvil     unix  -       -       n       -       1       anvil
mailman   unix  -       n       n       -       -       pipe
  flags=FRX user=list argv=/usr/lib/mailman/bin/postfix-to-mailman.py
  ${nexthop} ${user}
""".strip()

POSTFIXMASTER_ERR = """
""".strip()

POSTFIXMASTER_DOC = """
# ==========================================================================
# service type  private unpriv  chroot  wakeup  maxproc command + args
#               (yes)   (yes)   (no)    (never) (100)
# ==========================================================================
smtp      inet  n       -       n       -       -       smtpd
pickup    unix  n       -       n       60      1       pickup
cleanup   unix  n       -       n       -       0       cleanup
qmgr      unix  n       -       n       300     1       qmgr
#qmgr     unix  n       -       n       300     1       oqmgr
tlsmgr    unix  -       -       n       1000?   1       tlsmgr
rewrite   unix  -       -       n       -       -       trivial-rewrite
bounce    unix  -       -       n       -       0       bounce
defer     unix  -       -       n       -       0       bounce
trace     unix  -       -       n       -       0       bounce
verify    unix  -       -       n       -       1       verify
flush     unix  n       -       n       1000?   0       flush
proxymap  unix  -       -       n       -       -       proxymap
proxywrite unix -       -       n       -       1       proxymap
smtp      unix  -       -       n       -       -       smtp
relay     unix  -       -       n       -       -       smtp
        -o syslog_name=postfix/$service_name
#       -o smtp_helo_timeout=5 -o smtp_connect_timeout=5
showq     unix  n       -       n       -       -       showq
error     unix  -       -       n       -       -       error
retry     unix  -       -       n       -       -       error
discard   unix  -       -       n       -       -       discard
local     unix  -       n       n       -       -       local
virtual   unix  -       n       n       -       -       virtual
lmtp      unix  -       -       n       -       -       lmtp
anvil     unix  -       -       n       -       1       anvil
scache    unix  -       -       n       -       1       scache
""".strip()


def test_postfix_master():
    results = PostfixMaster(context_wrap(POSTFIXMASTER))
    assert len(results) == 25
    assert results[0]['service'] == 'smtp'
    assert results[0]['type'] == 'inet'
    assert results[0]['private'] == 'n'
    assert results[0]['command'] == 'smtpd'
    assert results[14]['args'] == ['-o syslog_name=postfix/submission',
                                        '-o smtpd_tls_security_level=encrypt',
                                        '-o smtpd_sasl_auth_enable=yes',
                                        '-o smtpd_tls_auth_only=yes',
                                        '-o smtpd_reject_unlisted_recipient=no',
                                        '-o smtpd_client_restrictions=$mua_client_restrictions',
                                        '-o smtpd_helo_restrictions=$mua_helo_restrictions',
                                        '-o smtpd_sender_restrictions=$mua_sender_restrictions',
                                        '-o smtpd_recipient_restrictions=',
                                        '-o smtpd_relay_restrictions=permit_sasl_authenticated,reject',
                                        '-o milter_macro_daemon_name=ORIGINATING']
    assert results[-1] == {'service': 'mailman', 'type': 'unix', 'private': '-', 'unpriv': 'n', 'chroot': 'n', 'wakeup': '-', 'maxproc': '-', 'command': 'pipe', 'args': ['flags=FRX user=list argv=/usr/lib/mailman/bin/postfix-to-mailman.py', '${nexthop} ${user}']}


def test_postfix_master_err():
    with pytest.raises(SkipComponent):
        postfix_conf.PostfixMaster(context_wrap(POSTFIXMASTER_ERR))


def test_postfix_master_doc_examples():
    env = {
        'postfix_master': PostfixMaster(context_wrap(POSTFIXMASTER_DOC))
    }
    failed, total = doctest.testmod(postfix_conf, globs=env)
    assert failed == 0
