"""
PacemakerLog - file ``/var/log/pacemaker.log``
==============================================
"""

from .. import LogFileOutput, parser


@parser('pacemaker.log')
class PacemakerLog(LogFileOutput):
    """
    Read the pacemaker log file.  Uses the ``LogFileOutput`` class parser
    functionality - see the base class for more details.

    Sample pacemaker.log::

        Aug 21 12:58:40 [11656] example.redhat.com        cib:     info: crm_client_destroy: 	Destroying 0 events
        Aug 21 12:59:53 [11655] example.redhat.com pacemakerd:     info: pcmk_quorum_notification: 	Membership 12: quorum retained (3)
        Aug 21 12:59:53 [11661] example.redhat.com       crmd:     info: pcmk_quorum_notification: 	Membership 12: quorum retained (3)
        Aug 21 12:59:53 [11655] example.redhat.com pacemakerd:     info: pcmk_quorum_notification: 	Membership 12: quorum retained (3)

    Note:
        Because pacemaker timestamps by default have no year, the
        year of the logs will be inferred from the year in your timestamp.
        This will also work around December/January crossovers.

    Examples:
        >>> pm = shared(PacemakerLog)
        >>> pm.get('crmd')
        ['Aug 21 12:59:53 [11661] example.redhat.comm       crmd:     info: pcmk_quorum_notification: 	Membership 12: quorum retained (3)']
        >>> from datetime import datetime
        >>> len(list(pm.get_after(datetime(21, 8, 2017, 12, 59, 50))))
        3
    """
    time_format = '%b %d %H:%M:%S'
