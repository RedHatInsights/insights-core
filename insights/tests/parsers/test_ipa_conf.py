import doctest

import pytest

from insights.core import NoSectionError
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

IPA_SYSRESTORE_STATE_OLD = """
[dirsrv]
serverid = IPA-TEST
enabled = True
"""

IPA_SYSRESTORE_STATE_NEW = """
[dirsrv]
serverid = IPA-TEST
enabled = True

[installation]
complete = True
"""


def test_doc_examples():
    env = {
        "ipaconfig": ipa_conf.IPAConfig(context_wrap(IPA_DEFAULT_CONF)),
        "oldstate": ipa_conf.IPAServerSysRestoreState(
            context_wrap(IPA_SYSRESTORE_STATE_OLD)
        ),
        "newstate": ipa_conf.IPAServerSysRestoreState(
            context_wrap(IPA_SYSRESTORE_STATE_NEW)
        ),
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


@pytest.mark.parametrize(
    "attr",
    ["basedn", "domain", "jsonrpc_uri", "ldap_uri", "realm", "server", "xmlrpc_uri"]
)
def test_ipa_missing_section(attr):
    cfg = ipa_conf.IPAConfig(context_wrap("[invalid]"))

    with pytest.raises(NoSectionError):
        getattr(cfg, attr)


def test_ipa_missing_settings():
    cfg = ipa_conf.IPAConfig(context_wrap("[global]"))

    with pytest.raises(ValueError):
        cfg.server

    with pytest.raises(ValueError):
        cfg.realm
