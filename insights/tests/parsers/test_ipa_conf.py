import doctest

import pytest

from insights.core.exceptions import ParseException
from insights.parsers import ipa_conf
from insights.tests import context_wrap

IPA_DEFAULT_CONF = """
[global]
host = client.ipa.test
basedn = dc=ipa,dc=test
realm = IPA.TEST
domain = ipa.test
xmlrpc_uri = https://server.ipa.test/ipa/xml
"""

IPA_DEFAULT_MINIMAL = """
[global]
realm = IPA.TEST
server = server.ipa.test
"""


def test_doc_examples():
    env = {
        "ipaconfig": ipa_conf.IPAConfig(context_wrap(IPA_DEFAULT_CONF)),
    }
    failed, total = doctest.testmod(ipa_conf, globs=env)
    assert failed == 0


def test_ipa_default_conf():
    cfg = ipa_conf.IPAConfig(context_wrap(IPA_DEFAULT_CONF))

    assert cfg.ipa_section == "global"
    assert cfg.get("global", "host") == "client.ipa.test"

    assert cfg.server == "server.ipa.test"
    assert cfg.domain == "ipa.test"
    assert cfg.realm == "IPA.TEST"
    assert cfg.basedn == "dc=ipa,dc=test"
    assert cfg.ldap_uri == "ldap://server.ipa.test"
    assert cfg.xmlrpc_uri == "https://server.ipa.test/ipa/xml"
    assert cfg.jsonrpc_uri == "https://server.ipa.test/ipa/json"


def test_ipa_default_minimal():
    cfg = ipa_conf.IPAConfig(context_wrap(IPA_DEFAULT_MINIMAL))

    assert cfg.server == "server.ipa.test"
    assert cfg.domain == "ipa.test"
    assert cfg.realm == "IPA.TEST"
    assert cfg.basedn == "dc=ipa,dc=test"
    assert cfg.ldap_uri == "ldap://server.ipa.test"
    assert cfg.xmlrpc_uri == "https://server.ipa.test/ipa/xml"
    assert cfg.jsonrpc_uri == "https://server.ipa.test/ipa/json"


def test_ipa_missing_section():
    with pytest.raises(ParseException):
        ipa_conf.IPAConfig(context_wrap("[invalid]"))


def test_ipa_missing_settings():
    with pytest.raises(ParseException):
        ipa_conf.IPAConfig(context_wrap("[global]"))
