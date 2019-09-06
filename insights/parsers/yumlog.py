"""
YumLog - file ``/var/log/yum.log``
==================================

This module provides parsing for the ``/var/log/yum.log`` file.
The ``YumLog`` class implements parsing for the file, which looks like::

    May 13 15:54:49 Installed: libevent-2.0.21-4.el7.x86_64
    May 13 15:54:49 Installed: tmux-1.8-4.el7.x86_64
    May 23 18:06:24 Installed: wget-1.14-10.el7_0.1.x86_64
    May 23 18:10:05 Updated: 1:openssl-libs-1.0.1e-51.el7_2.5.x86_64
    May 23 18:10:05 Installed: 1:perl-parent-0.225-244.el7.noarch
    May 23 18:10:05 Installed: perl-HTTP-Tiny-0.033-3.el7.noarch
    May 23 16:09:09 Erased: redhat-access-insights-batch
    May 23 18:10:05 Installed: perl-podlators-2.5.1-3.el7.noarch
    May 23 18:10:05 Installed: perl-Pod-Perldoc-3.20-4.el7.noarch
    May 23 18:10:05 Installed: 1:perl-Pod-Escapes-1.04-286.el7.noarch
    May 23 18:10:06 Installed: perl-Text-ParseWords-3.29-4.el7.noarch

The information is stored as a ``list`` of ``Entry`` objects, each of which
contains attributes for the position in the log, timestamp of the action,
the package's state in the system, and the affected package as an
``InstalledRpm``.

Note:
    The examples in this module may be executed with the following command:

    ``python -m insights.parsers.yumlog``

Examples:
     >>> YumLog.filters.append('wrapper')
     >>> YumLog.token_scan('daemon_start', 'Wrapper Started as Daemon')
     >>> logs = shared[YumLog]
     >>> len(logs.lines)
        11
     >>> wrapper_logs = logs.get('wrapper') # Can only rely on lines filtered being present
     >>> wrapper_logs[0].get('raw_message')
        'May 23 18:10:06 Installed: perl-Text-ParseWords-3.29-4.el7.noarch'
"""

from .. import LogFileOutput, parser
from insights.specs import Specs


@parser(Specs.yum_log)
class YumLog(LogFileOutput):
    """Class for parsing ``/var/log/yum.log`` file."""
    pass
