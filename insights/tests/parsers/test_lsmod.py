from insights.parsers import lsmod
from insights.tests import context_wrap

LSMODINFO = """
Module                  Size  Used by
xt_CHECKSUM            12549  1
ipt_MASQUERADE         12678  3
nf_nat_masquerade_ipv4    13412  1 ipt_MASQUERADE
tun                    27141  3
ip6t_rpfilter          12546  1
ip6t_REJECT            12939  2
ipt_REJECT             12541  4
xt_conntrack           12760  12
ebtable_nat            12807  0
ebtable_broute         12731  0
bridge                119560  1 ebtable_broute
stp                    12976  1 bridge
llc                    14552  2 stp,bridge
ebtable_filter         12827  0
ebtables               30913  3 ebtable_broute,ebtable_nat,ebtable_filter
ip6table_nat           12864  1
""".strip()


def test_get_modules_info():
    mod_dict = lsmod.LsMod(context_wrap(LSMODINFO))
    assert len(mod_dict.data) == 16
    assert 'xt_CHECKSUM' in mod_dict
    assert mod_dict['tun'].get('depnum') == '3'
    assert mod_dict['llc'].get('deplist') == 'stp,bridge'
    assert mod_dict['ip6table_nat'].get('size') == '12864'
