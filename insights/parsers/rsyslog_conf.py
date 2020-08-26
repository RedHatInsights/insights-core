"""
RsyslogConf - file ``/etc/rsyslog.conf``
========================================

The rsyslog configuration files can include statements with two different
line based formats along with snippets of 'RainerScript' that can span
multiple lines.

See http://www.rsyslog.com/doc/master/configuration/basic_structure.html#statement-types

Due to high parsing complexity, this parser presents a simple line-based
view of the file that meets the needs of the current rules.
"""
from .. import Parser, parser, get_active_lines
from insights.specs import Specs
from insights.core.filters import add_filter


add_filter(Specs.rsyslog_conf, ["{", "}", "(", ")"])


@parser(Specs.rsyslog_conf)
class RsyslogConf(Parser, list):
    """
    Parses `/etc/rsyslog.conf` content.

    Skips lines that begin with hash ("#") or are only whitespace.

    Attributes:
        data (list): List of lines in the file that don't start
            with '#' and aren't whitespace.

    Example:
        >>> type(rsysconf)
        <class 'insights.parsers.rsyslog_conf.RsyslogConf'>
        >>> len(rsysconf)
        13
        >>> rsysconf[2]
        'authpriv.*                                              /var/log/secure'
    """
    def __init__(self, *args, **kwargs):
        super(RsyslogConf, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        data = []
        brace_flag = False
        parenthesis_flag = False
        parenthesis_string = ""
        brace_string = ""

        for line in get_active_lines(content):
            l_strip = line.strip()
            # Combine multi lines in brace into one line
            if brace_flag:
                brace_string = brace_string + " " + l_strip
                if "}" in l_strip:
                    data.append(brace_string)
                    brace_string = ""
                    brace_flag = False
                continue
            else:
                if "{" in l_strip:
                    if "}" in l_strip:
                        data.append(l_strip)
                    else:
                        brace_flag = True
                        brace_string = l_strip
                    continue
                # Combine multi lines in parenthesis and not in brace into one line
                if parenthesis_flag:
                    parenthesis_string = parenthesis_string + " " + l_strip
                    if ")" in l_strip:
                        data.append(parenthesis_string)
                        parenthesis_string = ""
                        parenthesis_flag = False
                    continue
                else:
                    if "(" in l_strip:
                        if ")" in l_strip:
                            data.append(l_strip)
                        else:
                            parenthesis_flag = True
                            parenthesis_string = l_strip
                        continue
                    else:
                        data.append(l_strip)
        self.extend(data)
