"""
Nftables Configurations
=======================

This module includes the following parsers:

NftListRuleSet - command ``nft -j list ruleset``
------------------------------------------------
"""

from collections import defaultdict
import json

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
    To make it easier to use, here it extracts the address_family/table/chain/rule structures and
    save it to main_data attribute.

    The main_data attribute sample::

        {
            'ip': {
                'table1': {
                    'chains': {
                        'chain1': {
                            'attrs': {
                                "family": "ip", "table": "table1", "name": "chain1",
                                "type": "filter", "hook": "input", "prio": 0, "policy": "accept"
                            },
                            'rules': [
                                {
                                    "family": "ip", "table": "table1", "chain": "chain1",
                                    "expr": [
                                        {"vmap": {"key": {"payload":
                                        {"protocol": "ip", "field": "saddr"}},
                                        "data": "@example_map"}}]
                                },
                                {
                                    "family": "ip", "table": "table1", "chain": "chain1",
                                    "expr": [
                                        {"match": {"op": "==",
                                        "left": {"payload": {"protocol": "tcp", "field": "dport"}},
                                        "right": 22}}]
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
        ['table1']
        >>> 'chain1' in nft_obj.chains('ip', 'table1')
        True
        >>> len(nft_obj.rules('ip', 'table1', 'chain1'))
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
                table_name = value.get('table')
                if key == 'table':
                    table_name = value['name']
                    self.main_data[address_name][table_name] = defaultdict(dict)
                elif key == 'chain':
                    chain_name = value['name']
                    self.main_data[address_name][table_name]['chains'][chain_name] = {}
                    self.main_data[address_name][table_name]['chains'][chain_name]['attrs'] = value
                    self.main_data[address_name][table_name]['chains'][chain_name]['rules'] = []
                elif key == 'rule':
                    chain_name = value['chain']
                    self.main_data[address_name][table_name]['chains'][chain_name]['rules'].append(value)
        # transform to normal dict incase non-existing key are added when accessing it
        self.main_data = json.loads(json.dumps(self.main_data))
        if not self.main_data:
            raise SkipComponent

    def tables(self, address_family):
        """dict: Return the tables in some address family."""
        return self.main_data.get(address_family)

    def chains(self, address_family, table_name):
        """dict: Returns the chains in some table."""
        return self.main_data.get(address_family, {}).get(table_name, {}).get('chains')

    def rules(self, address_family, table_name, chain_name):
        """list: Returns the rules of some chain in some table."""
        return self.main_data.get(address_family, {}).get(table_name, {}).get('chains', {}).get(chain_name, {}).get('rules')
