from .. import LogFileOutput, parser


@parser('pacemaker.log')
class PacemakerLog(LogFileOutput):
    """
    ----------------- example of pacemaker.log --------------------------
    Aug 21 12:58:40 [11656] example.redhat.com        cib:     info: crm_client_destroy: 	Destroying 0 events
    Aug 21 12:59:53 [11655] example.redhat.comm pacemakerd:     info: pcmk_quorum_notification: 	Membership 12: quorum retained (3)
    Aug 21 12:59:53 [11661] example.redhat.comm       crmd:     info: pcmk_quorum_notification: 	Membership 12: quorum retained (3)
    Aug 21 12:59:53 [11655] example.redhat.com  pacemakerd:     info: pcmk_quorum_notification: 	Membership 12: quorum retained (3)
    """
    pass
