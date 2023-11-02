"""
SquidCacheLog - file ``/var/log/squid/cache.log``
=================================================
"""

from insights import parser
from insights.specs import Specs
from insights.core import LogFileOutput


@parser(Specs.squid_cache_log)
class SquidCacheLog(LogFileOutput):
    """
    Read the ``/var/log/squid/cache.log`` file.

    .. note::
        Please refer to its super-class :class:`insights.core.LogFileOutput` for more
        details.

    Sample log lines::

        2023/11/01 06:00:33 kid1|   Took 0.00 seconds (  0.00 entries/sec).
        FATAL: Couldn't start logfile helper
        Squid Cache (Version 3.5.20): Terminated abnormally.
        CPU Usage: 0.046 seconds = 0.033 user + 0.013 sys
        Maximum Resident Size: 34784 KB
        Page faults with physical i/o: 0
        2023/11/01 06:01:16 kid1| Set Current Directory to /var/spool/squid
        2023/11/01 06:01:16 kid1| Starting Squid Cache version 3.5.20 for x86_64-redhat-linux-gnu...
        2023/11/01 06:01:16 kid1| Service Name: squid

    Examples:
        >>> SquidCacheLog.last_scan('logfile_start_error', "Couldn't start logfile helper")
        >>> type(squid_cache_log)
        <class 'insights.parsers.squid.SquidCacheLog'>
        >>> error_msg = squid_cache_log.get('logfile_start_error')
        >>> error_msg.get('raw_message')
        "FATAL: Couldn't start logfile helper"
    """
    time_format = None
