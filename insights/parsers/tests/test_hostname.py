import pytest
from insights.parsers.hostname import Hostname
from insights.parsers.hostname import HostnameI
from insights.tests import context_wrap

HOSTNAME = "rhel7.example.com"
HOSTNAME_MULTILINE = """
rhel7.example.com
"""

HOSTNAME_SHORT = "rhel7"
HOSTNAME_SHORT_MULTILINE = """
rhel7
"""

HOSTNAME_I = "10.72.37.146 2620:52:0:4824:21a:4aff:fe16:3d1"
HOSTNAME_I_MULTLINE = """
10.72.37.146 2620:52:0:4824:21a:4aff:fe16:3d1
"""


def test_full_hostname():
    data = Hostname(context_wrap(HOSTNAME))
    assert data.fqdn == "rhel7.example.com"
    assert data.hostname == "rhel7"
    assert data.domain == "example.com"
    assert "{0}".format(data) == "<hostname: rhel7, domain: example.com>" 

def test_full_multiline_hostname():
    data = Hostname(context_wrap(HOSTNAME_MULTILINE, strip=False))
    assert data.fqdn == "rhel7.example.com"
    assert data.hostname == "rhel7"
    assert data.domain == "example.com"
    assert "{0}".format(data) == "<hostname: rhel7, domain: example.com>"


def test_short_hostname():
    data = Hostname(context_wrap(HOSTNAME_SHORT))
    assert data.fqdn == "rhel7"
    assert data.hostname == "rhel7"
    assert data.domain == ""


def test_short_multiline_hostname():
    data = Hostname(context_wrap(HOSTNAME_SHORT_MULTILINE, strip=False))
    assert data.fqdn == "rhel7"
    assert data.hostname == "rhel7"
    assert data.domain == ""


def test_empty_hostname():
    with pytest.raises(Exception):
        Hostname(context_wrap(""))


def test_hostname_I_multiline():
    data = HostnameI(context_wrap(HOSTNAME_I_MULTLINE, strip=False))
    assert data.ipv4 == "10.72.37.146"
    assert data.ipv6 == "2620:52:0:4824:21a:4aff:fe16:3d1"
    assert data.raw == "10.72.37.146 2620:52:0:4824:21a:4aff:fe16:3d1"


def test_hostname_I():
    data = HostnameI(context_wrap(HOSTNAME_I))
    assert data.ipv4 == "10.72.37.146"
    assert data.ipv6 == "2620:52:0:4824:21a:4aff:fe16:3d1"
    assert data.raw == "10.72.37.146 2620:52:0:4824:21a:4aff:fe16:3d1"


def test_hostname_I_exp():
    with pytest.raises(Exception):
        HostnameI(context_wrap(""))
