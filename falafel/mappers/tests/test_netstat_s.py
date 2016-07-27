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

        assert info['ip'] == {'total_packets_received': '3405107',
                              'forwarded': '0',
                              'incoming_packets_discarded': '0',
                              'incoming_packets_delivered': '2900146',
                              'requests_sent_out': '2886201',
                              'outgoing_packets_dropped': '456',
                              'fragments_received_ok': '4',
                              'fragments_created': '8'}
        assert info['icmp'] == {'icmp_messages_received': '114',
                                'input_icmp_message_failed': '0',
                                'icmp_input_histogram': {
                                    'destination_unreachable': '107',
                                    'echo_requests': '4',
                                    'echo_replies': '3',
                                },
                                'icmp_messages_sent': '261',
                                'icmp_messages_failed': '0',
                                'icmp_output_histogram': {
                                    'destination_unreachable': '254',
                                    'echo_request': '3',
                                    'echo_replies': '4'
                                }
                                }
        assert info['icmpmsg'] == {'intype0': '3',
                                   'intype3': '107',
                                   'intype8': '4',
                                   'outtype0': '4',
                                   'outtype3': '254',
                                   'outtype8': '3'}
        assert info['tcp'] == {'active_connections_openings': '1648',
                               'passive_connection_openings': '1525',
                               'failed_connection_attempts': '105',
                               'connection_resets_received': '69',
                               'connections_established': '139',
                               'segments_received': '2886370',
                               'segments_send_out': '2890303',
                               'segments_retransmited': '428',
                               'bad_segments_received': '0',
                               'resets_sent': '212'}
        assert info['udp'] == {'packets_received': '4901',
                               'packets_to_unknown_port_received': '107',
                               'packet_receive_errors': '0',
                               'packets_sent': '1793',
                               'receive_buffer_errors': '0',
                               'send_buffer_errors': '0'}
        assert info['udplite'] == {}
        assert info['tcpext'] == {'tcp_sockets_finished_time_wait_in_fast_timer': '1239',
                                  'delayed_acks_sent': '295934',
                                  'delayed_acks_further_delayed_because_of_locked_socket': '6',
                                  'quick_ack_mode_was_activated_times': '9',
                                  'packets_directly_queued_to_recvmsg_prequeue': '999263',
                                  'bytes_directly_in_process_context_from_backlog': '8266',
                                  'bytes_directly_received_in_process_context_from_prequeue': '104052505',
                                  'packet_headers_predicted': '122927',
                                  'packets_header_predicted_and_directly_queued_to_user': '339500',
                                  'acknowledgments_not_containing_data_payload_received': '253351',
                                  'predicted_acknowledgments': '711851',
                                  'times_recovered_from_packet_loss_by_selective_acknowledgements': '1',
                                  'congestion_windows_recovered_without_slow_start_after_partial_ack': '1',
                                  'fast_retransmits': '3',
                                  'other_tcp_timeouts': '54',
                                  'tcplossprobes': '12',
                                  'tcplossproberecovery': '12',
                                  'dsacks_sent_for_old_packets': '9',
                                  'dsacks_received': '13',
                                  'connections_reset_due_to_unexpected_data': '72',
                                  'connections_reset_due_to_early_user_close': '4',
                                  'connections_aborted_due_to_timeout': '53',
                                  'tcpdsackignorednoundo': '13',
                                  'tcpspuriousrtos': '1',
                                  'tcpsackshiftfallback': '6',
                                  'tcpdeferacceptdrop': '537',
                                  'ipreversepathfilter': '1',
                                  'tcprcvcoalesce': '2610',
                                  'tcpofoqueue': '595',
                                  'tcpchallengeack': '3',
                                  'tcpspuriousrtxhostqueues': '3'}
        assert info['ipext'] == {'innoroutes': '9',
                                 'inmcastpkts': '406',
                                 'inbcastpkts': '517437',
                                 'inoctets': '865450302',
                                 'outoctets': '812810111',
                                 'inmcastoctets': '12992',
                                 'inbcastoctets': '46402081'}

    def test_get_netstat_s_fail(self):
        info = get_netstat_s(context_wrap(NETSTAT_S_FAIL))

        assert info == {}

    def test_get_netstat_s_w(self):
        info = get_netstat_s(context_wrap(NETSTAT_S_W))

        assert len(info) == 1
        assert info['ip'] == {'total_packets_received': "6440",
                              "with_invalid_addresses": "3",
                              "forwarded": "0",
                              "incoming_packets_discarded": "0",
                              "incoming_packets_delivered": "6437",
                              "requests_sent_out": "4777"}
