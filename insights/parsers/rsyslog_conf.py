"""
rsyslog_conf - File /etc/rsyslog.conf
=====================================

The rsyslog configuration files can include statements with two different
line based formats along with snippets of 'RainerScript' that can span
multiple lines.

See http://www.rsyslog.com/doc/master/configuration/basic_structure.html#statement-types

Due to high parsing complexity, this parser presents a simple line-based
view of the file that meets the needs of the current rules.

Example:
    >>> content = '''
    ... :fromhost-ip, regex, "10.0.0.[0-9]" /tmp/my_syslog.log
    ... $ModLoad imtcp
    ... $InputTCPServerRun 10514"
    ... '''.strip()
    >>> from insights.tests import context_wrap
    >>> rsl = RsyslogConf(context_wrap(content))
    >>> len(rsl)
    3
    >>> len(list(rsl))
    3
    >>> any('imtcp' in n for n in rsl)
    True
"""
from .. import Parser, parser, get_active_lines


@parser('rsyslog.conf')
class RsyslogConf(Parser):
    """
    Parses `/etc/rsyslog.conf` info simple lines.

    Skips lines that begin with hash ("#") or are only whitespace.

    Attributes:
        data (list): List of lines in the file that don't start
            with '#' and aren't whitespace.
    """

    def parse_content(self, content):
        self.data = get_active_lines(content)

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        for d in self.data:
            yield d
