from insights.core.exceptions import ParseException
from insights.parsers import ls_rsyslog_errorfile
from insights.parsers.ls_rsyslog_errorfile import LsRsyslogErrorfile
from insights.tests import context_wrap
import doctest
import pytest

LS_RSYSLOG_ERRORFILE = """
/bin/ls: cannot access '/var/log/rsyslog/es-errors2.log': No such file or directory
/bin/ls: cannot access '/var/log/rsyslog/es-errors3.log': No such file or directory
-rw-r--r--. 1 0 0   9 Mar 15 17:16 /var/log/omelasticsearch.log
-rw-r--r--. 1 0 0 176 Mar 22 15:10 /var/log/rsyslog/es-errors1.log
"""

LS_RSYSLOG_ERRORFILE_ERROR = """
/bin/ls: cannot access '/var/log/omelasticsearch.log': No such file or directory
/bin/ls: cannot access '/var/log/rsyslog/es-errors1.log': No such file or directory
/bin/ls: cannot access '/var/log/rsyslog/es-errors2.log': No such file or directory
/bin/ls: cannot access '/var/log/rsyslog/es-errors3.log': No such file or directory
"""


def test_ls_rsyslog_errorfile():
    rsyslog_errorfile = LsRsyslogErrorfile(context_wrap(LS_RSYSLOG_ERRORFILE))
    assert len(rsyslog_errorfile.entries) == 2
    assert rsyslog_errorfile.entries.get('/var/log/omelasticsearch.log') == {'type': '-', 'perms': 'rw-r--r--.', 'links': 1, 'owner': '0', 'group': '0', 'size': 9, 'date': 'Mar 15 17:16', 'name': '/var/log/omelasticsearch.log', 'raw_entry': '-rw-r--r--. 1 0 0   9 Mar 15 17:16 /var/log/omelasticsearch.log', 'dir': ''}
    assert rsyslog_errorfile.entries.get('/var/log/rsyslog/es-errors1.log').get('size') == 176


def test_ls_rsyslog_errorfile_err():
    with pytest.raises(ParseException) as pe:
        LsRsyslogErrorfile(context_wrap(LS_RSYSLOG_ERRORFILE_ERROR))
        assert 'Error:' in str(pe)


def test_ls_rsyslog_errorfile_doc_examples():
    env = {
        'rsyslog_errorfile': LsRsyslogErrorfile(context_wrap(LS_RSYSLOG_ERRORFILE)),
    }
    failed, total = doctest.testmod(ls_rsyslog_errorfile, globs=env)
    assert failed == 0
