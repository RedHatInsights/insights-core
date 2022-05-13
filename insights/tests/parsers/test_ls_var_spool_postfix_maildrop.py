import doctest

from insights.parsers import ls_var_spool_postfix_maildrop
from insights.parsers.ls_var_spool_postfix_maildrop import LsVarSpoolPostfixMaildrop
from insights.tests import context_wrap

LS_VAR_SPOOL_POSTFIX_MAILDROP = """
total 20
-rwxr--r--. 1 0 90 258 Jul 11 15:54 55D6821C286
-rwxr--r--. 1 0 90 282 Jul 11 15:54 5852121C284
-rwxr--r--. 1 0 90 258 Jul 11 15:54 9FFEC21C287
-rwxr--r--. 1 0 90 258 Jul 11 15:54 E9A4521C285
-rwxr--r--. 1 0 90 258 Jul 11 15:54 EA60F21C288
"""


def test_ls_var_spool_postfix_maildrop():
    ls_var_spool_postfix_maildrop = LsVarSpoolPostfixMaildrop(context_wrap(LS_VAR_SPOOL_POSTFIX_MAILDROP, path='nsights_commands/ls_-ln_.var.spool.postfix.maildrop'))
    assert ls_var_spool_postfix_maildrop.files_of('/var/spool/postfix/maildrop') == ['55D6821C286', '5852121C284', '9FFEC21C287', 'E9A4521C285', 'EA60F21C288']


def test_ls_var_spool_postfix_maildrop_doc_examples():
    env = {
        'LsVarSpoolPostfixMaildrop': LsVarSpoolPostfixMaildrop,
        'ls_var_spool_postfix_maildrop': LsVarSpoolPostfixMaildrop(context_wrap(LS_VAR_SPOOL_POSTFIX_MAILDROP, path='nsights_commands/ls_-ln_.var.spool.postfix.maildrop')),
    }
    failed, total = doctest.testmod(ls_var_spool_postfix_maildrop, globs=env)
    assert failed == 0
