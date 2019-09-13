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
     >>> YumLog.filters.append('Installed')
     >>> YumLog.token_scan('Installed', 'Installed: perl-Text-ParseWords-3.29-4.el7.noarch')
     >>> len(logs.lines)
        11
     >>> installed_logs = logs.get('Installed') # Can only rely on lines filtered being present
     >>> installed_logs[0].get('raw_message')
        'May 23 18:10:06 Installed: perl-Text-ParseWords-3.29-4.el7.noarch'
"""
import datetime
from insights import LogFileOutput, parser
from insights.specs import Specs


@parser(Specs.yum_log)
class YumLog(LogFileOutput):
    """Class for parsing ``/var/log/yum.log`` file."""

    time_format = '%b %d %H:%M:%S'

    def _parse_line(self, line):
        """
        Parsed result::
            {'timestamp':'May 23 18:10:06',
             'status': 'Installed',
             'rpm':'perl-Text-ParseWords-3.29-4.el7.noarch',
             'message': '...',
             'raw_message': '...: ...'
            }
        """
        msg_info = {'raw_message': line}
        if ': ' in line:
            info, msg = [i.strip() for i in line.split(': ', 1)]
            msg_info['message'] = msg

            info_splits = info.split()
            if len(info_splits) == 4:
                logstamp = ' '.join(info_splits[:3])
                try:
                    datetime.datetime.strptime(logstamp, self.time_format)
                except ValueError:
                    return msg_info
                msg_info['timestamp'] = logstamp
                msg_info['status'] = info_splits[3]
                msg_info['rpm'] = msg_info['message']
        return msg_info
