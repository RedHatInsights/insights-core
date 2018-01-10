from insights.parsers.snmp import TcpIpStats
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
