from insights.parsers import hosts, SkipException
from insights.parsers.hosts import Hosts
from insights.tests import context_wrap
import doctest
import pytest

HOSTS_EXAMPLE = """
127.0.0.1 localhost localhost.localdomain localhost4 localhost4.localdomain4
::1 localhost localhost.localdomain localhost6 localhost6.localdomain6

# Comment
127.0.0.1 fte.foo.redhat.com ci.foo.redhat.com qa.foo.redhat.com stage.foo.redhat.com prod.foo.redhat.com # Comment at end of line

10.0.0.1 nonlocal.foo.redhat.com nonlocal2.bar.redhat.com
2001:db8::36    ipv6.example.com

# Hosts with tabs
192.0.2.1	bar.example.com	bar
2001:db8::38	atlas	atlas.example.com
""".strip() + "                  "

HOSTS_DOC = """
127.0.0.1 localhost localhost.localdomain localhost4 localhost4.localdomain4
::1 localhost localhost.localdomain localhost6 localhost6.localdomain6
# The same IP address can appear more than once, with different names
127.0.0.1 fte.example.com

10.0.0.1 nonlocal.example.com nonlocal2.fte.example.com
10.0.0.2 other.host.example.com # Comments at end of line are ignored
""".strip()

EXPECTED = {
    "127.0.0.1": [
        "localhost",
        "localhost.localdomain",
        "localhost4",
        "localhost4.localdomain4",
        "fte.foo.redhat.com",
        "ci.foo.redhat.com",
        "qa.foo.redhat.com",
        "stage.foo.redhat.com",
        "prod.foo.redhat.com"
    ],
    "::1": [
        "localhost",
        "localhost.localdomain",
        "localhost6",
        "localhost6.localdomain6"
    ],
    "10.0.0.1": [
        "nonlocal.foo.redhat.com",
        "nonlocal2.bar.redhat.com"
    ],
    '2001:db8::36': ['ipv6.example.com'],
    '192.0.2.1': ['bar.example.com', 'bar'],
    '2001:db8::38': ['atlas', 'atlas.example.com'],
}


def test_hosts():
    d = Hosts(context_wrap(HOSTS_EXAMPLE)).data
    assert len(d) == 6
    for key in ["127.0.0.1", "::1"]:
        assert key in d
        assert d[key] == EXPECTED[key]


def test_lines():
    l = Hosts(context_wrap(HOSTS_EXAMPLE)).lines
    assert len(l) == 7
    assert l[2]['ip'] == l[0]['ip'] == "127.0.0.1"
    assert l[-1]['names'] == ['atlas', 'atlas.example.com']
    assert l[3]['raw_line'] == '10.0.0.1 nonlocal.foo.redhat.com nonlocal2.bar.redhat.com'


def test_all_hosts():
    h = Hosts(context_wrap(HOSTS_EXAMPLE))
    all_names = h.all_names
    expected = set(EXPECTED["127.0.0.1"]) | set(EXPECTED["::1"]) | \
        set(EXPECTED["10.0.0.1"]) | set(EXPECTED['2001:db8::36']) | \
        set(EXPECTED["192.0.2.1"]) | set(EXPECTED['2001:db8::38'])
    assert all_names == expected
    assert len(h.all_ips) == 6
    assert h.all_ips == set(EXPECTED.keys())


def test_nonlocal():
    ob = Hosts(context_wrap(HOSTS_EXAMPLE))
    expected = {
        "10.0.0.1": EXPECTED["10.0.0.1"],
        '2001:db8::36': EXPECTED['2001:db8::36'],
        '192.0.2.1': EXPECTED['192.0.2.1'],
        '2001:db8::38': EXPECTED['2001:db8::38'],
    }
    assert ob.get_nonlocal() == expected


def test_ip_of():
    ob = Hosts(context_wrap(HOSTS_EXAMPLE))
    # One IP with multiple names
    assert ob.ip_of('localhost4.localdomain4') == '127.0.0.1'
    # IPv6 address, with single name
    assert ob.ip_of('ipv6.example.com') == '2001:db8::36'
    # No host found = None
    assert ob.ip_of('foo.example.com') is None


def test_exception():
    with pytest.raises(SkipException):
        Hosts(context_wrap(""))


def test_doc():
    env = {
            'hosts': Hosts(context_wrap(HOSTS_DOC)),
          }
    failed, total = doctest.testmod(hosts, globs=env)
    assert failed == 0
