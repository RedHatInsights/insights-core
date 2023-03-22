"""
LsRsyslogErrorfile - command ``ls -ln <path>``
==============================================

The ``ls -ln <path>`` command provides information for the listing of the
specified directory.

Attributes:
    data (dict): Dictionary of keys with values in dict.

Sample directory list collected::

    -rw-r--r--. 1 0 0   9 Mar 15 17:16 /var/log/omelasticsearch.log
    -rw-r--r--. 1 0 0 176 Mar 22 15:10 /var/log/rsyslog/es-errors1.log

Examples:
    >>> type(rsyslog_errorfile)
    <class 'insights.parsers.ls_rsyslog_errorfile.LsRsyslogErrorfile'>
    >>> len(rsyslog_errorfile.entries)
    2
    >>> rsyslog_errorfile.entries.get('/var/log/omelasticsearch.log').get('size')
    9
"""

from insights.core.plugins import parser
from insights.specs import Specs
from insights.core import Parser, ls_parser


@parser(Specs.ls_rsyslog_errorfile)
class LsRsyslogErrorfile(Parser):
    def parse_content(self, content):
        parsed_content = []
        for line in content:
            if 'No such file or directory' not in line:
                parsed_content.append(line)
        ls_data = ls_parser.parse(parsed_content, '').get('')
        self.entries = ls_data.get('entries')
