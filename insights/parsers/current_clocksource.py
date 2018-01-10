"""
CurrentClockSource - file ``/sys/devices/system/clocksource/clocksource0/current_clocksource``
==============================================================================================

This is a relatively simple parser that reads the
``/sys/devices/system/clocksource/clocksource0/current_clocksource`` file.
As well as reporting the contents of the file in its ``data`` property, it
also provides three properties that are true if the clock source is set to
that value:

    * **is_kvm** - the clock source file contains 'kvm-clock'
    * **is_tsc** - the clock source file contains 'tsc'
    * **is_vmi_timer** - the clock source file contains 'vmi-timer'

Examples:

    >>> cs = shared[CurrentClockSource]
    >>> cs.data
    'tsc'
    >>> cs.is_tsc
    True
"""

from .. import Parser, parser
from insights.specs import Specs


@parser(Specs.current_clocksource)
class CurrentClockSource(Parser):
    """
    The CurrentClockSource parser class.

    Attributes:
        data (str): the content of the current_clocksource file.
    """

    def parse_content(self, content):
        self.data = list(content)[0]

    @property
    def is_kvm(self):
        """
        bool: does the clock source contain 'kvm-clock'?
        """
        return 'kvm-clock' in self.data

    @property
    def is_tsc(self):
        """
        bool: does the clock source contain 'tsc'?
        """
        return 'tsc' in self.data

    @property
    def is_vmi_timer(self):
        """
        bool: does the clock source contain 'vmi-timer'?
        """
        return 'vmi-timer' in self.data
