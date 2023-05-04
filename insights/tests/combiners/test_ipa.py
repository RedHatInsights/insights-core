from insights.combiners.ipa import IPA
from insights.parsers.installed_rpms import InstalledRpms
from insights.parsers.ipa_conf import IPAConfig
from insights.parsers.redhat_release import RedhatRelease
from insights.parsers.sssd_conf import SSSD_Config

from insights.tests import context_wrap

REDHAT_RELEASE_RHEL = """
Red Hat Enterprise Linux release 9.2 (Plow)
"""

IPA_RPMS_CLIENT = """
ipa-client-4.10.1-6.el9.x86_64
"""

IPA_RPMS_SERVER = """
ipa-client-4.10.1-6.el9.x86_64
ipa-server-4.10.1-6.el9.x86_64
"""

SSSD_CONF_SERVER = """
[domain/ipa.test]
id_provider = ipa
ipa_server_mode = True
ipa_server = server.ipa.test
ipa_domain = ipa.test
ipa_hostname = server.ipa.test
auth_provider = ipa
chpass_provider = ipa
access_provider = ipa
cache_credentials = True
ldap_tls_cacert = /etc/ipa/ca.crt
krb5_store_password_if_offline = True
sudo_provider = ipa
autofs_provider = ipa
subdomains_provider = ipa
session_provider = ipa
hostid_provider = ipa

[sssd]
domains = ipa.test
"""

IPA_DEFAULT_CONF_SERVER = """
[global]
host = server.ipa.test
basedn = dc=ipahcc,dc=test
realm = ipa.test
domain = ipa.test
xmlrpc_uri = https://server.ipa.test/ipa/xml
ldap_uri = ldapi://%2Frun%2Fslapd-IPAHCC-TEST.socket
mode = production
enable_ra = True
ra_plugin = dogtag
dogtag_version = 10
"""

SSSD_CONF_CLIENT = """
[domain/ipa.test]
id_provider = ipa
ipa_server = _srv_, server.ipa.test
ipa_domain = ipa.test
ipa_hostname = client91.ipa.test
auth_provider = ipa
chpass_provider = ipa
access_provider = ipa
cache_credentials = True
ldap_tls_cacert = /etc/ipa/ca.crt
krb5_store_password_if_offline = True

[sssd]
domains = ipa.test
"""

IPA_DEFAULT_CONF_CLIENT = """
[global]
basedn = dc=ipahcc,dc=test
realm = ipa.test
domain = ipa.test
server = server.ipa.test
host = client91.ipa.test
xmlrpc_uri = https://server.ipa.test/ipa/xml
enable_ra = True
"""


def test_ipa():
    redhat_release = RedhatRelease(context_wrap(REDHAT_RELEASE_RHEL))

    rpms_client = InstalledRpms(context_wrap(IPA_RPMS_CLIENT))
    sssd_conf_client = SSSD_Config(context_wrap(SSSD_CONF_CLIENT))
    ipa_conf_client = IPAConfig(context_wrap(IPA_DEFAULT_CONF_CLIENT))

    rpms_server = InstalledRpms(context_wrap(IPA_RPMS_SERVER))
    sssd_conf_server = SSSD_Config(context_wrap(SSSD_CONF_SERVER))
    ipa_conf_server = IPAConfig(context_wrap(IPA_DEFAULT_CONF_SERVER))

    ipa_client = IPA(
        ipa_conf_client, sssd_conf_client, rpms_client, redhat_release
    )
    assert ipa_client.sssd_conf.domains == [ipa_client.ipa_conf.domain]
    assert ipa_client._is_client is None
    assert ipa_client._is_server is None
    assert ipa_client.is_client
    assert ipa_client._is_client
    assert not ipa_client.is_server
    assert not ipa_client._is_server

    ipa_server = IPA(
        ipa_conf_server, sssd_conf_server, rpms_server, redhat_release
    )
    assert ipa_server.sssd_conf.domains == [ipa_server.ipa_conf.domain]
    assert ipa_server.is_client
    assert ipa_server.is_server

    ipa_mixed = IPA(
        ipa_conf_client, sssd_conf_server, rpms_client, redhat_release
    )
    assert ipa_mixed.sssd_conf.domains == [ipa_mixed.ipa_conf.domain]
    assert ipa_mixed.is_client
    assert not ipa_mixed.is_server
