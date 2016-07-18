from falafel.mappers.netstat_s import get_netstat_s
from falafel.tests import context_wrap
# import json

NETSTAT_S = '''
Ip:
    3405107 total packets received
    0 forwarded
    0 incoming packets discarded
    2900146 incoming packets delivered
    2886201 requests sent out
    456 outgoing packets dropped
    4 fragments received ok
    8 fragments created
Icmp:
    114 ICMP messages received
    0 input ICMP message failed.
    ICMP input histogram:
        destination unreachable: 107
        echo requests: 4
        echo replies: 3
    261 ICMP messages sent
    0 ICMP messages failed
    ICMP output histogram:
        destination unreachable: 254
        echo request: 3
        echo replies: 4
IcmpMsg:
        InType0: 3
        InType3: 107
        InType8: 4
        OutType0: 4
        OutType3: 254
        OutType8: 3
Tcp:
    1648 active connections openings
    1525 passive connection openings
    105 failed connection attempts
    69 connection resets received
    139 connections established
    2886370 segments received
    2890303 segments send out
    428 segments retransmited
    0 bad segments received.
    212 resets sent
Udp:
    4901 packets received
    107 packets to unknown port received.
    0 packet receive errors
    1793 packets sent
    0 receive buffer errors
    0 send buffer errors
UdpLite:
TcpExt:
    1239 TCP sockets finished time wait in fast timer
    295934 delayed acks sent
    6 delayed acks further delayed because of locked socket
    Quick ack mode was activated 9 times
    999263 packets directly queued to recvmsg prequeue.
    8266 bytes directly in process context from backlog
    104052505 bytes directly received in process context from prequeue
    122927 packet headers predicted
    339500 packets header predicted and directly queued to user
    253351 acknowledgments not containing data payload received
    711851 predicted acknowledgments
    1 times recovered from packet loss by selective acknowledgements
    1 congestion windows recovered without slow start after partial ack
    3 fast retransmits
    54 other TCP timeouts
    TCPLossProbes: 12
    TCPLossProbeRecovery: 12
    9 DSACKs sent for old packets
    13 DSACKs received
    72 connections reset due to unexpected data
    4 connections reset due to early user close
    53 connections aborted due to timeout
    TCPDSACKIgnoredNoUndo: 13
    TCPSpuriousRTOs: 1
    TCPSackShiftFallback: 6
    TCPDeferAcceptDrop: 537
    IPReversePathFilter: 1
    TCPRcvCoalesce: 2610
    TCPOFOQueue: 595
    TCPChallengeACK: 3
    TCPSpuriousRtxHostQueues: 3
IpExt:
    InNoRoutes: 9
    InMcastPkts: 406
    InBcastPkts: 517437
    InOctets: 865450302
    OutOctets: 812810111
    InMcastOctets: 12992
    InBcastOctets: 46402081
'''

NETSTAT_S_FAIL = "cannot open /proc/net/snmp: No such file or directory"

NETSTAT_S_W = '''
error parsing /proc/net/netstat: No such file or directory
Ip:
    6440 total packets received
    3 with invalid addresses
    0 forwarded
    0 incoming packets discarded
    6437 incoming packets delivered
    4777 requests sent out
'''


class TestNetstats():
    def test_get_netstat_s(self):
        info = get_netstat_s(context_wrap(NETSTAT_S))
        # print json.dumps(context_wrap(NETSTAT_S).content, indent=4)
        # print json.dumps(info, indent=4)

        assert info['Ip'] == ['3405107 total packets received', \
                              '0 forwarded', \
                              '0 incoming packets discarded', \
                              '2900146 incoming packets delivered', \
                              '2886201 requests sent out', \
                              '456 outgoing packets dropped', \
                              '4 fragments received ok', \
                              '8 fragments created']
        assert info['Icmp'] == ['114 ICMP messages received', \
                                '0 input ICMP message failed.', \
                                'ICMP input histogram:', \
                                'destination unreachable: 107', \
                                'echo requests: 4', \
                                'echo replies: 3', \
                                '261 ICMP messages sent', \
                                '0 ICMP messages failed', \
                                'ICMP output histogram:', \
                                'destination unreachable: 254', \
                                'echo request: 3', \
                                'echo replies: 4']
        assert info['IcmpMsg'] == ['InType0: 3', \
                                   'InType3: 107', \
                                   'InType8: 4', \
                                   'OutType0: 4', \
                                   'OutType3: 254', \
                                   'OutType8: 3']
        assert info['Tcp'] == ['1648 active connections openings', \
                               '1525 passive connection openings', \
                               '105 failed connection attempts', \
                               '69 connection resets received', \
                               '139 connections established', \
                               '2886370 segments received', \
                               '2890303 segments send out', \
                               '428 segments retransmited', \
                               '0 bad segments received.', \
                               '212 resets sent']
        assert info['Udp'] == ['4901 packets received', \
                               '107 packets to unknown port received.', \
                               '0 packet receive errors', \
                               '1793 packets sent', \
                               '0 receive buffer errors', \
                               '0 send buffer errors']
        assert info['UdpLite'] == []
        assert info['TcpExt'] == ['1239 TCP sockets finished time wait in fast timer', \
                                  '295934 delayed acks sent', \
                                  '6 delayed acks further delayed because of locked socket', \
                                  'Quick ack mode was activated 9 times', \
                                  '999263 packets directly queued to recvmsg prequeue.', \
                                  '8266 bytes directly in process context from backlog', \
                                  '104052505 bytes directly received in process context from prequeue', \
                                  '122927 packet headers predicted', \
                                  '339500 packets header predicted and directly queued to user', \
                                  '253351 acknowledgments not containing data payload received', \
                                  '711851 predicted acknowledgments', \
                                  '1 times recovered from packet loss by selective acknowledgements', \
                                  '1 congestion windows recovered without slow start after partial ack', \
                                  '3 fast retransmits', \
                                  '54 other TCP timeouts', \
                                  'TCPLossProbes: 12', \
                                  'TCPLossProbeRecovery: 12', \
                                  '9 DSACKs sent for old packets', \
                                  '13 DSACKs received', \
                                  '72 connections reset due to unexpected data', \
                                  '4 connections reset due to early user close', \
                                  '53 connections aborted due to timeout', \
                                  'TCPDSACKIgnoredNoUndo: 13', \
                                  'TCPSpuriousRTOs: 1', \
                                  'TCPSackShiftFallback: 6', \
                                  'TCPDeferAcceptDrop: 537', \
                                  'IPReversePathFilter: 1', \
                                  'TCPRcvCoalesce: 2610', \
                                  'TCPOFOQueue: 595', \
                                  'TCPChallengeACK: 3', \
                                  'TCPSpuriousRtxHostQueues: 3']
        assert info['IpExt'] == ['InNoRoutes: 9', \
                                'InMcastPkts: 406', \
                                'InBcastPkts: 517437', \
                                'InOctets: 865450302', \
                                'OutOctets: 812810111', \
                                'InMcastOctets: 12992', \
                                'InBcastOctets: 46402081']

    def test_get_netstat_s_fail(self):
        info = get_netstat_s(context_wrap(NETSTAT_S_FAIL))

        assert info == {}

    def test_get_netstat_s_w(self):
        info = get_netstat_s(context_wrap(NETSTAT_S_W))

        assert len(info) == 1
        assert info["Ip"] == ['6440 total packets received', \
                              '3 with invalid addresses', \
                              '0 forwarded', \
                              '0 incoming packets discarded', \
                              '6437 incoming packets delivered', \
                              '4777 requests sent out']
