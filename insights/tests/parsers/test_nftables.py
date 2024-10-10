import doctest
import pytest

from insights.core.dr import SkipComponent
from insights.parsers import nftables
from insights.parsers.nftables import NftListRuleSet
from insights.tests import context_wrap


NTT_LIST_RULESET_DOC = """
{"nftables": [{"metainfo": {"version": "0.9.3", "release_name": "Topsy", "json_schema_version": 1}}, {"table": {"family": "ip", "name": "table1", "handle": 17}}, {"map": {"family": "ip", "name": "example_map", "table": "table1", "type": "ipv4_addr", "handle": 2, "map": "verdict", "elem": [["192.0.2.1", {"accept": null}], ["192.0.2.2", {"drop": null}], ["192.0.2.3", {"accept": null}]]}}, {"set": {"family": "ip", "name": "example_set", "table": "table1", "type": "ipv4_addr", "handle": 4}}, {"chain": {"family": "ip", "table": "table1", "name": "chain1", "handle": 1, "type": "filter", "hook": "input", "prio": 0, "policy": "accept"}}, {"rule": {"family": "ip", "table": "table1", "chain": "chain1", "handle": 3, "expr": [{"vmap": {"key": {"payload": {"protocol": "ip", "field": "saddr"}}, "data": "@example_map"}}]}}, {"rule": {"family": "ip", "table": "table1", "chain": "chain1", "handle": 7, "expr": [{"match": {"op": "==", "left": {"payload": {"protocol": "tcp", "field": "dport"}}, "right": 22}}, {"counter": {"packets": 29, "bytes": 1976}}, {"accept": null}]}}]}
""".strip()

NTT_LIST_RULESET_OUTPU1 = """
{"nftables": [{"metainfo": {"version": "0.9.3", "release_name": "Topsy", "json_schema_version": 1}}, {"table": {"family": "ip", "name": "example_table", "handle": 17}}, {"map": {"family": "ip", "name": "example_map", "table": "example_table", "type": "ipv4_addr", "handle": 2, "map": "verdict", "elem": [["192.0.2.1", {"accept": null}], ["192.0.2.2", {"drop": null}], ["192.0.2.3", {"accept": null}]]}}, {"set": {"family": "ip", "name": "example_set", "table": "example_table", "type": "ipv4_addr", "handle": 4}}, {"chain": {"family": "ip", "table": "example_table", "name": "example_chain", "handle": 1, "type": "filter", "hook": "input", "prio": 0, "policy": "accept"}}, {"rule": {"family": "ip", "table": "example_table", "chain": "example_chain", "handle": 3, "expr": [{"vmap": {"key": {"payload": {"protocol": "ip", "field": "saddr"}}, "data": "@example_map"}}]}}, {"table": {"family": "ip", "name": "nftables_svc", "handle": 18}}, {"chain": {"family": "ip", "table": "nftables_svc", "name": "INPUT", "handle": 1, "type": "filter", "hook": "input", "prio": 0, "policy": "accept"}}, {"rule": {"family": "ip", "table": "nftables_svc", "chain": "INPUT", "handle": 2, "expr": [{"match": {"op": "==", "left": {"payload": {"protocol": "tcp", "field": "dport"}}, "right": 22}}, {"accept": null}]}}, {"rule": {"family": "ip", "table": "nftables_svc", "chain": "INPUT", "handle": 3, "expr": [{"match": {"op": "==", "left": {"payload": {"protocol": "tcp", "field": "dport"}}, "right": 443}}, {"accept": null}]}}, {"rule": {"family": "ip", "table": "nftables_svc", "chain": "INPUT", "handle": 4, "expr": [{"reject": null}]}}]}
""".strip()

