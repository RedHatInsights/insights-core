"""
samba logs - files matching ``/var/log/samba/*.log``
====================================================
"""

from insights import parser, LogFileOutput
from datetime import datetime
from insights.specs import Specs


def strip_surrounds(s):
    start = 0
    end = len(s) - 1
    while (s[start] == '[' and s[end] == ']') or \
      (s[start] == '[' and s[end] == ',') or \
      (s[start] == '(' and s[end] == ')'):
        start += 1
        end -= 1
    if s[end] == ',':
        end -= 1
    return s[start:(end + 1)]


@parser(Specs.samba_logs)
class SAMBALog(LogFileOutput):
    """
    Parser class for reading samba log files.  The main work is done by the
    LogFileOutput super-class.

    .. note:

        Please refer to its super-class :class:`insights.core.LogFileOutput`

    Sample input:

       [2018/12/07 07:09:44.812154,  5, pid=6434, effective(0, 0), real(0, 0)] ../source3/param/loadparm.c:1344(free_param_opts)
        Freeing parametrics:
       [2018/12/07 07:09:44.812281,  3, pid=6434, effective(0, 0), real(0, 0)] ../source3/param/loadparm.c:547(init_globals)
        Initialising global parameters
       [2018/12/07 07:09:44.812356,  2, pid=6434, effective(0, 0), real(0, 0)] ../source3/param/loadparm.c:319(max_open_files)
        rlimit_max: increasing rlimit_max (1024) to minimum Windows limit (16384)
       [2019/45/899 11:11:04.911891,  3, pid=15822, effective(0, 0), real(0, 0)] ../source3/printing/queue_process.c:236
        (bq_sig_hup_handler) Reloading pcap cache after SIGHUP.

    Each line is parsed into a dictionary with the following keys:

        * **timestamp** - the date of the log line (as a string)
        * **datetime** - the date as a datetime object (if conversion is possible)
        * **pid** - process id of samba process being run
        * **function** - the function within the module
        * **message** - the body of the message
        * **raw_message** - the raw message before being split.

    Examples:
        >>> 'Fake' in samba_logs
        True
        >>> 'pid=15822, effective(0, 0), real(0, 0)]' in samba_logs
        True
        >>> len(samba_logs.get('Fake line')) == 1
        True
    """
    time_format = '%b %d %H:%M:%S %Y'

    def _parse_line(self, line):
        fields = line.split()
        try:
            parsed_line = {
                'timestamp': strip_surrounds(' '.join(fields[0:2])),
                'pid': strip_surrounds(fields[3]),
                'function': strip_surrounds(fields[8]),
                'message': ' '.join(fields[8:]),
                'raw_message': line
            }

            parsed_line['datetime'] = datetime.strptime(
                parsed_line['timestamp'],
                '%a %b %d %H:%M:%S %Y'
            )
        except:
            pass
        return parsed_line
