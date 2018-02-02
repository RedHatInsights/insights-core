"""
up2date Logs -  Files ``/var/log/up2date``
==========================================

Modules for parsing the content of log file ``/var/log/up2date`` in sosreport archives of RHEL.

"""
from .. import LogFileOutput, parser
from insights.specs import Specs


@parser(Specs.up2date_log)
class Up2dateLog(LogFileOutput):
    """
    Class for parsing the log file: ``/var/log/up2date``.

    .. note::
        Please refer to its super-class :class:`insights.core.LogFileOutput`

    Example content of ``/var/log/up2date`` command is::

        [Thu Feb  1 02:46:25 2018] rhn_register updateLoginInfo() login info
        [Thu Feb  1 02:46:35 2018] rhn_register A socket error occurred: (-3, 'Temporary failure in name resolution'), attempt #1
        [Thu Feb  1 02:46:40 2018] rhn_register A socket error occurred: (-3, 'Temporary failure in name resolution'), attempt #2
        [Thu Feb  1 02:46:45 2018] rhn_register A socket error occurred: (-3, 'Temporary failure in name resolution'), attempt #3
        [Thu Feb  1 02:46:50 2018] rhn_register A socket error occurred: (-3, 'Temporary failure in name resolution'), attempt #4
        [Thu Feb  1 02:46:55 2018] rhn_register A socket error occurred: (-3, 'Temporary failure in name resolution'), attempt #5

        ...

    Examples:
        >>> ulog.get('Temporary failure in name resolution')[0]['raw_message']
        "[Thu Feb  1 02:46:35 2018] rhn_register A socket error occurred: (-3, 'Temporary failure in name resolution'), attempt #1"
    """

    time_format = '%a %b %d %H:%M:%S %Y'
