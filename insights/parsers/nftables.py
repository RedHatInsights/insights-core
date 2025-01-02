"""
Nftables Configurations
=======================

This module includes the following parsers:

NftListRuleSet - command ``nft -j list ruleset``
------------------------------------------------
"""

from insights.core import JSONParser
from insights.core.dr import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs
from insights.parsr import query
from insights.parsr.query import make_child_query as q


@parser(Specs.nft_list_ruleset)
class NftListRuleSet(JSONParser):
    """
    It parses the output of "nft -j list ruleset".

    Sample output::

        {
            "nftables": [
                {
                    "metainfo": {"version": "0.9.3", "release_name": "Topsy", "json_schema_version": 1}
                },
                {
                    "table": {"family": "ip", "name": "table1"}
                },
                {
                    "map": {
                        "family": "ip", "name": "example_map", "table": "table1",
                        "type": "ipv4_addr", "map": "verdict",
                        "elem": [
                            ["192.0.2.1", {"accept": null}],
                            ["192.0.2.2", {"drop": null}],]
                    }
                },
                {
                    "chain": {
                        "family": "ip", "table": "table1", "name": "chain1",
                        "type": "filter", "hook": "input", "prio": 0,
                        "policy": "accept"
                    }
                },
                {
                    "rule": {
                        "family": "ip", "table": "table1", "chain": "chain1",
                        "expr": [
                            {"vmap": {"key": {"payload": {"protocol": "ip", "field": "saddr"}},
                            "data": "@example_map"}}]
                    }
                },
                {
                    "rule": {
                        "family": "ip", "table": "table1", "chain": "chain1",
                        "expr": [
                            {"match": {
                                "op": "==",
                                "left": {"payload": {"protocol": "tcp", "field": "dport"}},
                                "right": 22}}
                        ]
                    }
                }
            ]
        }

    The json output is dict with a single "nftables" key, the value is a list of all data in nftables.
    To make it easier to use, here it makes use of ``insights.parsr.query.Entry`` and transfer the
    data to an Entry object and set it back to the data attribute.

    Attributes:
        data (object): An ``insights.parsr.query.Entry`` object containing all of the data as its
            children.

    Raises:
        SkipComponent: No tables available.

    Examples:
        >>> type(nft_obj)
        <class 'insights.parsers.nftables.NftListRuleSet'>
        >>> [str(item) for item in nft_obj.tables('ip')]   # change unicode to string to be compatible with python2.7
        ['table1']
        >>> chains = nft_obj.chains('ip', 'table1')
        >>> len(chains)
        1
        >>> str(chains[0]['name'].value)  # change unicode to string to be compatible with python2.7
        'chain1'
        >>> str(chains[0]['type'].value)  # change unicode to string to be compatible with python2.7
        'filter'
        >>> rules = nft_obj.rules('ip', 'table1', 'chain1')
        >>> len(rules)
        2
        >>> rules[1]['expr']['match']['right'].value
        22
    """

    def parse_content(self, content):
        super(NftListRuleSet, self).parse_content(content)
        self.data = query.from_dict(self.data)
        if not self.data['nftables']['table']:
            raise SkipComponent

    def tables(self, address_family):
        """list: Return the table names in some address family."""
        return [item['name'].value for item in self.data['nftables']['table'].where('family', address_family)]

    def chains(self, address_family, table_name):
        """list: Returns the chains in some table."""
        return self.data['nftables']['chain'].where(q('family', address_family) & q('table', table_name))

    def rules(self, address_family, table_name, chain_name):
        """list: Returns the rules of some chain in some table."""
        return self.data['nftables']['rule'].where(q('family', address_family) & q('table', table_name) & q('chain', chain_name))
