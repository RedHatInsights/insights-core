"""
System kernel files under ``/proc/sys/kernel`` or ``/sys/kernel``
=================================================================

This module contains the following parsers:

SchedRTRuntime - file ``/proc/sys/kernel/sched_rt_runtime_us``
--------------------------------------------------------------
SchedFeatures - file ``/sys/kernel/debug/sched_features``
---------------------------------------------------------
"""
from insights.core import Parser
from insights.core.exceptions import ParseException
from insights.core.plugins import parser
from insights.parsers import get_active_lines
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


@parser(Specs.sys_kernel_sched_features)
class SchedFeatures(Parser):
    """
    Class for parsing the `/sys/kernel/debug/sched_features` file.

    Typical content of the file is::

        GENTLE_FAIR_SLEEPERS START_DEBIT NO_NEXT_BUDDY LAST_BUDDY CACHE_HOT_BUDDY

    Examples:
        >>> type(sfs)
        <class 'insights.parsers.sys_kernel.SchedFeatures'>
        >>> "GENTLE_FAIR_SLEEPERS" in sfs.features
        True
        >>> "TEST1" in sfs.features
        False

    Attributes:
        features (list): A list with all the features
    """

    def parse_content(self, content):
        self.features = []
        for line in get_active_lines(content):
            self.features.extend(line.split())
