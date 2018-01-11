from insights.parsers.snmp import TcpIpStats
from insights.parsers.snmp import TcpIpStatsIPV6
from insights.tests import context_wrap

PROC_SNMP = """
Ip: Forwarding DefaultTTL InReceives InHdrErrors InAddrErrors ForwDatagrams InUnknownProtos InDiscards InDelivers OutRequests OutDiscards OutNoRoutes ReasmTimeout ReasmReqds ReasmOKs ReasmFails FragOKs FragFails FragCreates
Ip: 2 64 2628 0 2 0 0 0 2624 1618 0 0 0 0 0 10 0 0 0
Icmp: InMsgs InErrors InDestUnreachs InTimeExcds InParmProbs InSrcQuenchs InRedirects InEchos InEchoReps InTimestamps InTimestampReps InAddrMasks InAddrMaskReps OutMsgs OutErrors OutDestUnreachs OutTimeExcds OutParmProbs OutSrcQuenchs OutRedirects OutEchos OutEchoReps OutTimestamps OutTimestampReps OutAddrMasks OutAddrMaskReps
Icmp: 0 0 0 0 0 0 0 0 0 0 0 0 0 2 0 2 0 0 0 0 0 0 0 0 0 0
IcmpMsg: InType3 OutType3
IcmpMsg: 34 44
Tcp: RtoAlgorithm RtoMin RtoMax MaxConn ActiveOpens PassiveOpens AttemptFails EstabResets CurrEstab InSegs OutSegs RetransSegs InErrs OutRsts
Tcp: 1 200 120000 -1 25 4 0 0 1 2529 1520 1 0 9
Udp: InDatagrams NoPorts InErrors OutDatagrams RcvbufErrors SndbufErrors
Udp: 95 0 0 95 1 4
UdpLite: InDatagrams NoPorts InErrors OutDatagrams RcvbufErrors SndbufErrors
UdpLite: 0 10 0 0 0 100
""".strip()

PROC_SNMP_NO = """
""".strip()

PROC_SNMP6 = """
Ip6InReceives                   	757
Ip6InHdrErrors                  	0
Ip6InTooBigErrors               	0
Ip6InNoRoutes                   	0
Ip6InAddrErrors                 	0
Ip6InUnknownProtos              	0
Ip6InTruncatedPkts              	0
Ip6InDiscards                   	0
Ip6InDelivers                   	748
Ip6OutForwDatagrams             	0
Ip6OutRequests                  	713
Ip6OutDiscards                  	0
Ip6OutNoRoutes                  	0
Ip6ReasmTimeout                 	0
Ip6ReasmReqds                   	0
Ip6ReasmOKs                     	0
Ip6ReasmFails                   	0
Ip6FragOKs                      	0
Ip6FragFails                    	0
Ip6FragCreates                  	0
Ip6InMcastPkts                  	99
Ip6OutMcastPkts                 	71
Ip6InOctets                     	579410
Ip6OutOctets                    	1553244
Ip6InMcastOctets                	9224
Ip6OutMcastOctets               	5344
Ip6InBcastOctets                	0
Ip6OutBcastOctets               	0
Ip6InNoECTPkts                  	759
Ip6InECT1Pkts                   	0
Ip6InECT0Pkts                   	0
Ip6InCEPkts                     	0
Icmp6InMsgs                     	94
Icmp6InErrors                   	0
Icmp6OutMsgs                    	41
Icmp6OutErrors                  	0
Icmp6InCsumErrors               	0
Icmp6InDestUnreachs             	0
Icmp6InPktTooBigs               	0
Icmp6InTimeExcds                	0
Icmp6InParmProblems             	0
Icmp6InEchos                    	0
Icmp6InEchoReplies              	0
Icmp6InGroupMembQueries         	28
Icmp6InGroupMembResponses       	0
Icmp6InGroupMembReductions      	0
Icmp6InRouterSolicits           	0
Icmp6InRouterAdvertisements     	62
Icmp6InNeighborSolicits         	3
Icmp6InNeighborAdvertisements   	1
Icmp6InRedirects                	0
Icmp6InMLDv2Reports             	0
Icmp6OutDestUnreachs            	0
Icmp6OutPktTooBigs              	0
Icmp6OutTimeExcds               	0
Icmp6OutParmProblems            	0
Icmp6OutEchos                   	0
Icmp6OutEchoReplies             	0
Icmp6OutGroupMembQueries        	0
Icmp6OutGroupMembResponses      	0
Icmp6OutGroupMembReductions     	0
Icmp6OutRouterSolicits          	1
Icmp6OutRouterAdvertisements    	0
Icmp6OutNeighborSolicits        	3
Icmp6OutNeighborAdvertisements  	3
Icmp6OutRedirects               	0
Icmp6OutMLDv2Reports            	34
Icmp6InType130                  	28
Icmp6InType134                  	62
Icmp6InType135                  	3
Icmp6InType136                  	1
Icmp6OutType133                 	1
Icmp6OutType135                 	3
Icmp6OutType136                 	3
Icmp6OutType143                 	34
Udp6InDatagrams                 	0
Udp6NoPorts                     	0
Udp6InErrors                    	0
Udp6OutDatagrams                	0
Udp6RcvbufErrors                	0
Udp6SndbufErrors                	0
Udp6InCsumErrors                	0
UdpLite6InDatagrams             	0
UdpLite6NoPorts                 	0
UdpLite6InErrors                	0
UdpLite6OutDatagrams            	0
UdpLite6RcvbufErrors            	0
UdpLite6SndbufErrors            	0
UdpLite6InCsumErrors            	0
""".strip()

