"""
HttpdLimits - File ``/proc/`cat /etc/httpd/run/httpd.pid`/limits``
==================================================================

Parser for parsing the ``/proc/`cat /etc/httpd/run/httpd.pid`` file.

"""

from .. import Parser, parser
from ..parsers import parse_fixed_table

HEADER_SUBSTITUTE = [('Soft Limit', 'Soft_Limit'), ('Hard Limit', 'Hard_Limit')]


@parser('httpd_limits')
class HttpdLimits(Parser):
    """
    Parse the ``/proc/`cat /etc/httpd/run/httpd.pid`` file into a list of lines
    by using the ``parse_fixed_table`` function.  Each line is a dictionary of
    fields, named according to their definitions in ``Limit``.
    This class provides the '__len__' and '__iter__' methods to allow it to
    be used as a list to iterate over the ``data`` data.

    Typical content looks like::

        Limit                     Soft Limit           Hard Limit           Units
        Max cpu time              unlimited            unlimited            seconds
        Max file size             unlimited            unlimited            bytes
        Max data size             unlimited            unlimited            bytes
        Max stack size            10485760             unlimited            bytes
        Max core file size        0                    unlimited            bytes
        Max resident set          unlimited            unlimited            bytes
        Max processes             9                    99                   processes
        Max open files            1024                 4096                 files
        Max locked memory         65536                65536                bytes
        Max address space         unlimited            unlimited            bytes
        Max file locks            unlimited            unlimited            locks
        Max pending signals       15211                15211                signals
        Max msgqueue size         819200               819200               bytes
        Max nice priority         0                    0
        Max realtime priority     0                    0
        Max realtime timeout      unlimited            unlimited            us

    Examples:
        >>> httpd_limits = shared[HttpdLimits]
        >>> httpd_limits.max_processes
        '99'
        >>> len(httpd_limits)
        16

    Attributes:
        data (list): a list of parsed limit line as dict.
        max_processes (str): the hard limit of the max processes.
    """

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        for row in self.data:
            yield row

    def parse_content(self, content):
        self.data = []
        self.max_processes = ''
        if 'No such file or directory' not in content[0]:
            self.data = parse_fixed_table(content, header_substitute=HEADER_SUBSTITUTE)
        for row in self.data:
            if 'Max processes' == row['Limit']:
                self.max_processes = row['Hard_Limit']
