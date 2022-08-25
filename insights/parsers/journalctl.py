"""
JournalCtl - command ``journalctl xxx``
=======================================

This module contains the following parsers:

JournalAll - command ``journalctl --no-pager``
----------------------------------------------
JournalHeader - command ``journalctl --no-pager --header``
----------------------------------------------------------
JournalSinceBoot - command ``journalctl --no-pager --boot``
-----------------------------------------------------------

"""


from insights.core.plugins import parser
from insights.specs import Specs
from insights.core import Syslog


@parser(Specs.journal_all)
class JournalAll(Syslog):
    """
    Handle the output of ``journalctl --no-pager`` command.  Uses the ``Syslog`` class
    parser functionality - see the base class for more details.

    Sample log lines::

        -- Logs begin at Wed 2017-02-08 15:18:00 CET, end at Tue 2017-09-19 09:25:27 CEST. --
        May 18 15:13:34 lxc-rhel68-sat56 jabberd/sm[11057]: session started: jid=rhn-dispatcher-sat@lxc-rhel6-sat56.redhat.com/superclient
        May 18 15:13:36 lxc-rhel68-sat56 wrapper[11375]: --> Wrapper Started as Daemon
        May 18 15:13:36 lxc-rhel68-sat56 wrapper[11375]: Launching a JVM...
        May 18 15:24:28 lxc-rhel68-sat56 yum[11597]: Installed: lynx-2.8.6-27.el6.x86_64
        May 18 15:36:19 lxc-rhel68-sat56 yum[11954]: Updated: sos-3.2-40.el6.noarch

    .. note::
        Because journal timestamps by default have no year,
        the year of the logs will be inferred from the year in your timestamp.
        This will also work around December/January crossovers.

    Examples:
        >>> type(JournalAll)
        <class 'insights.parsers.journalctl.JournalAll'>
        >>> len(JournalAll.lines)
        10
        >>> bona_list = JournalAll.get('(root) LIST (root)')
        >>> bona_list[0].get('message')
        '(root) LIST (root)'
    """
    pass


@parser(Specs.journal_header)
class JournalHeader(Syslog):
    """
    Parses the output of command "journalctl --no-pager --header", this command shows
    internal header information of the journal fields accessed. Although its output is
    not kind of Logs, we used the `Syslog` as the base class to parser it.

    Sample Output::

        File Path: /run/log/journal/6bdaf92aa0754b53acbb1dbff7127e2b/system.journal
        File ID: b1390ea69aa747e9ac5c597835c3c562
        Machine ID: 6bdaf92aa0754b53acbb1dbff7127e2b
        Boot ID: 082ada53f8184c4896c73101ad793eb5
        Sequential Number ID: 435b0e30f47a46d8a2a2f9a42eae0aaf
        State: ONLINE
        Compatible Flags:
        Incompatible Flags: COMPRESSED-LZ4
        Header size: 240
        Arena size: 8388368
        Data Hash Table Size: 19904
        Field Hash Table Size: 333
        Rotate Suggested: no
        Head Sequential Number: 74388 (12294)
        Tail Sequential Number: 81647 (13eef)
        Head Realtime Timestamp: Mon 2022-08-15 12:01:10 CST (5e63fae9e6e58)
        Tail Realtime Timestamp: Wed 2022-08-17 18:38:48 CST (5e66d7852bb3e)
        Tail Monotonic Timestamp: 1month 2w 3d 14h 19min 3.733s (3c647d7ce0f)
        Objects: 19073
        Entry Objects: 7260
        Data Objects: 9297
        Data Hash Table Fill: 46.7%
        Field Objects: 52
        Field Hash Table Fill: 15.6%
        Tag Objects: 0
        Entry Array Objects: 2462
        Disk usage: 8.0M

    Examples:
        >>> type(journal_header)
        <class 'insights.parsers.journalctl.JournalHeader'>
        >>> result_list = journal_header.get('File Path')
        >>> len(result_list)
        1
        >>> result_list[0].get('raw_message')
        'File Path: /run/log/journal/6bdaf92aa0754b53acbb1dbff7127e2b/system.journal'
    """

    pass


@parser(Specs.journal_since_boot)
class JournalSinceBoot(Syslog):
    """
    Handle the output of ``journalctl --no-pager --boot`` command.  Uses
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
        >>> type(JournalSinceBoot)
        <class 'insights.parsers.journalctl.JournalSinceBoot'>
        >>> len(JournalSinceBoot.lines)
        10
        >>> bona_list = JournalSinceBoot.get('(root) LIST (root)')
        >>> bona_list[0].get('message')
        '(root) LIST (root)'
    """
    pass
