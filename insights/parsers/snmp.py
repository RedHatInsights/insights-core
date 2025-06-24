"""
snmpd parser
============
Parsers provided by this module are:

TcpIpStats - file ``/proc/net/snmp``
------------------------------------
The ``TcpIpStats`` class implements the parsing of ``/proc/net/snmp``
file, which contains TCP/IP stats of individual layer.

TcpIpStatsIPV6 - file ``/proc/net/snmp6``
-----------------------------------------
The ``TcpIpStatsIPV6`` class implements the parsing of ``/proc/net/snmp6``
file, which contains TCP/IP stats of individual layer.


SnmpdConf - file ``/etc/snmp/snmpd.conf``
-----------------------------------------
The ``SnmpdConf`` class implements the parsing of ``/etc/snmp/snmpd.conf``
file, which is the configuration file for the Net-SNMP SNMP agent.
"""

from insights.core import LegacyItemAccess, Parser
from insights.core.exceptions import ParseException
from insights.core.plugins import parser
from insights.parsers import get_active_lines
from insights.specs import Specs


@parser(Specs.proc_snmp_ipv4)
class TcpIpStats(Parser, LegacyItemAccess):
    """
    Parser for ``/proc/net/snmp`` file.

    Sample input is provided in the *Examples*.

    Examples:

        >>> SNMP_CONTENT = '''
        ... Ip: Forwarding DefaultTTL InReceives InHdrErrors InAddrErrors ForwDatagrams InUnknownProtos InDiscards InDelivers OutRequests OutDiscards OutNoRoutes ReasmTimeout ReasmReqds ReasmOKs ReasmFails FragOKs FragFails FragCreates
        ... Ip: 2 64 43767 0 0 0 0 0 41807 18407 12 73 0 0 0 10 0 0 0
        ... Icmp: InMsgs InErrors InCsumErrors InDestUnreachs InTimeExcds InParmProbs InSrcQuenchs InRedirects InEchos InEchoReps InTimestamps InTimestampReps InAddrMasks InAddrMaskReps OutMsgs OutErrors OutDestUnreachs OutTimeExcds OutParmProbs OutSrcQuenchs OutRedirects OutEchos OutEchoReps OutTimestamps OutTimestampReps OutAddrMasks OutAddrMaskReps
        ... Icmp: 34 0 0 34 0 0 0 0 0 0 0 0 0 0 44 0 44 0 0 0 0 0 0 0 0 0 0
        ... IcmpMsg: InType3 OutType3
        ... IcmpMsg: 34 44
        ... Tcp: RtoAlgorithm RtoMin RtoMax MaxConn ActiveOpens PassiveOpens AttemptFails EstabResets CurrEstab InSegs OutSegs RetransSegs InErrs OutRsts InCsumErrors
        ... Tcp: 1 200 120000 -1 444 0 0 6 7 19269 17050 5 4 234 0
        ... Udp: InDatagrams NoPorts InErrors OutDatagrams RcvbufErrors SndbufErrors InCsumErrors IgnoredMulti
        ... Udp: 18905 34 0 1348 0 0 0 3565
        ... UdpLite: InDatagrams NoPorts InErrors OutDatagrams RcvbufErrors SndbufErrors InCsumErrors IgnoredMulti
        ... UdpLite: 0 0 0 0 0 0 0 0
        ... '''.strip()
        >>> type(proc_snmp_ipv4)
        <class 'insights.parsers.snmp.TcpIpStats'>
        >>> snmp_stats = proc_snmp_ipv4.get("Ip")
        >>> snmp_stats["DefaultTTL"]
        64
        >>> snmp_stats = proc_snmp_ipv4.get("Udp")
        >>> snmp_stats["InDatagrams"]
        18905


    Resultant Data::

        {
            'Ip':
                {
                    'FragCreates': 0,
                    'ReasmFails': 10,
                    'Forwarding': 2,
                    'ReasmOKs': 0,
                    'ReasmReqds': 0,
                    'ReasmTimeout': 0,
                    ...
                    ...
                },
            'Icmp':
                {
                    'InRedirects': 0,
                    'InMsgs': 34,
                    'InSrcQuenchs': 0,
                    ...
                    ...
                }
            ...
            ...
        }
    """
    def parse_content(self, content):
        snmp_stats = {}
        data_id = []
        for line in content:
            line_split = line.split()
            if line_split[1].isdigit():
                snmp_stats[line_split[0].replace(":", "")] = dict(zip(data_id, map(int, line_split[1:])))
            else:
                data_id = line_split[1:]
        self.data = snmp_stats


