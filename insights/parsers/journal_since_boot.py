"""
JournalSinceBoot file ``/sos_commands/logs/journalctl_--no-pager_--boot``
=========================================================================
"""

from .. import Syslog, parser
from insights.specs import Specs
from insights.util import deprecated


@parser(Specs.journal_since_boot)
class JournalSinceBoot(Syslog):
    """

    .. warning::

        This parser is deprecated, please use
        :py:class:`insights.parsers.journalctl.JournalSinceBoot` instead.


    Read the ``/sos_commands/logs/journalctl_--no-pager_--boot`` file.  Uses
    the ``Syslog`` class parser functionality - see the base class for more
    details.

    Sample log lines::

        -- Logs begin at Wed 2017-02-08 15:18:00 CET, end at Tue 2017-09-19 09:25:27 CEST. --
        May 18 15:13:34 lxc-rhel68-sat56 jabberd/sm[11057]: session started: jid=rhn-dispatcher-sat@lxc-rhel6-sat56.redhat.com/superclient
        May 18 15:13:36 lxc-rhel68-sat56 wrapper[11375]: --> Wrapper Started as Daemon
        May 18 15:13:36 lxc-rhel68-sat56 wrapper[11375]: Launching a JVM...
        May 18 15:24:28 lxc-rhel68-sat56 yum[11597]: Installed: lynx-2.8.6-27.el6.x86_64
        May 18 15:36:19 lxc-rhel68-sat56 yum[11954]: Updated: sos-3.2-40.el6.noarch

    Note:
        Because journal timestamps by default have no year,
        the year of the logs will be inferred from the year in your timestamp.
        This will also work around December/January crossovers.

    Examples:
        >>> JournalSinceBoot.filters.append('wrapper')
        >>> JournalSinceBoot.token_scan('daemon_start', 'Wrapper Started as Daemon')
        >>> msgs = shared[JournalSinceBoot]
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

    def __init__(self, context):
        deprecated(
            JournalSinceBoot,
            "Please use the :class:`insights.parsers.journalctl.JournalSinceBoot` instead.",
            "3.1.25"
        )
        super(JournalSinceBoot, self).__init__(context)

    pass
