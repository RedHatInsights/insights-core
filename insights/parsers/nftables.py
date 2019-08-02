"""
NFTables configuration
======================

Module for processing output of the ``/usr/sbin/nft`` commands.

Parsers included are:

NFTListRules - command ``/usr/sbin/nft list ruleset``
-----------------------------------------------------

"""
from insights import parser, CommandParser
from insights.parsers import SkipException, ParseException
from insights.specs import Specs


@parser(Specs.nft_ruleset)
class NFTListRules(CommandParser, dict):
    """
    This parser parses the output of ``/usr/sbin/nft list ruleset``

    Sample input data looks like::

        table ip filter {
                chain INPUT {
                    type filter hook input priority 0; policy accept;
                    iifname "virbr0" meta l4proto udp udp dport 53 counter packets 0 bytes 0 accept
                    iifname "virbr0" meta l4proto tcp tcp dport 53 counter packets 0 bytes 0 accept
                }
                chain FORWARD {
                    type filter hook forward priority 0; policy accept;
                    oifname "virbr0" ip daddr 192.168.122.0/24 ct state related,established counter packets 0 bytes 0 accept
                    iifname "virbr0" oifname "virbr0" counter packets 0 bytes 0 accept
                }
                chain OUTPUT {
                    type filter hook output priority 0; policy accept;
                    oifname "virbr0" meta l4proto udp udp dport 68 counter packets 0 bytes 0 accept
                }
        }
        table ip6 filter {
                chain INPUT {
                    type filter hook input priority 0; policy accept;
                }
                chain FORWARD {
                    type filter hook forward priority 0; policy accept;
                }
                chain OUTPUT {
                    type filter hook output priority 0; policy accept;
                }
        }

    Raises:
        SkipException: When content is empty.
        ParseException: When content can not be parsed.

    Examples:
        >>> type(nftables)
        <class 'insights.parsers.nftables.NFTListRules'>
        >>> sorted(nftables.tables)
        ['ip filter', 'ip6 filter']
        >>> sorted(nftables.get_chains('ip filter'))
        ['FORWARD', 'INPUT', 'OUTPUT']
        >>> nftables.get_rules('ip6 filter', 'OUTPUT')
        ['type filter hook output priority 0; policy accept;']

    """

    def parse_content(self, content):
        if not content:
            raise SkipException("No Contents")

        tables = {}
        tb_name = ca_name = None
        for line in content:
            line_strip = line.strip()
            if line_strip.startswith('table'):
                tb_name = line_strip.split('table ', 1)[-1].split('{')[0].strip()
                tables[tb_name] = {}
            elif tb_name and line_strip.startswith('chain'):
                ca_name = line_strip.split('chain ', 1)[-1].split('{')[0].strip()
                tables[tb_name][ca_name] = []
            elif tb_name and ca_name and line_strip and '}' != line_strip:
                tables[tb_name][ca_name].append(line_strip)
            elif line.startswith('}') and line.endswith('}'):
                tb_name = None
            elif not line.startswith('}') and line.endswith('}'):
                ca_name = None
            elif line_strip:
                raise ParseException("Content out of table or chain: '{0}'".format(line))

        if not tables:
            raise ParseException("No Parsed Contents")

        self.update(tables)

    @property
    def tables(self):
        """
        (list): Returns the list of tables.
        """
        return sorted(self.keys())

    def get_chains(self, table):
        """
        Get the list of chains of specified `table`

        Args:
           nf_tbl (str): Name of the specified `table`

        Returns:
            (list): List of chains under the `table`
        """
        return sorted(self.get(table, {}).keys())

    def get_rules(self, table, chain):
        """
        Get the list of rules of the specified `chain` under the specified
        `table`.

        Args:
           nf_tbl (str): Name of the specified table
           chain (str): Name of the specified chain

        Returns:
            (list): List of rules of the specified `chain` under the specified `table`
        """
        return self.get(table, {}).get(chain, [])
