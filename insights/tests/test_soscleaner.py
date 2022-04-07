from insights.contrib.soscleaner import SOSCleaner

from mock.mock import Mock
from pytest import mark


def _soscleaner():
    soscleaner = SOSCleaner()
    soscleaner.logger = Mock()
    return soscleaner


@mark.parametrize(("line", "expected"), [
    ("radius_ip_1=10.0.0.1", "radius_ip_1=10.230.230.1"),
    (
        (
            "        inet 10.0.2.15"
            "  netmask 255.255.255.0"
            "  broadcast 10.0.2.255"
        ),
        (
            "        inet 10.230.230.3"
            "  netmask 10.230.230.1"
            "  broadcast 10.230.230.2"
        ),
    ),
    (
        "radius_ip_1=10.0.0.100-10.0.0.200",
        "radius_ip_1=10.230.230.1-10.230.230.2",
    ),
])
def test_sub_ip_match(line, expected):
    soscleaner = _soscleaner()
    actual = soscleaner._sub_ip(line)
    assert actual == expected


@mark.parametrize(("line", "expected"), [
    (
        (
            "        inet 10.0.2.155"
            "  netmask 10.0.2.1"
            "  broadcast 10.0.2.15"
        ),
        (
            "        inet 10.230.230.1"
            "  netmask 10.230.230.3"
            "  broadcast 10.230.230.2"
        ),
    ),
])
def test_sub_ip_match_IP_overlap(line, expected):
    soscleaner = _soscleaner()
    actual = soscleaner._sub_ip(line)
    assert actual == expected


@mark.parametrize(("line", "expected"), [
    (
        "tcp6       0      0 10.0.0.1:23           10.0.0.110:63564   ESTABLISHED 0",
        "tcp6       0      0 10.230.230.2:23       10.230.230.1:63564 ESTABLISHED 0"
    ),
    (
        "tcp6  10.0.0.11    0 10.0.0.1:23       10.0.0.111:63564    ESTABLISHED 0",
        "tcp6  10.230.230.2 0 10.230.230.3:23   10.230.230.1:63564  ESTABLISHED 0"
    ),
    (
        "unix  2      [ ACC ]     STREAM     LISTENING     43279    2070/snmpd         172.31.0.1\n",
        "unix  2      [ ACC ]     STREAM     LISTENING     43279    2070/snmpd         10.230.230.1\n"
    ),
    (
        "unix  2      [ ACC ]     STREAM     LISTENING     43279    2070/snmpd         172.31.111.11\n",
        "unix  2      [ ACC ]     STREAM     LISTENING     43279    2070/snmpd         10.230.230.1 \n"
    ),
])
def test_sub_ip_match_IP_overlap_netstat(line, expected):
    soscleaner = _soscleaner()
    actual = soscleaner._sub_ip_netstat(line)
    assert actual == expected


@mark.xfail
@mark.parametrize(("line",), [
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
    )
])
def test_sub_ip_no_match(line):
    soscleaner = _soscleaner()
    actual = soscleaner._sub_ip(line)
    assert actual == line
