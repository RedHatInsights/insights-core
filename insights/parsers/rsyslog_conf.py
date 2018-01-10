"""
RsyslogConf - file ``/etc/rsyslog.conf``
========================================

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

import re
from insights.specs import Specs


@parser(Specs.rsyslog_conf)
class RsyslogConf(Parser):
    """
    Parses `/etc/rsyslog.conf` info simple lines.

    Skips lines that begin with hash ("#") or are only whitespace.

    Attributes:
        data (list): List of lines in the file that don't start
            with '#' and aren't whitespace.
        config_items(dict): Configuration items opportunistically found in the
            configuration file, with their values as given.
    """

    def parse_content(self, content):
        self.data = get_active_lines(content)

        self.config_items = {}
        # Config items are e.g. "$Word value #optional comment"
        config_re = re.compile(r'^\s*\$(?P<name>\S+)\s+(?P<value>.*?)(?:\s+#.*)?$')
        for line in self.data:
            lstrip = line.strip()
            match = config_re.match(lstrip)
            if match:
                self.config_items[match.group('name')] = match.group('value')

    def config_val(self, item, default=None):
        """
        Return the given configuration item, or the default if not defined.

        Parameters:
            item(str): The configuration item name
            default: The default if the item is not found (defaults to None)

        Returns:
            The related value in the `config_items` dictionary.
        """
        return self.config_items.get(item, default)

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        for d in self.data:
            yield d
