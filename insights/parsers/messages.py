"""
Messages file ``/var/log/messages``
===================================
"""

from .. import Syslog, parser
from insights.specs import Specs


@parser(Specs.messages)
class Messages(Syslog):
    """
    Read the ``/var/log/messages`` file.

    .. note::
        Please refer to its super-class :class:`insights.core.Syslog` for more
        details.

    Sample log lines::

        May 18 15:13:34 lxc-rhel68-sat56 jabberd/sm[11057]: session started: jid=rhn-dispatcher-sat@lxc-rhel6-sat56.redhat.com/superclient
        May 18 15:13:36 lxc-rhel68-sat56 wrapper[11375]: --> Wrapper Started as Daemon
        May 18 15:13:36 lxc-rhel68-sat56 wrapper[11375]: Launching a JVM...
        May 18 15:24:28 lxc-rhel68-sat56 yum[11597]: Installed: lynx-2.8.6-27.el6.x86_64
        May 18 15:36:19 lxc-rhel68-sat56 yum[11954]: Updated: sos-3.2-40.el6.noarch

    .. note::
        Because /var/log/messages timestamps by default have no year,
        the year of the logs will be inferred from the year in your timestamp.
        This will also work around December/January crossovers.

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
    pass
