"""
Messages - file ``/var/log/messages``
=====================================

Reads the ``/var/log/messages`` file as a standard LogFileOutput class parser.

The important function is ``get(s)``, which finds all lines with the string
**s** and parses them into dictionaries with the following keys:

* ``timestamp`` - the time the log line was written
* ``procname`` - the process or facility that wrote the line
* ``hostname`` - the host that generated the log line
* ``message`` - the rest of the message (after the process name)
* ``raw_message`` - the raw message before being split.

It is best to use filters and/or scanners with the messages log, to speed up
parsing.  These work on the raw message, before being parsed.

Sample log lines::

    May 18 15:13:34 lxc-rhel68-sat56 jabberd/sm[11057]: session started: jid=rhn-dispatcher-sat@lxc-rhel6-sat56.redhat.com/superclient
    May 18 15:13:36 lxc-rhel68-sat56 wrapper[11375]: --> Wrapper Started as Daemon
    May 18 15:13:36 lxc-rhel68-sat56 wrapper[11375]: Launching a JVM...
    May 18 15:24:28 lxc-rhel68-sat56 yum[11597]: Installed: lynx-2.8.6-27.el6.x86_64
    May 18 15:36:19 lxc-rhel68-sat56 yum[11954]: Updated: sos-3.2-40.el6.noarch

Examples:

    >>> Messages.filters.append('wrapper')
    >>> Messages.token_scan('daemon_start', 'Wrapper Started as Daemon')
    >>> msgs = shared[Messages]
    >>> len(msgs.lines)
    >>> wrapper_msgs = msgs.get('wrapper') # Can only rely on lines filtered being present
    >>> wrapper_msgs[0]
    {'timestamp': 'May 18 15:13:36', 'hostname': 'lxc-rhel68-sat56',
     'procname': wrapper[11375]', 'message': '--> Wrapper Started as Daemon',
     'raw_message': 'May 18 15:13:36 lxc-rhel68-sat56 wrapper[11375]: --> Wrapper Started as Daemon'
    }
    >>> msgs.daemon_start # Token set if matching lines present in logs
    True

"""

from .. import LogFileOutput, parser


@parser('messages')
class Messages(LogFileOutput):
    """
    Read the ``/var/log/messages`` file using the LogFileOutput parser class.

    NOTE:
        Because /var/log/messages timestamps by default have no year,
        the year of the logs will be inferred from the year in your timestamp.
        This will also work around December/January crossovers.
    """
    time_format = '%b %d %H:%M:%S'

    def get(self, s):
        """
        Parameters:
            s (str): String to search for

        Returns:
            ([dicts]): all lines that contain 's' as a list of dictionaries

        Examples::

            [
             {'timestamp':'May 18 14:24:14',
              'procname': 'kernel',
              'hostname':'lxc-rhel68-sat56',
              'message': '...',
              'raw_message': '...: ...'
             }, ...
            ]
        """
        r = []
        for l in self.lines:
            if s in l:
                info, msg = [i.strip() for i in l.split(': ', 1)]

                msg_info = {
                    'message': msg,
                    'raw_message': l
                }

                info_splits = info.split()
                if len(info_splits) == 5:
                    msg_info['timestamp'] = ' '.join(info_splits[:3])
                    msg_info['hostname'] = info_splits[3]
                    msg_info['procname'] = info_splits[4]
                r.append(msg_info)
        return r
