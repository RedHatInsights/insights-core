"""
ProcSwapMemory
==============

Parser for calculating the total SWAP memory of each PID.

"""

from insights.specs import Specs
from insights.parsers import SkipException
from insights import CommandParser, parser
import json


@parser(Specs.proc_swap_memory)
class ProcSwapMemory(CommandParser):
    """
    Base class which calculates the total SWAP memory of each PID. For the calculation, it collects
    and sums the ``Swap`` and ``SwapPss`` variable of each PID.

    Typical content looks like::

      [{"pid": 3065, "command": "/usr/libexec/packagekitd", "swap": 348, "swappss": 348}, {"pid": 2873, "command": "/usr/bin/gnome-shell", "swap": 13576, "swappss": 348}]

    Attributes:
      data (list): List of dictionaries that store pid, command, swap key memory, and swappss key memory for each PID.

    Examples:
    >>> type(swap_memory_doc_obj)
    <class 'insights.parsers.proc_swap_memory.ProcSwapMemory'>
    >>> swap_memory_doc_obj.data[0]['pid']
    3065
    >>> swap_memory_doc_obj.data[0]['command']
    '/usr/libexec/packagekitd'
    >>> swap_memory_doc_obj.data[0]['swap']
    348
    """
    def parse_content(self, content):
        if not content:
            raise SkipException('No files found.')
        self.data = json.loads(''.join(content))
