import pytest

from insights.core.exceptions import SkipComponent
from insights.combiners.krb5 import AllKrb5Conf
from insights.combiners.identity_domain import (
    IdentityDomain,
    DomainInfo,
    DomainTypes,
    ClientSoftware,
    ServerSoftware,
    IPAMode,
)
from insights.combiners.ipa import IPA
from insights.parsers.installed_rpms import InstalledRpms
from insights.parsers.ipa_conf import IPAConfig
from insights.parsers.krb5 import Krb5Configuration
from insights.parsers.redhat_release import RedhatRelease
from insights.parsers.samba import SambaConfigs
from insights.parsers.sssd_conf import SSSD_Config
from insights.tests import context_wrap

KRB5_CONF = """
[libdefaults]
    dns_lookup_realm = false
    default_realm = IPA.TEST
    dns_canonicalize_hostname = false
    ticket_lifetime = 24h
    renew_lifetime = 7d
    rdns = false

[realms]
    IPA.TEST = {
        pkinit_anchors = FILE:/var/lib/ipa-client/pki/kdc-ca-bundle.pem
        pkinit_pool = FILE:/var/lib/ipa-client/pki/ca-bundle.pem
    }
    KERBEROS-LDAP.TEST = {
        kdc = kdc.kerberos-ldap.test
    }

    KERBEROS.TEST = {
        kdc = kdc.kerberos.test
    }

    # "realm join" for AD  does not add an entry to krb5.conf.
    # AD-WINBIND.TEST = {}
    # AD-SSSD.TEST = {}

[domain_realm]
  .ipa.test = IPA.TEST
  ipa.test = IPA.TEST
"""

SMB_CONF_WINBIND = """
# output of testparm -s
Server role: ROLE_DOMAIN_MEMBER

[global]
    realm = AD-WINBIND.TEST
    security = ADS
    template homedir = /home/%U@%D
    template shell = /bin/bash
    winbind offline logon = Yes
    winbind refresh tickets = Yes
    workgroup = AD-WINBIND
    idmap config * : range = 10000-999999
    idmap config sub1 : backend = rid
    idmap config sub1 : range = 2000000-2999999
    idmap config * : backend = tdb
"""

REDHAT_RELEASE_RHEL = """
Red Hat Enterprise Linux release 9.2 (Plow)
"""

IPA_RPMS_CLIENT = """
ipa-client-4.10.1-6.el9.x86_64
"""

IPA_DEFAULT_CONF = """
[global]
basedn = dc=ipa,dc=test
realm = IPA.TEST
domain = ipa.test
server = server.ipa.test
xmlrpc_uri = https://server.ipa.test/ipa/xml
enable_ra = True
"""

SSSD_CONF = """
[sssd]
domains = ad-sssd.test, ipa.test, kerberos-ldap, ldap
config_file_version = 2
services = nss, pam

[domain/ad-sssd.test]
default_shell = /bin/bash
krb5_store_password_if_offline = True
cache_credentials = True
krb5_realm = AD-SSSD.TEST
realmd_tags = manages-system joined-with-adcli
id_provider = ad
fallback_homedir = /home/%u@%d
ad_domain = ad-sssd.test
use_fully_qualified_names = True
ldap_id_mapping = True
access_provider = ad

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

[domain/kerberos-ldap]
id_provider = ldap
ldap_uri = ldap://ldap.kerberos-ldap.test
ldap_search_base = dc=kerberos-ldap,dc=test
auth_provider = krb5
krb5_server = kdc.kerberos-ldap.test
krb5_realm = KERBEROS-LDAP.TEST

[domain/ldap]
id_provider = ldap
ldap_uri = ldap://ldap.ldap.test
ldap_search_base = dc=ldap,dc=test?subtree?
cache_credentials = true
"""

IPA_DOMAIN = DomainInfo(
    "ipa.test",
    DomainTypes.IPA,
    ServerSoftware.IPA,
    ClientSoftware.SSSD,
    "ipa.test",
    "IPA.TEST",
    None,
    IPAMode.IPA_CLIENT,
)

KERBEROS_LDAP_DOMAIN = DomainInfo(
    "kerberos-ldap",
    DomainTypes.LDAP_KRB5,
    ServerSoftware.LDAP_KRB5,
    ClientSoftware.SSSD,
    None,
    "KERBEROS-LDAP.TEST",
    None,
    None,
)

LDAP_DOMAIN = DomainInfo(
    "ldap",
    DomainTypes.LDAP,
    ServerSoftware.LDAP,
    ClientSoftware.SSSD,
    None,
    None,
    None,
    None,
)

AD_SSSD_DOMAIN = DomainInfo(
    "ad-sssd.test",
    DomainTypes.AD_SSSD,
    ServerSoftware.AD,
    ClientSoftware.SSSD,
    "ad-sssd.test",
    "AD-SSSD.TEST",
    None,
    None,
)

KERBEROS_DOMAIN = DomainInfo(
    "kerberos.test",
    DomainTypes.KRB5,
    ServerSoftware.KRB5,
    ClientSoftware.KRB5,
    None,
    "KERBEROS.TEST",
    None,
    None,
)

AD_WINBIND_DOMAIN = DomainInfo(
    "ad-winbind.test",
    DomainTypes.AD_WINBIND,
    ServerSoftware.AD,
    ClientSoftware.WINBIND,
    "ad-winbind.test",
    "AD-WINBIND.TEST",
    "AD-WINBIND",
    None,
)


def test_identity_domain_sssd():
    krb5 = AllKrb5Conf(
        [Krb5Configuration(context_wrap(KRB5_CONF, path="/etc/krb5.conf"))]
    )
    sssd = SSSD_Config(context_wrap(SSSD_CONF, path="/etc/sssd/sssd.conf"))
    redhat_release = RedhatRelease(context_wrap(REDHAT_RELEASE_RHEL))
    rpms_client = InstalledRpms(context_wrap(IPA_RPMS_CLIENT))
    ipa_conf = IPAConfig(context_wrap(IPA_DEFAULT_CONF, path="/etc/ipa/default.conf"))
    ipa = IPA(ipa_conf, sssd, rpms_client, redhat_release)

    identity_domain = IdentityDomain(sssd, krb5, ipa, None)

    assert identity_domain.domains == [
        AD_SSSD_DOMAIN,
        IPA_DOMAIN,
        KERBEROS_LDAP_DOMAIN,
        LDAP_DOMAIN,
        KERBEROS_DOMAIN,
    ]

    assert identity_domain.default_realm == "IPA.TEST"
    assert identity_domain.dns_lookup_kdc is True
    assert identity_domain.dns_lookup_realm is False


def test_identity_domain_samba():
    smbwb = SambaConfigs(context_wrap(SMB_CONF_WINBIND, path="/etc/samba/smb.conf"))
    identity_domain = IdentityDomain(None, None, None, smbwb)
    assert identity_domain.domains == [AD_WINBIND_DOMAIN]

    assert identity_domain.default_realm is None
    assert identity_domain.dns_lookup_kdc is True
    assert identity_domain.dns_lookup_realm is True


def test_identity_domain_empty():
    with pytest.raises(SkipComponent):
        IdentityDomain(None, None, None, None)
