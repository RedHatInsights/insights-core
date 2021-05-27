"""
ProcSmaps - File ``/proc/<PID>/smaps``
======================================

Parser for parsing the ``smaps`` file under ``/proc/<PID>`` directory.

"""

from insights.specs import Specs
from insights.parsers import SkipException
from insights import CommandParser, parser
import json


@parser(Specs.proc_smaps)
class ProcSmaps(CommandParser):
    """
    Base class for parsing the ``smaps`` file under special ``/proc/<PID>``
    directory into a list of dictionaries.

    Typical content looks like::

        [{"pid": 3065, "command": "/usr/libexec/packagekitd", "swap": 348, "swappss": 348}, {"pid": 2873, "command": "/usr/bin/gnome-shell", "swap": 13576, "swappss": 348}]

    Examples:
        >>> type(proc_smaps)
        <class 'insights.parsers.proc_smaps.ProcSmaps'>
        >>> proc_smaps.data[0]['PID']
        3443
        >>> str(proc_smaps.data[0]['COMMAND'])
        '/usr/bin/gnome-shell'
        >>> proc_smaps.data[0]['Swap']
        54772
        >>> proc_smaps.data[0]['SwapPss']
        54492
    """
    def parse_content(self, content):
        if not content:
            raise SkipException('No files found.')
        self.data = json.loads(''.join(content))
