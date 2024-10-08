"""
Nftables Configurations
=======================

This module includes the following parsers:

NftListRuleSet - command ``nft -j list ruleset``
------------------------------------------------
"""

from collections import defaultdict

from insights.core import JSONParser
from insights.core.dr import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.nft_list_ruleset)
class NftListRuleSet(JSONParser):
    """
    It parses the output of "nft -j list ruleset".

    Sample output::

        {
            "nftables": [
                {
                    "metainfo": {
                        "version": "0.9.3", "release_name": "Topsy", "json_schema_version": 1
                    }
                },
                {
                    "table": {
                        "family": "ip", "name": "example_table1", "handle": 17
                    }
                },
                {
                    "map": {
                        "family": "ip", "name": "example_map", "table": "example_table1", "type": "ipv4_addr", "handle": 2, "map": "verdict", "elem": [["192.0.2.1", {"accept": null}], ["192.0.2.2", {"drop": null}], ["192.0.2.3", {"accept": null}]]
                    }
                },
                {
                    "set": {
                        "family": "ip", "name": "example_set", "table": "example_table1", "type": "ipv4_addr", "handle": 4
                    }
                },
                {
                    "chain": {
                        "family": "ip", "table": "example_table1", "name": "example_chain1", "handle": 1, "type": "filter", "hook": "input", "prio": 0, "policy": "accept"
                    }
                },
                {
                    "rule": {
                        "family": "ip", "table": "example_table1", "chain": "example_chain1", "handle": 3, "expr": [{"vmap": {"key": {"payload": {"protocol": "ip", "field": "saddr"}}, "data": "@example_map"}}]
                    }
                },
                {
                    "rule": {
                        "family": "ip", "table": "example_table1", "chain": "example_chain1", "handle": 7, "expr": [{"match": {"op": "==", "left": {"payload": {"protocol": "tcp", "field": "dport"}}, "right": 22}}, {"counter": {"packets": 29, "bytes": 1976}}, {"accept": null}]
                    }
                }
            ]
        }

    The json output is dict with a list of all the elements in nftables as the value of the "nftables" key.
    To make it easier to use, here it extracts the address_family/table/chain/rule structures and
    save it to main_data attribute.

    The main_data attribute sample::

        {
            'ip': {
                'example_table1': {
                    'chains': {
                        'example_chain1': {
                            'attrs': {
                                "family": "ip", "table": "example_table1", "name": "example_chain1", "handle": 1, "type": "filter", "hook": "input", "prio": 0, "policy": "accept"
                            },
                            'rules': [
                                {
                                    "family": "ip", "table": "example_table1", "chain": "example_chain1", "handle": 3, "expr": [{"vmap": {"key": {"payload": {"protocol": "ip", "field": "saddr"}}, "data": "@example_map"}}]
                                },
                                {
                                    "family": "ip", "table": "example_table", "chain": "example_chain", "handle": 7, "expr": [{"match": {"op": "==", "left": {"payload": {"protocol": "tcp", "field": "dport"}}, "right": 22}}, {"counter": {"packets": 29, "bytes": 1976}}, {"accept": None}]
                                }
                            ]
                        }
                    }
                }
            }
        }

    Attributes:
        main_data (dict): A dict contains the address_family/table/chain/rule data.

    Raises:
        SkipComponent: No available nftables.

    Examples:
        >>> type(nft_obj)
        <class 'insights.parsers.nftables.NftListRuleSet'>
        >>> [str(key) for key in nft_obj.main_data.keys()]  # to be compatible with python2.6/2.7, transform unicode to string
        ['ip']
        >>> [str(key) for key in nft_obj.main_data['ip'].keys()] # to be compatible with python2.6/2.7, transform unicode to string
        ['example_table1']
        >>> 'example_chain1' in nft_obj.chains('ip', 'example_table1')
        True
        >>> len(nft_obj.rules('ip', 'example_table1', 'example_chain1'))
        2

    """

    def parse_content(self, content):
        """
        There are a lot of other types in nftables besides "chain/rule", like "map", "set", "quota".
        But they are not extracted now since there are no rules dependent on them. If needed,
        we can extract them later.
        """
        super(NftListRuleSet, self).parse_content(content)
        self.main_data = defaultdict(dict)
        for item in self.data['nftables']:
            for key, value in item.items():
                address_name = value.get('family')
                if key == 'table':
                    table_name = value['name']
                    self.main_data[address_name][table_name] = defaultdict(dict)
                else:
                    if key in ['chain', 'rule']:
                        table_name = value['table']
                        if key == 'chain':
                            chain_name = value['name']
                            self.main_data[address_name][table_name]['chains'][chain_name] = {}
                            self.main_data[address_name][table_name]['chains'][chain_name]['attrs'] = value
                            self.main_data[address_name][table_name]['chains'][chain_name]['rules'] = []
                        else:
                            # rule
                            chain_name = value['chain']
                            self.main_data[address_name][table_name]['chains'][chain_name]['rules'].append(value)

        if not self.main_data:
            raise SkipComponent

    def tables(self, address_family):
        """dict: Return the tables in some address family."""
        return self.main_data[address_family]

    def chains(self, address_family, table_name):
        """dict: Returns the chains in some table."""
        return self.main_data[address_family][table_name]['chains']

    def rules(self, address_family, table_name, chain_name):
        """list: Returns the rules of some chain in some table."""
        return self.main_data[address_family][table_name]['chains'][chain_name]['rules']
