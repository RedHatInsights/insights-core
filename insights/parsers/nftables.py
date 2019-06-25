"""
NFTables configuration
======================

Module for processing output of the ``/usr/sbin/nft``.
commands.  Parsers included are:

NFTListRules - command ``/usr/sbin/nft list ruleset``
-----------------------------------------------------

"""


from .. import parser, get_active_lines, CommandParser
from insights.parsers import SkipException, ParseException
from insights.specs import Specs


@parser(Specs.nft_ruleset)
class NFTListRules(CommandParser):

    """
    This parser will parse the output of ``/usr/sbin/nft list ruleset``

    Sample input data looks like::

        table ip filter {
        \t\tchain INPUT {
        \t\t	type filter hook input priority 0; policy accept;
        \t\t	iifname "virbr0" meta l4proto udp udp dport 53 counter packets 0 bytes 0 accept
        \t\t	iifname "virbr0" meta l4proto tcp tcp dport 53 counter packets 0 bytes 0 accept
        \t\t	iifname "virbr0" meta l4proto udp udp dport 67 counter packets 0 bytes 0 accept
        \t\t	iifname "virbr0" meta l4proto tcp tcp dport 67 counter packets 0 bytes 0 accept
        \t\t}
        \t\t
        \t\tchain FORWARD {
        \t\t	type filter hook forward priority 0; policy accept;
        \t\t	oifname "virbr0" ip daddr 192.168.122.0/24 ct state related,established counter packets 0 bytes 0 accept
        \t\t	iifname "virbr0" ip saddr 192.168.122.0/24 counter packets 0 bytes 0 accept
        \t\t	iifname "virbr0" oifname "virbr0" counter packets 0 bytes 0 accept
        \t\t	oifname "virbr0" counter packets 0 bytes 0 reject
        \t\t	iifname "virbr0" counter packets 0 bytes 0 reject
        \t\t}
        \t\t
        \t\tchain OUTPUT {
        \t\t	type filter hook output priority 0; policy accept;
        \t\t	oifname "virbr0" meta l4proto udp udp dport 68 counter packets 0 bytes 0 accept
        \t\t}
        }
        table ip6 filter {
        \t\tchain INPUT {
        \t\t	type filter hook input priority 0; policy accept;
        \t\t}
        \t\t
        \t\tchain FORWARD {
        \t\t	type filter hook forward priority 0; policy accept;
        \t\t}
        \t\t
        \t\tchain OUTPUT {
        \t\t	type filter hook output priority 0; policy accept;
        \t\t}
        }
        table bridge filter {
        \t\tchain INPUT {
        \t\t	type filter hook input priority -200; policy accept;
        \t\t}
        \t\t
        \t\tchain FORWARD {
        \t\t	type filter hook forward priority -200; policy accept;
        \t\t}
        \t\t
        \t\tchain OUTPUT {
        \t\t	type filter hook output priority -200; policy accept;
        \t\t}
        }
        table ip security {
        \t\tchain INPUT {
        \t\t	type filter hook input priority 150; policy accept;
        \t\t}
        \t\t
        \t\tchain FORWARD {
        \t\t	type filter hook forward priority 150; policy accept;
        \t\t}
        \t\t
        \t\tchain OUTPUT {
        \t\t	type filter hook output priority 150; policy accept;
        \t\t}
        }
        table ip raw {
        \t\tchain PREROUTING {
        \t\t	type filter hook prerouting priority -300; policy accept;
        \t\t}
        \t\t
        \t\tchain OUTPUT {
        \t\t	type filter hook output priority -300; policy accept;
        \t\t}
        }
        table ip mangle {
        \t\tchain PREROUTING {
        \t\t	type filter hook prerouting priority -150; policy accept;
        \t\t}
        \t\t
        \t\tchain INPUT {
        \t\t	type filter hook input priority -150; policy accept;
        \t\t}
        \t\t
        \t\tchain FORWARD {
        \t\t	type filter hook forward priority -150; policy accept;
        \t\t}
        \t\t
        \t\tchain OUTPUT {
        \t\t	type route hook output priority -150; policy accept;
        \t\t}
        \t\t
        \t\tchain POSTROUTING {
        \t\t	type filter hook postrouting priority -150; policy accept;
        \t\t	oifname "virbr0" meta l4proto udp udp dport 68 counter packets 0 bytes 0 # CHECKSUM fill
        \t\t}
        }
        table ip nat {
        \t\tchain PREROUTING {
        \t\t	type nat hook prerouting priority -100; policy accept;
        \t\t}
        \t\t
        \t\tchain INPUT {
        \t\t	type nat hook input priority 100; policy accept;
        \t\t}
        \t\t
        \t\tchain POSTROUTING {
        \t\t	type nat hook postrouting priority 100; policy accept;
        \t\t	ip saddr 192.168.122.0/24 ip daddr 224.0.0.0/24 counter packets 3 bytes 232 return
        \t\t	ip saddr 192.168.122.0/24 ip daddr 255.255.255.255 counter packets 0 bytes 0 return
        \t\t	meta l4proto tcp ip saddr 192.168.122.0/24 ip daddr != 192.168.122.0/24 counter packets 0 bytes 0 masquerade to :1024-65535
        \t\t	meta l4proto udp ip saddr 192.168.122.0/24 ip daddr != 192.168.122.0/24 counter packets 0 bytes 0 masquerade to :1024-65535
        \t\t	ip saddr 192.168.122.0/24 ip daddr != 192.168.122.0/24 counter packets 0 bytes 0 masquerade
        \t\t}
        \t\t
        \t\tchain OUTPUT {
        \t\t	type nat hook output priority -100; policy accept;
        \t\t}
        }

    Raises:
        SkipException: When content is empty.
        ParseException: When content can not be parsed.

    Examples:
        >>> type(nftables_obj)
        <class 'insights.parsers.nftables.NFTListRules'>

    """

    def parse_content(self, content):

        if not content:
            raise SkipException("No Contents")

        self.data = {}
        nst_cnt = 0
        idx_key = ''
        idx_key_2 = ''
        for line in get_active_lines(content):
            if line.endswith('{') and nst_cnt == 0:
                idx_key = line.split('{')[0].strip()
                self.data[idx_key] = {}
                nst_cnt += 1
            elif not ((line.endswith('{')) or (line.endswith('}'))) and\
                    idx_key and idx_key_2 and nst_cnt == 2:
                self.data[idx_key][idx_key_2].append(line)
            elif line.endswith('{') and nst_cnt == 1 and idx_key:
                idx_key_2 = line.split('{')[0].strip()
                self.data[idx_key][idx_key_2] = []
                nst_cnt += 1
            elif line.endswith('}') and nst_cnt == 2 and idx_key_2:
                idx_key_2 = ''
                nst_cnt -= 1
            elif line.endswith('}') and nst_cnt == 1 and idx_key:
                idx_key = ''
                nst_cnt -= 1

        if not self.data:
            raise ParseException("No Parsed Contents")

    @property
    def get_nftables(self):
        """
        (list): This will return the list of netfilter tables if exists
        else it will return `[]` emplty list.
        """
        return list(sorted(self.data.keys())) if self.data.keys() else []

    def get_rules(self, nf_tbl, nf_tbl_chain):
        """
        (list): This will return the list of rules added under netfilter table `nf_tbl`
        and chains from the netfilter table `nf_tbl_chain` if exists else it will return
        `[]` emplty list.
        """
        return list(sorted(self.data[nf_tbl][nf_tbl_chain])) if (nf_tbl in self.data) and (nf_tbl_chain in self.data[nf_tbl]) else []
