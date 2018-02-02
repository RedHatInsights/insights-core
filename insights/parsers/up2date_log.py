"""
up2date Logs -  Files ``/var/log/up2date``
==========================================

Modules for parsing the content of log file ``/var/log/up2date`` in sosreport archives of RHEL.

.. note::
    Please refer to the super-class :class:`insights.core.LogFileOutput`
"""
from .. import LogFileOutput, parser


@parser('up2date_log')
class Up2dateLog(LogFileOutput):
    """Class for parsing the log file: ``/var/log/up2date`` """
    time_format = '%a %b %d %H:%M:%S %Y'
