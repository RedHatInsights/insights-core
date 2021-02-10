"""
PmLogSummary - Command ``pmlogsummary``
=======================================
"""

from insights import parser, CommandParser
from insights.parsers import SkipComponent
from insights.specs import Specs


@parser(Specs.pmlog_summary)
class PmLogSummary(CommandParser, dict):
    """
    Parser to parse the output of the ``pmlogsummary`` command

    Sample output of the command is::

        mem.util.used  3133919.812 Kbyte
        mem.physmem  3997600.000 Kbyte
        kernel.all.cpu.user  0.003 none
        kernel.all.cpu.sys  0.004 none
        kernel.all.cpu.nice  0.000 none
        kernel.all.cpu.steal  0.000 none
        kernel.all.cpu.idle  3.986 none
        disk.all.total  0.252 count / sec

    Example:
        >>> type(pmlog_summary)
        <class 'insights.parsers.pmlog_summary.PmLogSummary'>
        >>> 'mem.util.used' in pmlog_summary
        True
        >>> pmlog_summary['disk.all.total']
        '0.252 count / sec'
    """

    def parse_content(self, content):
        data = {}
        for line in content:
            k, v = line.split(None, 1)
            if k:
                data[k] = v

        if len(data) == 0:
            raise SkipComponent()

        self.update(data)
