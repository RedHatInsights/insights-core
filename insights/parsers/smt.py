"""
Simultaneous Multithreading (SMT) parsers
=========================================

Parsers included in this module are:

CpuSMTActive - file ``/sys/devices/system/cpu/smt/active``
----------------------------------------------------------
CpuCoreOnline - files matching ``/sys/devices/system/cpu/cpu[0-9]*/online``
---------------------------------------------------------------------------
CpuSiblings - files matching ``/sys/devices/system/cpu/cpu[0-9]*/topology/thread_siblings_list``
------------------------------------------------------------------------------------------------
"""

from insights.core import Parser
from insights.core.plugins import parser
from insights.parsers import SkipException
from insights.specs import Specs
import re


@parser(Specs.cpu_smt_active)
class CpuSMTActive(Parser):
    """
    Class for parsing ``/sys/devices/system/cpu/smt/active`` file.
    Reports whether SMT is enabled and active.

    Typical output of this command is::

        1

    Raises:
        SkipException: When content is empty or cannot be parsed.

    Examples:
        >>> cpu_smt.on
        True
    """
    def parse_content(self, content):
        if not content:
            raise SkipException("No content.")
        self.on = bool(int(content[0]))


@parser(Specs.cpu_cores)
class CpuCoreOnline(Parser):
    """
    Class for parsing ``/sys/devices/system/cpu/cpu[0-9]*/online`` matching files.
    Reports whether a CPU core is online. Cpu0 is always online, so it does not have the "online" file.

    Typical output of this command is::

        1
        1
        1

    Raises:
        SkipException: When content is empty or cannot be parsed

    Examples:
        >>> cpu_core.core_id
        0
        >>> cpu_core.on
        True
    """
    cpu_core_path = r'/sys/devices/system/cpu/cpu(\d+)/online'

    def parse_content(self, content):
        if not content:
            raise SkipException("No content.")
        self.on = bool(int(content[0]))
        self.core_id = int(re.match(CpuCoreOnline.cpu_core_path, self.file_path).group(1))

    def __repr__(self):
        return "[Core {0}: {1}]".format(self.core_id, "Online" if self.on else "Offline")


@parser(Specs.cpu_siblings)
class CpuSiblings(Parser):
    """
    Class for parsing ``/sys/devices/system/cpu/cpu[0-9]*/topology/thread_siblings_list`` matching files.
    Reports CPU core siblings.

    Typical output of this command is::

        0,2
        1,3
        0,2
        1,3

    Raises:
        SkipException: When content is empty or cannot be parsed

    Examples:
        >>> cpu_siblings.core_id
        0
        >>> cpu_siblings.siblings
        [0, 2]
    """
    cpu_siblings_path = r'/sys/devices/system/cpu/cpu(\d+)/topology/thread_siblings_list'

    def parse_content(self, content):
        if not content:
            raise SkipException("No content.")

        # The separator in the sibling list may be either in the format 0-1 or 0,2 depending on the CPU model
        if "-" in content[0]:
            cpu_range = [int(x) for x in content[0].split("-")]
            self.siblings = [x for x in range(cpu_range[0], cpu_range[1] + 1)]
        elif "," in content[0]:
            self.siblings = [int(x) for x in content[0].split(",")]
        else:
            self.siblings = [int(content[0])]

        self.core_id = int(re.match(CpuSiblings.cpu_siblings_path, self.file_path).group(1))

    def __repr__(self):
        return "[Core {0} Siblings: {1}]".format(self.core_id, self.siblings)
