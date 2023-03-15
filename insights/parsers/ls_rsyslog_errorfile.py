"""
LsRsyslogErrorfile - command ``ls -ln <path>``
==============================================

The ``ls -ln <path>`` command provides information for the listing of the
specified directory.

Attributes:
    data (dict): Dictionary of keys with values in dict.

Sample directory list collected::

    -rwxr-xr-x.  1 0  0     2558 Apr 10  2019 /var/log/oversized.log

Examples:
    >>> type(rsyslog_errorfile)
    <class 'insights.parsers.ls_rsyslog_errorfile.LsRsyslogErrorfile'>
    >>> len(rsyslog_errorfile.data)
    1
    >>> rsyslog_errorfile.data.get('/var/log/oversized.log').get('size')
    2558
"""

from insights.core.plugins import parser
from insights.specs import Specs
from insights.core import CommandParser, ls_parser


@parser(Specs.ls_rsyslog_errorfile)
class LsRsyslogErrorfile(CommandParser):
    def parse_content(self, content):
        ls_data = ls_parser.parse(content, '').get('')
        self.data = ls_data.get('entries')
