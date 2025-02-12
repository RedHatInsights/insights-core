"""
WcProc1Mountinfo - Command ``/usr/bin/wc -l /proc/1/mountinfo``
===============================================================

Parser for parsing the output of command ``/usr/bin/wc -l /proc/1/mountinfo``.
"""
from insights.core import Parser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.wc_proc_1_mountinfo)
class WcProc1Mountinfo(Parser):
    """
    Provides the line counts of file ``/proc/1/mountinfo`` by parsing the
    output of command ``/usr/bin/wc -l /proc/1/mountinfo``.

    Attributes:
        line_count(int): the line counts of file ``/proc/1/mountinfo``

    Typical content looks like::

        37 /proc/1/mountinfo

    Examples:
        >>> type(wc_info)
        <class 'insights.parsers.wc.WcProc1Mountinfo'>
        >>> wc_info.line_count
        37

    Raises:
        SkipComponent: if the command output is empty or missing file
        ParseException: if the command output is unparsable
    """

    def parse_content(self, content):
        if len(content) == 0 or 'No such file or directory' in content[0]:
            raise SkipComponent("Error: ", content[0] if content else 'empty file')
        count_str = content[0].split()[0]
        if not count_str.isdigit():
            raise ParseException("Error: unparsable output from command wc: ", content[0])
        self.line_count = int(count_str)


@parser(Specs.wc_var_lib_pcp_config_pmda)
class WcPcpConfigPmda(Parser, dict):
    """
    Provides the line counts of file ``/var/lib/pcp/config/pmda/*`` by parsing the
    output of command ``/usr/bin/wc -l /var/lib/pcp/config/pmda/*``.

    Typical content looks like::
        6 /var/lib/pcp/config/pmda/144.0.py
        3 /var/lib/pcp/config/pmda/60.1
        5 /var/lib/pcp/config/pmda/60.10
        3 /var/lib/pcp/config/pmda/60.11
        275 /var/lib/pcp/config/pmda/60.12
        16 /var/lib/pcp/config/pmda/60.17
        3 /var/lib/pcp/config/pmda/60.24
        6 /var/lib/pcp/config/pmda/60.28
        17 /var/lib/pcp/config/pmda/60.3
        21 /var/lib/pcp/config/pmda/60.32
        974 /var/lib/pcp/config/pmda/60.4
        140113 /var/lib/pcp/config/pmda/60.40
        24 /var/lib/pcp/config/pmda/62.0
        141466 total

    Examples:
        >>> type(wc_pcp_config_pmda)
        <class 'insights.parsers.wc.WcPcpConfigPmda'>
        >>> wc_pcp_config_pmda['/var/lib/pcp/config/pmda/62.0']
        24

    Raises:
        SkipComponent: if the command output is empty or missing file
    """

    def parse_content(self, content):
        if len(content) == 0 or 'No such file or directory' in content[0]:
            raise SkipComponent("Error: ", content[0] if content else 'empty file')
        for line in content:
            count_str, file = line.split()
            if file.startswith('/var/lib/pcp/config/pmda/') and count_str.isdigit():
                self[file] = int(count_str)
