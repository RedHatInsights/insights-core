from falafel.core.plugins import mapper


@mapper('netstat-s')
def get_netstat_s(context):
    '''
    Return a dict, and each key's value is a list. For example:

    {
        "Udp": [
            "4901 packets received",
            "107 packets to unknown port received.",
            "0 packet receive errors",
            "1793 packets sent",
            "0 receive buffer errors",
            "0 send buffer errors"
        ],
        "TcpExt": [
            "1239 TCP sockets finished time wait in fast timer",
            "295934 delayed acks sent",
            "6 delayed acks further delayed because of locked socket",
            "Quick ack mode was activated 9 times",
            "999263 packets directly queued to recvmsg prequeue.",
            "8266 bytes directly in process context from backlog",
            "104052505 bytes directly received in process context from prequeue",
            "122927 packet headers predicted",
            "339500 packets header predicted and directly queued to user",
            "253351 acknowledgments not containing data payload received",
            "711851 predicted acknowledgments",
            "1 times recovered from packet loss by selective acknowledgements",
            "1 congestion windows recovered without slow start after partial ack",
            "3 fast retransmits",
            "54 other TCP timeouts",
            "TCPLossProbes: 12",
            "TCPLossProbeRecovery: 12",
            "9 DSACKs sent for old packets",
            "13 DSACKs received",
            "72 connections reset due to unexpected data",
            "4 connections reset due to early user close",
            "53 connections aborted due to timeout",
            "TCPDSACKIgnoredNoUndo: 13",
            "TCPSpuriousRTOs: 1",
            "TCPSackShiftFallback: 6",
            "TCPDeferAcceptDrop: 537",
            "IPReversePathFilter: 1",
            "TCPRcvCoalesce: 2610",
            "TCPOFOQueue: 595",
            "TCPChallengeACK: 3",
            "TCPSpuriousRtxHostQueues: 3"
        ],
        ......
        }
    '''
    info = dict()
    session = None
    data = list()

    # There maybe some error metadata, such as:
    # 'cannot open /proc/net/snmp: No such file or directory'
    #or  '/bin/sh: /bin/netstat: No such file or directory'
    # In this situation, return {} directly.
    if 'cannot open' in context.content[0] or 'bin' in context.content[0]:
        return info

    # The right metadata(content) will start with "Ip". Some metadata may start
    # with 'error' or 'ERROR' and the rest of lines are right datas. For example:
    # ~~~~~~~
    # error parsing /proc/net/netstat: No such file or directory
    # Ip:
    #   515 total packets received
    #   5 with invalid addresses
    #   0 forwarded
    #.....
    #~~~~~~~~
    #In this situation, 'error...' line will be ignore.
    for line in context.content:
        if session:
            if line.startswith(' '):
                data.append(line.strip())
            else:
                info[session] = data
                data = list()
                session = None
        if not session:
            session = line.split(":")[0]
            if session.startswith('error') or session.startswith('ERROR'):
                session = None

    # Assign to the last seesion
    info[session] = data
    return info
