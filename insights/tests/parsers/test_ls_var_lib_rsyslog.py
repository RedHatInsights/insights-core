import doctest

from insights.parsers import ls_var_lib_rsyslog
from insights.tests import context_wrap


LS_VAR_LIB_RSYSLOG_1 = """
total 4
-rw-------. 1 root root system_u:object_r:syslogd_var_lib_t:s0 127 Nov 30 03:40 imjournal.state
"""

LS_VAR_LIB_RSYSLOG_2 = """
total 4
-rw-------. root root system_u:object_r:syslogd_var_lib_t:s0 imjournal.state
"""


def test_ls_var_lib_rsyslog():
    rsyslog_obj = ls_var_lib_rsyslog.LsVarLibRsyslog(context_wrap(LS_VAR_LIB_RSYSLOG_2, path="insights_commands/ls_-lZ_.var.lib.rsyslog"))
    assert rsyslog_obj.files_of('/var/lib/rsyslog') == ['imjournal.state']
    journal_obj = rsyslog_obj.dir_entry('/var/lib/rsyslog', 'imjournal.state')
    assert journal_obj is not None
    assert journal_obj['se_type'] == 'syslogd_var_lib_t'
    assert journal_obj['owner'] == 'root'


def test_ls_var_lib_pcp_doc_examples():
    env = {
        'rsyslog_obj': ls_var_lib_rsyslog.LsVarLibRsyslog(context_wrap(LS_VAR_LIB_RSYSLOG_1, path="insights_commands/ls_-lZ_.var.lib.rsyslog")),
    }
    failed, total = doctest.testmod(ls_var_lib_rsyslog, globs=env)
    assert failed == 0
