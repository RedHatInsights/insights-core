import pytest
import doctest
from insights.parsers import hostname
from insights.parsers.hostname import Hostname, HostnameShort, HostnameDefault
from insights.tests import context_wrap

HOSTNAME_FULL = "rhel7.example.com"
HOSTNAME_FULL_MULTILINE = """
rhel7.example.com
"""

HOSTNAME_SHORT = "rhel7"
HOSTNAME_SHORT_MULTILINE = """
rhel7
"""


def test_full_hostname():
    data = Hostname(context_wrap(HOSTNAME_FULL))
    assert data.fqdn == "rhel7.example.com"
    assert data.raw == "rhel7.example.com"
    assert data.hostname == "rhel7"
    assert data.domain == "example.com"
    assert "{0}".format(data) == "<raw: rhel7.example.com, hostname: rhel7, domain: example.com>"


def test_full_multiline_hostname():
    data = Hostname(context_wrap(HOSTNAME_FULL_MULTILINE, strip=False))
    assert data.fqdn == "rhel7.example.com"
    assert data.hostname == "rhel7"
    assert data.domain == "example.com"
    assert "{0}".format(data) == "<raw: rhel7.example.com, hostname: rhel7, domain: example.com>"


def test_short_hostname():
    data = HostnameShort(context_wrap(HOSTNAME_SHORT))
    assert data.raw == "rhel7"
    assert data.hostname == "rhel7"
    assert "{0}".format(data) == "<raw: rhel7, hostname: rhel7>"


def test_short_multiline_hostname():
    data = HostnameShort(context_wrap(HOSTNAME_SHORT_MULTILINE, strip=False))
    assert data.raw == "rhel7"
    assert data.hostname == "rhel7"
    assert "{0}".format(data) == "<raw: rhel7, hostname: rhel7>"


def test_default_hostname():
    data = HostnameDefault(context_wrap(HOSTNAME_SHORT))
    assert data.raw == "rhel7"
    assert data.hostname == "rhel7"
    assert "{0}".format(data) == "<raw: rhel7, hostname: rhel7>"


def test_default_multiline_hostname():
    data = HostnameDefault(context_wrap(HOSTNAME_SHORT_MULTILINE, strip=False))
    assert data.raw == "rhel7"
    assert data.hostname == "rhel7"
    assert "{0}".format(data) == "<raw: rhel7, hostname: rhel7>"


def test_empty_hostname():
    with pytest.raises(Exception):
        Hostname(context_wrap(""))


def test_hostname_doc():
    env = {
            'hostname': Hostname(context_wrap(HOSTNAME_FULL)),
            'hostname_def': HostnameDefault(context_wrap(HOSTNAME_SHORT)),
            'hostname_s': HostnameShort(context_wrap(HOSTNAME_SHORT)),
          }
    failed, total = doctest.testmod(hostname, globs=env)
    assert failed == 0
