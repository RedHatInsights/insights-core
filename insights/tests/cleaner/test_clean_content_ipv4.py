from mock.mock import patch
from pytest import mark

from insights.client.config import InsightsConfig
from insights.cleaner import Cleaner


@mark.parametrize(
    ("line", "expected"),
    [
        ("test_no_ip", "test_no_ip"),
        ("test 127.0.0.1", "test 127.0.0.1"),
        ("radius_ip_1=10.0.0.1", "radius_ip_1=10.230.230.1"),
        (
            (
                "        inet 10.0.2.15"
                "  netmask 255.255.255.0"
                "  broadcast 10.0.2.255"
                " dup 10.0.2.15"
            ),
            (
                "        inet 10.230.230.3"
                "  netmask 10.230.230.1"
                "  broadcast 10.230.230.2"
                " dup 10.230.230.3"
            ),
        ),
        (
            ["inet 10.0.2.15", "  netmask 255.255.255.0", " broadcast 10.0.2.255", "dup 10.0.2.15"],
            [
                "inet 10.230.230.1",
                "  netmask 10.230.230.3",
                " broadcast 10.230.230.2",
                "dup 10.230.230.1",
            ],
        ),
        (
            "radius_ip_1=10.0.0.100-10.0.0.200",
            "radius_ip_1=10.230.230.1-10.230.230.2",
        ),
    ],
)
@mark.parametrize(
    ("obfuscate", "obfuscation_list"),
    [
        (True, None),
        (None, ['ipv4']),
    ],
)
def test_obfuscate_ipv4_match(obfuscate, obfuscation_list, line, expected):
    c = InsightsConfig(obfuscate=obfuscate, obfuscation_list=obfuscation_list)
    pp = Cleaner(c, {})
    actual = pp.clean_content(line)
    assert actual == expected


@mark.parametrize(
    ("line", "expected"),
    [
        (
            ("        inet 10.0.2.155" "  netmask 10.0.2.1" "  broadcast 10.0.2.15"),
            ("        inet 10.230.230.1" "  netmask 10.230.230.3" "  broadcast 10.230.230.2"),
        ),
    ],
)
@mark.parametrize(
    ("obfuscate", "obfuscation_list"),
    [
        (True, None),
        (None, ['ipv4']),
    ],
)
def test_obfuscate_ipv4_match_IP_overlap(obfuscate, obfuscation_list, line, expected):
    c = InsightsConfig(obfuscate=obfuscate, obfuscation_list=obfuscation_list)
    pp = Cleaner(c, {})
    actual = pp.clean_content(line)
    assert actual == expected


@mark.parametrize(
    ("line", "expected"),
    [
        ("test_no_ip", "test_no_ip"),
        ("test 127.0.0.1", "test 127.0.0.1"),
        (
            "tcp6       0      0 100.100.100.101:23    10.231.200.1:63564 ESTABLISHED 0",
            "tcp6       0      0 10.230.230.1:23       10.230.230.2:63564 ESTABLISHED 0",
        ),
        (
            "tcp6       0      0 10.0.0.1:23           10.0.0.110:63564   ESTABLISHED 0",
            "tcp6       0      0 10.230.230.2:23       10.230.230.1:63564 ESTABLISHED 0",
        ),
        (
            "tcp6  10.0.0.11    0 10.0.0.1:23       10.0.0.111:63564    ESTABLISHED 0",
            "tcp6  10.230.230.2 0 10.230.230.3:23   10.230.230.1:63564  ESTABLISHED 0",
        ),
        (
            "unix  2      [ ACC ]     STREAM     LISTENING     43279    2070/snmpd         172.31.0.1\n",
            "unix  2      [ ACC ]     STREAM     LISTENING     43279    2070/snmpd         10.230.230.1\n",
        ),
        (
            "unix  2      [ ACC ]     STREAM     LISTENING     43279    2070/snmpd         172.31.111.11\n",
            "unix  2      [ ACC ]     STREAM     LISTENING     43279    2070/snmpd         10.230.230.1 \n",
        ),
    ],
)
@mark.parametrize(
    ("obfuscate", "obfuscation_list"),
    [
        (True, None),
        (None, ['ipv4']),
    ],
)
def test_obfuscate_ipv4_match_IP_overlap_netstat(obfuscate, obfuscation_list, line, expected):
    c = InsightsConfig(obfuscate=obfuscate, obfuscation_list=obfuscation_list)
    pp = Cleaner(c, {})
    actual1 = pp.clean_content(line, width=True)
    assert actual1 == expected


@mark.parametrize(
    ("original", "expected"),
    [
        (
            "{\"name\":\"shadow-utils\","
            "\"epoch\":\"2\","
            "\"version\":\"4.1.5.1\","
            "\"release\":\"5.el6\","
            "\"arch\":\"x86_64\","
            "\"installtime\":\"Wed 13 Jan 2021 10:04:18 AM CET\","
            "\"buildtime\":\"1455012203\","
            "\"vendor\":\"Red Hat, Inc.\","
            "\"buildhost\":\"x86-027.build.eng.bos.redhat.com\","
            "\"sigpgp\":"
            "\"RSA/8, "
            "Tue 08 Mar 2016 11:15:08 AM CET, "
            "Key ID 199e2f91fd431d51\"}",
            "{\"name\":\"shadow-utils\","
            "\"epoch\":\"2\","
            "\"version\":\"10.230.230.1\","
            "\"release\":\"5.el6\","
            "\"arch\":\"x86_64\","
            "\"installtime\":\"Wed 13 Jan 2021 10:04:18 AM CET\","
            "\"buildtime\":\"1455012203\","
            "\"vendor\":\"Red Hat, Inc.\","
            "\"buildhost\":\"x86-027.build.eng.bos.redhat.com\","
            "\"sigpgp\":"
            "\"RSA/8, "
            "Tue 08 Mar 2016 11:15:08 AM CET, "
            "Key ID 199e2f91fd431d51\"}",
        )
    ],
)
@mark.parametrize(
    ("obfuscate", "obfuscation_list"),
    [
        (True, None),
        (None, ['ipv4']),
    ],
)
@patch("insights.cleaner.ip.IPv4._ip2db", return_value="10.230.230.1")
def test_obfuscate_ipv4_false_positive(_ip2db, obfuscate, obfuscation_list, original, expected):
    c = InsightsConfig(obfuscate=obfuscate, obfuscation_list=obfuscation_list)
    pp = Cleaner(c, {})
    actual = pp.clean_content(original)
    assert actual == expected
    # "no_obfuscate=['ipv4']
    actual = pp.clean_content(original, no_obfuscate=['ipv4'])
    assert actual == original