NTT_LIST_RULESET_TWO_CHAINS = """
{"nftables": [{"metainfo": {"version": "0.9.3", "release_name": "Topsy", "json_schema_version": 1}}, {"table": {"family": "ip", "name": "example_table", "handle": 17}}, {"map": {"family": "ip", "name": "example_map", "table": "example_table", "type": "ipv4_addr", "handle": 2, "map": "verdict", "elem": [["192.0.2.1", {"accept": null}], ["192.0.2.2", {"drop": null}], ["192.0.2.3", {"accept": null}]]}}, {"set": {"family": "ip", "name": "example_set", "table": "example_table", "type": "ipv4_addr", "handle": 4}}, {"chain": {"family": "ip", "table": "example_table", "name": "example_chain", "handle": 1, "type": "filter", "hook": "input", "prio": 0, "policy": "accept"}}, {"rule": {"family": "ip", "table": "example_table", "chain": "example_chain", "handle": 3, "expr": [{"vmap": {"key": {"payload": {"protocol": "ip", "field": "saddr"}}, "data": "@example_map"}}]}}, {"rule": {"family": "ip", "table": "example_table", "chain": "example_chain", "handle": 7, "expr": [{"match": {"op": "==", "left": {"payload": {"protocol": "tcp", "field": "dport"}}, "right": 22}}, {"counter": {"packets": 808, "bytes": 61250}}, {"accept": null}]}}, {"chain": {"family": "ip", "table": "example_table", "name": "postrouting", "handle": 8, "type": "nat", "hook": "postrouting", "prio": 100, "policy": "accept"}}, {"rule": {"family": "ip", "table": "example_table", "chain": "postrouting", "handle": 9, "expr": [{"match": {"op": "==", "left": {"payload": {"protocol": "tcp", "field": "dport"}}, "right": 22}}, {"accept": null}]}}]}
""".strip()

EMPTY_OUTPUT = """
{"nftables": [{"metainfo": {"version": "0.9.3", "release_name": "Topsy", "json_schema_version": 1}}]}
""".strip()


def test_module_documentation():
    failed, _ = doctest.testmod(
        nftables,
        globs={
            "nft_obj": NftListRuleSet(context_wrap(NTT_LIST_RULESET_DOC))
        }
    )
    assert failed == 0


