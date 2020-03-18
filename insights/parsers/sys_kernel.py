"""
System kernel files under ``/proc/sys/kernel`` or ``/sys/kernel``
=================================================================

This module contains the following parsers:

SchedRTRuntime - file ``/proc/sys/kernel/sched_rt_runtime_us``
--------------------------------------------------------------
"""

from insights import Parser, parser, get_active_lines
from insights.parsers import ParseException
from insights.specs import Specs


@parser(Specs.sched_rt_runtime_us)
class SchedRTRuntime(Parser):
    """
    Class for parsing the `/proc/sys/kernel/sched_rt_runtime_us` file.

    Typical content of the file is::

        950000

    Examples:
        >>> type(srt)
        <class 'insights.parsers.sys_kernel.SchedRTRuntime'>
        >>> srt.runtime_us
        950000

    Attributes:
        runtime_us (int): The value of sched_rt_runtime_us

    Raises:
        ParseException: Raised when there is more than one line or the value isn't interger.
    """

    def parse_content(self, content):
        lines = get_active_lines(content)
        if len(lines) != 1:
            raise ParseException("Unexpected file content")
        try:
            self.runtime_us = int(lines[0])
        except:
            raise ParseException("Unexpected file content")
