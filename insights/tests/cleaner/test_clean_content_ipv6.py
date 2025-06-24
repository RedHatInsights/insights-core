import six
from pytest import mark

try:
    import ipaddress
except Exception:
    from insights.contrib import ipaddress

from insights.client.config import InsightsConfig
from insights.cleaner import Cleaner


IPv6_cases = """
a FE80::2E21:3101:34FB:F580 dev enp3s0 2c:21:31:fb:f5:80 router
X ff02::2 dev enp3s0 lladdr 33:33:00:00:00:02 NOARP
b ff02::16 dev enp3s0 lladdr 33:33:00:00:00:16 NOARP
3 fe80::2204:fff:fe83:7678/64 lladdr 20:04:0f:83:76:78 router
2620:52:0:4996::1fe dev enp3s0 lladdr 2c:21:31:fb:f5:80 STALE
ff02::1:ff47:17 dev enp3s0 lladdr 33:33:ff:47:00:17 NOARP
::1 dev lo lladdr 00:00:00:00:00:00 NOARP
fe80::2204:fff:fe76:224b dev enp3s0 lladdr router STALE - line 1
dev enp3s0 lladdr router 9d8a::5ef5:342:ac2a:ab52
D ::1/32 NOARP
e ::/32 NOARP
F ::ffff:/32 NOARP

fe80::2204:fff:fe76:224b dev enp3s0 lladdr router STALE - line 2
""".strip().splitlines()

IPv6_cases_keep_same = """
fe80::2204:fff:fe76:224b dev enp3s0 lladdr router STALE - line 1
FE80::2204:FFF:FE76:224B dev enp3s0 lladdr router STALE - line 2
dev enp3s0 lladdr router fe80:0000:0000:0000:2204:fff:fe76:224b
dev enp3s0 lladdr router fe80:0:0:0:2204:fff:fe76:224b
""".strip().splitlines()


@mark.parametrize("obfuscation_list", [[], ['ipv6']])
def test_obfuscate_ipv6(obfuscation_list):
    c = InsightsConfig(obfuscation_list=obfuscation_list)
    pp = Cleaner(c, {})
    ip_changed = 0
    len_changed = 0
    ret0 = pp.clean_content(IPv6_cases)
    for idx, line in enumerate(ret0):
        org_line = IPv6_cases[idx]
        if line != org_line:
            ip_changed += 1
        if len(line) != len(org_line):
            len_changed += 1
    if obfuscation_list:
        assert ip_changed == len(IPv6_cases) - 5  # empty and 4 lines of "::" are not obfuscated
        assert len_changed == 0  # length of obfuscated IPv6 is not changed
    else:
        assert ip_changed == 0
        assert len_changed == 0
    # No obfuscated IP address will be obfuscated:
    ret1 = pp.clean_content(ret0)
    assert ret1 == ret0


@mark.parametrize("obfuscation_list", [[], ['ipv6']])
def test_obfuscate_ipv6_the_same(obfuscation_list):
    c = InsightsConfig(obfuscation_list=obfuscation_list)
    pp = Cleaner(c, {})
    ip_changed = 0
    len_changed = 0
    ret0 = pp.clean_content(IPv6_cases_keep_same)
    for idx, line in enumerate(ret0):
        org_line = IPv6_cases_keep_same[idx]
        if line != org_line:
            ip_changed += 1
        if len(line) != len(org_line):
            len_changed += 1
    if obfuscation_list:
        assert len_changed == 0  # length of obfuscated IPv6 is not changed
        assert ip_changed == len(IPv6_cases_keep_same)
        # Four IPs are obfuscated
        obf_ips = pp.obfuscate.get('ipv6').mapping()
        assert len(obf_ips) == 4
        # But they are all the same - 1: in result
        ret_ip = ipaddress.ip_address(
            ret0[0].split()[0] if six.PY3 else u'{0}'.format(ret0[0].split()[0])
        )
        assert ret_ip == ipaddress.ip_address(
            ret0[1].split()[0] if six.PY3 else u'{0}'.format(ret0[1].split()[0])
        )
        assert ret_ip == ipaddress.ip_address(
            ret0[2].split()[-1] if six.PY3 else u'{0}'.format(ret0[2].split()[-1])
        )
        assert ret_ip == ipaddress.ip_address(
            ret0[3].split()[-1] if six.PY3 else u'{0}'.format(ret0[3].split()[-1])
        )
        # But they are all the same - 2: in mapping
        for ip in obf_ips:
            assert (
                ipaddress.ip_address(
                    ip['obfuscated'] if six.PY3 else u'{0}'.format(ip['obfuscated'])
                )
                == ret_ip
            )
    else:
        assert ip_changed == 0
        assert len_changed == 0
    # No obfuscated IP address will be obfuscated:
    ret1 = pp.clean_content(ret0)
    assert ret1 == ret0


def test_obfuscate_ipv6_no_obfuscate():
    c = InsightsConfig(obfuscation_list=['ipv6'])
    pp = Cleaner(c, {})
    # no_obfuscate=['ipv6'] will not obfuscate any IPv6 address
    ret = pp.clean_content(IPv6_cases, no_obfuscate=['ipv6', 'mac'])
    assert ret == IPv6_cases
    # no_obfuscate=['ipv4'] will only obfuscate IPv4 address but not IPv6 address
    pp = Cleaner(c, {})  # Must initialize a new instance
    ret = pp.clean_content(IPv6_cases, no_obfuscate=['ipv4', 'mac'])
    assert ret != IPv6_cases