def test_nft_list_ruleset():
    nft_obj = NftListRuleSet(context_wrap(NTT_LIST_RULESET_OUTPU1))
    assert len(nft_obj.main_data) == 1
    assert 'ip' in nft_obj.main_data

    tables = nft_obj.tables('ip')
    assert len(tables) == 2
    assert 'example_table' in tables
    assert 'nftables_svc' in tables

    chains = nft_obj.chains('ip', 'example_table')
    assert len(chains) == 1
    assert 'example_chain' in chains

    assert chains['example_chain']['attrs']['type'] == 'filter'
    assert chains['example_chain']['attrs']['hook'] == 'input'
    assert chains['example_chain']['attrs']['prio'] == 0
    assert chains['example_chain']['attrs']['policy'] == 'accept'

    example_chain_rules = nft_obj.rules('ip', 'example_table', 'example_chain')
    assert len(example_chain_rules) == 1
    # {"rule": {"family": "ip", "table": "example_table", "chain": "example_chain", "handle": 3, "expr": [{"vmap": {"key": {"payload": {"protocol": "ip", "field": "saddr"}}, "data": "@example_map"}}]}}
    assert 'vmap' in example_chain_rules[0]['expr'][0]
    assert example_chain_rules[0]['expr'][0]['vmap']['key']['payload']['protocol'] == 'ip'
    assert example_chain_rules[0]['expr'][0]['vmap']['key']['payload']['field'] == 'saddr'
    assert example_chain_rules[0]['expr'][0]['vmap']['data'] == '@example_map'

    svc_chains = nft_obj.chains('ip', 'nftables_svc')
    assert len(svc_chains) == 1
    assert 'INPUT' in svc_chains

    nftables_svc_input_rules = nft_obj.rules('ip', 'nftables_svc', 'INPUT')
    assert len(nftables_svc_input_rules) == 3
    # {"rule": {"family": "ip", "table": "nftables_svc", "chain": "INPUT", "handle": 2, "expr": [{"match": {"op": "==", "left": {"payload": {"protocol": "tcp", "field": "dport"}}, "right": 22}}, {"accept": null}]}}
    first_rule = nftables_svc_input_rules[0]
    assert first_rule['expr'][0]['match']['left']['payload']['protocol'] == 'tcp'
    assert first_rule['expr'][0]['match']['left']['payload']['field'] == 'dport'
    assert first_rule['expr'][0]['match']['op'] == '=='
    assert first_rule['expr'][0]['match']['right'] == 22
    assert first_rule['expr'][1]['accept'] is None
    # {"rule": {"family": "ip", "table": "nftables_svc", "chain": "INPUT", "handle": 3, "expr": [{"match": {"op": "==", "left": {"payload": {"protocol": "tcp", "field": "dport"}}, "right": 443}}, {"accept": null}]}}
    second_rule = nftables_svc_input_rules[1]
    assert second_rule['expr'][0]['match']['left']['payload']['protocol'] == 'tcp'
    assert second_rule['expr'][0]['match']['left']['payload']['field'] == 'dport'
    assert second_rule['expr'][0]['match']['op'] == '=='
    assert second_rule['expr'][0]['match']['right'] == 443
    assert second_rule['expr'][1]['accept'] is None
    # {"rule": {"family": "ip", "table": "nftables_svc", "chain": "INPUT", "handle": 4, "expr": [{"reject": null}]}}
    third_rule = nftables_svc_input_rules[2]
    assert third_rule['expr'][0]['reject'] is None

    # test map info in data
    # {"map": {"family": "ip", "name": "example_map", "table": "example_table", "type": "ipv4_addr", "handle": 2, "map": "verdict", "elem": [["192.0.2.1", {"accept": null}], ["192.0.2.2", {"drop": null}], ["192.0.2.3", {"accept": null}]]}}
    assert 'map' in nft_obj.data['nftables'][2]
    map_info = nft_obj.data['nftables'][2]['map']
    assert map_info['name'] == 'example_map'
    assert map_info['table'] == 'example_table'
    assert map_info['type'] == 'ipv4_addr'
    assert map_info['map'] == 'verdict'
    assert len(map_info['elem']) == 3
    map_eles = map_info['elem']
    assert '192.0.2.1' in map_eles[0]
    assert '192.0.2.2' in map_eles[1]
    assert '192.0.2.3' in map_eles[2]

    # test set info in data
    # {"set": {"family": "ip", "name": "example_set", "table": "example_table", "type": "ipv4_addr", "handle": 4}}
    assert 'set' in nft_obj.data['nftables'][3]
    set_info = nft_obj.data['nftables'][3]['set']
    assert set_info['name'] == 'example_set'
    assert set_info['table'] == 'example_table'
    assert set_info['type'] == 'ipv4_addr'

    nft2_obj = NftListRuleSet(context_wrap(NTT_LIST_RULESET_TWO_CHAINS))
    chains = nft2_obj.chains('ip', 'example_table')
    assert len(chains) == 2
    assert 'postrouting' in chains
    rules = nft2_obj.rules('ip', 'example_table', 'postrouting')
    assert len(rules) == 1
    first_rule = rules[0]
    # {"rule": {"family": "ip", "table": "example_table", "chain": "postrouting", "handle": 9, "expr": [{"match": {"op": "==", "left": {"payload": {"protocol": "tcp", "field": "dport"}}, "right": 22}}, {"accept": null}]}}
    assert first_rule['expr'][0]['match']['left']['payload']['protocol'] == 'tcp'
    assert first_rule['expr'][0]['match']['left']['payload']['field'] == 'dport'
    assert first_rule['expr'][0]['match']['op'] == '=='
    assert first_rule['expr'][0]['match']['right'] == 22
    assert first_rule['expr'][1]['accept'] is None

    assert nft2_obj.tables('non_exist_ip') is None
    assert nft2_obj.chains('ip', 'non_exist_table') is None
    assert nft2_obj.rules('ip', 'example_table', 'non_exist_chain') is None


def test_except_in_nft_list_ruleset():
    with pytest.raises(SkipComponent):
        NftListRuleSet(context_wrap(EMPTY_OUTPUT))