PROC_SNMP6_ODD = """
Ip6InReceives                   	757
Ip6InHdrErrors                  	0
Icmp6OutMLDv2Reports            	0
Icmp6InType130                  	28
Icmp6InType134                  	62
Ip6InDiscards
""".strip()


def test_snmp():
    stats = TcpIpStats(context_wrap(PROC_SNMP))
    snmp_stats = stats.get("Ip")
    assert snmp_stats
    assert snmp_stats["DefaultTTL"] == 64
    assert snmp_stats["InReceives"] == 2628
    assert snmp_stats["InHdrErrors"] == 0
    assert snmp_stats["InAddrErrors"] == 2
    assert snmp_stats["InDiscards"] == 0
    assert snmp_stats["InDelivers"] == 2624
    assert snmp_stats["ReasmFails"] == 10
    assert snmp_stats["OutRequests"] == 1618

    snmp_stats = stats.get("Tcp")
    assert snmp_stats["RtoMax"] == 120000
    assert snmp_stats["MaxConn"] == -1
    assert snmp_stats["OutSegs"] == 1520
    assert snmp_stats["ActiveOpens"] == 25

    snmp_stats = stats.get("IcmpMsg")
    assert snmp_stats["OutType3"] == 44

    snmp_stats = stats.get("Udp")
    assert snmp_stats["OutDatagrams"] == 95
    assert snmp_stats["RcvbufErrors"] == 1
    assert snmp_stats["NoPorts"] == 0

    stats = TcpIpStats(context_wrap(PROC_SNMP_NO))
    snmp_stats = stats.get("Ip")
    assert snmp_stats is None


def test_snmp6():
    stats = TcpIpStatsIPV6(context_wrap(PROC_SNMP6))
    snmp6_stats_RX = stats.get("Ip6InReceives")
    snmp6_stats_MLD = stats.get("Icmp6OutMLDv2Reports")
    assert snmp6_stats_RX == 757
    assert snmp6_stats_MLD == 34
    stats = TcpIpStatsIPV6(context_wrap(PROC_SNMP6_ODD))
    snmp6_stats_disx = stats.get("Ip6InDiscards")
    snmp6_stats_odd = stats.get("some_unknown")
    assert snmp6_stats_disx is None
    assert snmp6_stats_odd is None
