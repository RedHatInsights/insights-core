"""
LpstatPrinters - command ``lpstat -p``
======================================

Parses the output of ``lpstat -p``, to get locally configured printers.

Current available printer states are:

* IDLE (``PRINTER_STATUS_IDLE``)
* PROCESSING (``PRINTER_STATUS_PROCESSING``) -- printing
* DISABLED (``PRINTER_STATUS_DISABLED``)
* UNKNOWN (``PRINTER_STATUS_UNKNOWN``)


Examples:
    >>> from insights.parsers.lpstat import LpstatPrinters, PRINTER_STATUS_DISABLED
    >>> from insights.tests import context_wrap
    >>> LPSTAT_P_OUTPUT = '''
    ... printer idle_printer is idle.  enabled since Fri 20 Jan 2017 09:55:50 PM CET
    ... printer disabled_printer disabled since Wed 15 Feb 2017 12:01:11 PM EST -
    ...     reason unknown
    ... '''
    >>> lpstat = LpstatPrinters(context_wrap(LPSTAT_P_OUTPUT))
    >>> lpstat.printers
    [{'status': 'IDLE', 'name': 'idle_printer'}, {'status': 'DISABLED', 'name': 'disabled_printer'}]
    >>> lpstat.printer_names_by_status(PRINTER_STATUS_DISABLED)
    ['disabled_printer']

"""

from .. import parser, CommandParser
from insights.specs import Specs

# Printer states
PRINTER_STATUS_IDLE = 'IDLE'
PRINTER_STATUS_PROCESSING = 'PROCESSING'
PRINTER_STATUS_DISABLED = 'DISABLED'
PRINTER_STATUS_UNKNOWN = 'UNKNOWN'

START_LINE_MARKER = 'printer '


@parser(Specs.lpstat_p)
class LpstatPrinters(CommandParser):
    """Class to parse ``lpstat -p`` command output.

    Raises:
        ValueError: Raised if any error occurs parsing the content.
    """

    def __init__(self, *args, **kwargs):
        self.printers = []
        """dict: Dictionary of locally configured printers, with keys 'name' and 'status'"""
        super(LpstatPrinters, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        marker_len = len(START_LINE_MARKER)
        for line in content:
            if line.startswith(START_LINE_MARKER):
                printer_line = line[marker_len:]
                # cut printer name until next space character
                printer_name = printer_line[:printer_line.index(' ')]
                state_line_starts = marker_len + len(printer_name) + 1  # 1 is space
                state_line = line[state_line_starts:]

                printer = {
                    'name': printer_name,
                    'status': self._parse_status(state_line)
                }
                self.printers.append(printer)

    def _parse_status(self, state_line):
        if 'is idle' in state_line:
            return PRINTER_STATUS_IDLE
        elif 'printing' in state_line:
            return PRINTER_STATUS_PROCESSING
        elif 'disabled' in state_line:
            return PRINTER_STATUS_DISABLED

        return PRINTER_STATUS_UNKNOWN

    def printer_names_by_status(self, status):
        """Gives names of configured printers for a given status

        Arguments:
            status (string)
        """
        names = [prntr['name'] for prntr in self.printers if prntr['status'] == status]
        return names