@parser(Specs.proc_snmp_ipv6)
class TcpIpStatsIPV6(Parser, LegacyItemAccess):
    """
    Parser for ``/proc/net/snmp6`` file.

    Sample input is provided in the *Examples*.

    Examples:

        >>> SNMP_CONTENT = '''
        ... Ip6InReceives                   	757
        ... Ip6InHdrErrors                  	0
        ... Ip6InTooBigErrors               	0
        ... Ip6InNoRoutes                   	0
        ... Ip6InAddrErrors                 	0
        ... Ip6InDiscards                       10
        ... Ip6OutForwDatagrams             	0
        ... Ip6OutDiscards                  	0
        ... Ip6OutNoRoutes                  	0
        ... Ip6InOctets                     	579410
        ... Icmp6OutErrors                  	0
        ... Icmp6InCsumErrors               	0
        ... '''.strip()
        >>> type(proc_snmp_ipv6)
        <class 'insights.parsers.snmp.TcpIpStatsIPV6'>
        >>> IP6_RX_stats = proc_snmp_ipv6.get("Ip6InReceives")
        >>> IP6_RX_stats
        757
        >>> IP6_In_Disc = proc_snmp_ipv6.get("Ip6InDiscards")
        >>> IP6_In_Disc
        10


    Resultant Data::

        {
            'Ip6InReceives': 757,
            'Ip6InHdrErrors': 0,
            'Ip6InTooBigErrors': 0,
            'Ip6InNoRoutes': 0,
            'Ip6InAddrErrors': 0,
            'Ip6InDiscards': 10,
            ...
            ...
        }
    """

    def parse_content(self, content):
        snmp6_stats = {}
        for line in content:
            line_split = line.split()
            snmp6_stats[line_split[0]] = int(line_split[1]) if len(line_split) > 1 and line_split[1] else None
        self.data = snmp6_stats


@parser(Specs.snmpd_conf)
class SnmpdConf(Parser, dict):
    """
    Class for parsing the file ``/etc/snmp/snmpd.conf``

    Sample file content::

        #       sec.name  source          community
        com2sec notConfigUser  default       public

        #       groupName      securityModel securityName
        group   notConfigGroup v1           notConfigUser
        group   notConfigGroup v2c           notConfigUser

        # Make at least  snmpwalk -v 1 localhost -c public system fast again.
        #       name           incl/excl     subtree         mask(optional)
        view    systemview    included   .1.3.6.1.2.1.1
        view    systemview    included   .1.3.6.1.2.1.25.1.1

        #       group          context sec.model sec.level prefix read   write  notif
        access  notConfigGroup ""      any       noauth    exact  systemview none none

        dontLogTCPWrappersConnects yes
        include_ifmib_iface_prefix eth enp1s0

    Examples:
        >>> type(snmpd_conf)
        <class 'insights.parsers.snmp.SnmpdConf'>
        >>> snmpd_conf['dontLogTCPWrappersConnects']
        ['yes']
        >>> snmpd_conf['include_ifmib_iface_prefix']
        ['eth enp1s0']
    """

    def parse_content(self, content):
        content = get_active_lines(content)
        if not content:
            raise ParseException('Empty Content')

        for line in content:
            parts = line.split(None, 1)
            key = parts[0].strip()
            self.setdefault(key, [])
            if len(parts) > 1:
                value = parts[1].strip()
                self[key].append(value)
