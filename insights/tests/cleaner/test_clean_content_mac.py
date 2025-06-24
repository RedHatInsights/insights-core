from pytest import mark

from insights.client.config import InsightsConfig
from insights.cleaner import Cleaner


MAC_cases = """
0c:1a:2b:3c:4d:5e           # GOOD
0d-1A-2B-3C-4D-5E           # GOOD
0e:1A:2B:3C:4D:5E           # GOOD
3f:1a-2b:3c:4d:5e           # NG
001a2b3c4d5e                # NG
00:1a:2b:3c:4d              # NG
00:1a:2b:3c:4d:5e:6f        # NG
00:1G:2B:3C:4D:5E           # NG
abc00:1a:2b:3c:4d:5e        # NG
00:1a:2b:3c:4d:5e-xyz"      # NG

Valid MAC 00:1a:2B:3c:4D:5E in lowercase/uppercase  # GOOD
Valid hyphenated 0d-1A-2B-3C-4D-5E                  # GOOD == line-2
Broadcast address FF:FF:FF:FF:FF:FF                 # NG
00:00:00:00:00:00 null address                      # NG
Multicast example 01:00:5E:1a:34:56                 # GOOD
f1:08:5E:12:34:a6 multipule 01:08:5E:12:34:56       # GOOD
Invalid mixed separators 00:1A-2B:3C:4D:5E          # NG
Invalid character 00:1A:2B:3C:4D:5G,                # NG
No separators 001A2B3C4D5E                          # NG
Edge case:MAC=00:11:22:33:44:55=end"                # GOOD
""".strip().splitlines()

MAC_cases_keep_same = """
fe:ab:04:ff:76:4b dev enp3s0 lladdr router STALE - line 1
FE:ab:04:FF:76:4B dev enp3s0 lladdr router STALE - line 2
dev enp3s0 lladdr router fe:ab:04:FF:76:4b
""".strip().splitlines()


@mark.parametrize("obfuscation_list", [[], ['mac']])
def test_obfuscate_mac(obfuscation_list):
    c = InsightsConfig(obfuscation_list=obfuscation_list)
    pp = Cleaner(c, {})
    mac_changed = 0
    ret0 = pp.clean_content(MAC_cases)
    for idx, line in enumerate(ret0):
        org_line = MAC_cases[idx]
        if line != org_line:
            mac_changed += 1
    if obfuscation_list:
        assert mac_changed == len([l for l in MAC_cases if 'GOOD' in l])
    else:
        assert mac_changed == 0
    # No obfuscated address will be obfuscated:
    ret1 = pp.clean_content(ret0)
    assert ret1 == ret0


@mark.parametrize("obfuscation_list", [[], ['mac']])
def test_obfuscate_mac_the_same(obfuscation_list):
    c = InsightsConfig(obfuscation_list=obfuscation_list)
    pp = Cleaner(c, {})
    mac_changed = 0
    ret0 = pp.clean_content(MAC_cases_keep_same)
    for idx, line in enumerate(ret0):
        org_line = MAC_cases_keep_same[idx]
        if line != org_line:
            mac_changed += 1
    if obfuscation_list:
        assert mac_changed == len(MAC_cases_keep_same)
        # Three MACs are obfuscated
        obf_macs = pp.obfuscate.get('mac').mapping()
        assert len(obf_macs) == 3
        # But they are all the same - 1: in result
        ret_mac = obf_macs[0].get('obfuscated').lower()
        # But they are all the same - 2: in mapping
        for mac in obf_macs:
            assert ret_mac == mac['obfuscated'].lower()
    else:
        assert mac_changed == 0
    # No obfuscated address will be obfuscated:
    ret1 = pp.clean_content(ret0)
    assert ret1 == ret0


def test_obfuscate_mac_no_obfuscate():
    c = InsightsConfig(obfuscation_list=['mac'])
    pp = Cleaner(c, {})
    # no_obfuscate=['mac'] will not obfuscate any MAC address
    ret = pp.clean_content(MAC_cases, no_obfuscate=['mac'])
    assert ret == MAC_cases
