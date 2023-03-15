import doctest
from insights.parsers import ls_rsyslog_errorfile
from insights.parsers.ls_rsyslog_errorfile import LsRsyslogErrorfile
from insights.tests import context_wrap

LS_RSYSLOG_ERRORFILE = """
-rwxr-xr-x.  1 0  0     2558 Apr 10  2019 /var/log/oversized.log
"""


def test_ls_rsyslog_errorfile():
    rsyslog_errorfile = LsRsyslogErrorfile(context_wrap(LS_RSYSLOG_ERRORFILE))
    assert len(rsyslog_errorfile.data) == 1
    assert rsyslog_errorfile.data.get('/var/log/oversized.log') == {'type': '-', 'perms': 'rwxr-xr-x.', 'links': 1, 'owner': '0', 'group': '0', 'size': 2558, 'date': 'Apr 10  2019', 'name': '/var/log/oversized.log', 'raw_entry': '-rwxr-xr-x.  1 0  0     2558 Apr 10  2019 /var/log/oversized.log', 'dir': ''}
    assert rsyslog_errorfile.data.get('/var/log/oversized.log').get('size') == 2558


def test_ls_rsyslog_errorfile_doc_examples():
    env = {
        'rsyslog_errorfile': LsRsyslogErrorfile(context_wrap(LS_RSYSLOG_ERRORFILE)),
    }
    failed, total = doctest.testmod(ls_rsyslog_errorfile, globs=env)
    assert failed == 0
