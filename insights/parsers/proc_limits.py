"""
ProcLimits - File ``/proc/<PID>/limits``
========================================

Parser for parsing the the ``limits`` file under special ``/proc/<PID>``
directory.

"""

from .. import Parser, parser, LegacyItemAccess
from ..parsers import parse_fixed_table, ParseException
from insights.specs import Specs

HEADER_SUBSTITUTE = [('Soft Limit', 'Soft_Limit'), ('Hard Limit', 'Hard_Limit')]


class Limits(LegacyItemAccess):
    """
    An object representing a line in the ``/proc/limits``.  Each entry contains
    below fixed attributes:

    Attributes:
        hard_limit(str): Hard limit
        soft_limit(str): Soft limit
        units(str): Unit of the limit value
    """

    def __init__(self, data={}):
        self.data = data
        for k, v in data.items():
            setattr(self, k, v)

    def items(self):
        """
        To keep backward compatibility and let it can be iterated as a
        dictionary.
        """
        for k, v in self.data.items():
            yield k, v


class ProcLimits(Parser):
    """
    Base class for parsing the ``limits`` file under special ``/proc/<PID>``
    directory into a list of dictionaries by using the
    :py:func:`insights.parsers.parse_fixed_table` function.

    Each line is a dictionary of fields, named according to their definitions
    in ``Limit``.

    This class provides the '__len__' and '__iter__' methods to allow it to
    be used as a list to iterate over the parsed dictionaries.

    Each of the resource provided by this file will be set as an attribute.
    The attribute name is the resource name got from the ``Limit`` column, which
    is converted to lowercase and joined the words with underline '_'.  If not
    sure about whether an attribute is exist or not, check it via the
    '__contains__' method before fetching it.
    The attribute value is set to a :class:`Limits` which wraps the
    corresponding ``hard_limit``, ``soft_limit`` and ``units``.

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
        >>> len(proc_limits)
        16
        >>> proc_limits.max_processes.hard_limit
        '99'
        >>> proc_limits.max_processes.soft_limit
        '9'
        >>> 'max_cpu_time' in proc_limits
        True
        >>> proc_limits.max_cpu_time.soft_limit
        'unlimited'
        >>> proc_limits.max_cpu_time.units
        'seconds'

    Raises:
        insights.parsers.ParseException: if the ``limits`` file is empty or
            doesn't exist.
    """

    def __contains__(self, key):
        return any(key == row['Limit'] for row in self.data)

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        for row in self.data:
            yield row

    def parse_content(self, content):
        if len(content) == 0 or 'No such file or directory' in content[0]:
            raise ParseException("Error: ", content[0] if content else 'empty file')
        self.data = parse_fixed_table(content, header_substitute=HEADER_SUBSTITUTE)
        for row in self.data:
            row['Limit'] = row['Limit'].lower().replace(' ', '_')
            setattr(self, row['Limit'],
                    Limits({'hard_limit': row['Hard_Limit'],
                            'soft_limit': row['Soft_Limit'],
                            'units': row['Units']}))


@parser(Specs.httpd_limits)
class HttpdLimits(ProcLimits):
    """
    Class for parsing the ``limits`` file of the ``httpd`` process.
    """
    pass


@parser(Specs.mysqld_limits)
class MysqldLimits(ProcLimits):
    """
    Class for parsing the ``limits`` file of the ``mysqld`` process.
    """
    pass


@parser(Specs.ovs_vswitchd_limits)
class OvsVswitchdLimits(ProcLimits):
    """
    Class for parsing the ``limits`` file of the ``ovs-vswitchd`` process.
    """
    pass
