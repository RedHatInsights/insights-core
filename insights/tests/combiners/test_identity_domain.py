import textwrap

import pytest

from insights.combiners.identity_domain import (
    ClientSoftware,
    DomainTypes,
    IdentityDomain,
    IPAMode,
    ServerSoftware,
)
from insights.combiners.ipa import IPA
from insights.combiners.krb5 import AllKrb5Conf
from insights.combiners.sssd_conf import SSSDConfAll
from insights.core.exceptions import SkipComponent
from insights.parsers.installed_rpms import InstalledRpms
from insights.parsers.ipa_conf import IPAConfig
from insights.parsers.krb5 import Krb5Configuration
from insights.parsers.samba import SambaConfigs
from insights.parsers.sssd_conf import SSSDConf
from insights.tests import context_wrap


def test_identity_domain__sssd_ldap():
    sssd_conf = textwrap.dedent(
        """
        [sssd]
        domains = ldap.test

        [domain/ldap.test]
        id_provider = ldap
        """
    ).strip()

    sssd_conf = SSSDConfAll(
        SSSDConf(context_wrap(sssd_conf, "/etc/sssd/sssd.conf")), []
    )

    identity_domain = IdentityDomain(sssd_conf, None, None, None)

    assert len(identity_domain.domains) == 1
    domain = identity_domain.domains[0]

    assert domain.name == "ldap.test"
    assert domain.domain_type == DomainTypes.LDAP
    assert domain.server_software == ServerSoftware.LDAP
    assert domain.client_software == ClientSoftware.SSSD
    assert domain.domain is None
    assert domain.realm is None
    assert domain.workgroup is None
    assert domain.ipa_mode is None

    assert identity_domain.default_realm is None
    assert identity_domain.dns_lookup_kdc is True
    assert identity_domain.dns_lookup_realm is True


@pytest.mark.parametrize(
    "explicit_realm", [True, False], ids=["realm_set", "realm_unset"]
)
def test_identity_domain__sssd_ldap_krb5(explicit_realm):
    realm = "LDAP.TEST" if not explicit_realm else "MYREALM"

    krb5_conf = textwrap.dedent(
        """
        [libdefaults]
          default_realm = {realm}

        [realms]
          {realm} = {{
              kdc = kdc.realm1.test
          }}
        [domain_realm]
        """.format(
            realm=realm
        )
    ).strip()

    sssd_conf = textwrap.dedent(
        """
        [sssd]
        domains = ldap.test

        [domain/ldap.test]
        id_provider = ldap
        auth_provider = krb5
        """
    ).strip()

    if explicit_realm:
        sssd_conf += "\nkrb5_realm = " + realm

    sssd_conf = SSSDConfAll(
        SSSDConf(context_wrap(sssd_conf, "/etc/sssd/sssd.conf")), []
    )
    krb5_conf = AllKrb5Conf(
        [Krb5Configuration(context_wrap(krb5_conf, path="/etc/krb5.conf"))]
    )
    identity_domain = IdentityDomain(sssd_conf, krb5_conf, None, None)

    assert len(identity_domain.domains) == 1
    domain = identity_domain.domains[0]

    assert domain.name == "ldap.test"
    assert domain.domain_type == DomainTypes.LDAP_KRB5
    assert domain.server_software == ServerSoftware.LDAP_KRB5
    assert domain.client_software == ClientSoftware.SSSD
    assert domain.domain is None
    assert domain.realm == realm
    assert domain.workgroup is None
    assert domain.ipa_mode is None

    assert identity_domain.default_realm == realm
    assert identity_domain.dns_lookup_kdc is True
    assert identity_domain.dns_lookup_realm is True


@pytest.mark.parametrize(
    "explicit_realm", [True, False], ids=["realm_set", "realm_unset"]
)
@pytest.mark.parametrize("ipa_server", [True, False], ids=["ipa_server", "ipa_client"])
@pytest.mark.parametrize("sssd_domain", ["ipa.test", "IPA"])
def test_identity_domain__sssd_ipa(explicit_realm, ipa_server, sssd_domain):
    realm = "IPA.TEST" if not explicit_realm else "MYREALM"

    ipa_conf = textwrap.dedent(
        """
        [global]
        basedn = dc=ipahcc,dc=test
        realm = {realm}
        domain = ipa.test
        server = server.ipa.test
        host = client91.ipa.test
        xmlrpc_uri = https://server.ipa.test/ipa/xml
        enable_ra = True
        """.format(
            realm=realm
        )
    ).strip()

    krb5_conf = textwrap.dedent(
        """
        [libdefaults]
           dns_lookup_realm = true
           dns_lookup_kdc = true
           default_realm = {realm}
           dns_canonicalize_hostname = false
           ticket_lifetime = 24h
           renew_lifetime = 7d
           rdns = false

        [realms]
          {realm} = {{
              pkinit_anchors = FILE:/var/lib/ipa-client/pki/kdc-ca-bundle.pem
              pkinit_pool = FILE:/var/lib/ipa-client/pki/ca-bundle.pem
          }}

        [domain_realm]
        .ipa.test = {realm}
        ipa.test = {realm}
        """.format(
            realm=realm
        )
    ).strip()

    sssd_conf = textwrap.dedent(
        """
        [sssd]
        domains = {domain}

        [domain/{domain}]
        id_provider = ipa
        ipa_server_mode = false
        """.format(
            domain=sssd_domain
        )
    ).strip()

    sssd_conf += "\nipa_server_mode = " + str(ipa_server)

    if explicit_realm:
        sssd_conf += "\nkrb5_realm = " + realm

    if sssd_domain != "ipa.test":
        sssd_conf += "\nipa_domain = ipa.test"

    rpms = InstalledRpms(context_wrap("sssd-2.9.1-1.el9.x86_64"))
    ipa_conf = IPAConfig(context_wrap(ipa_conf))
    sssd_conf = SSSDConfAll(
        SSSDConf(context_wrap(sssd_conf, "/etc/sssd/sssd.conf")), []
    )
    krb5_conf = AllKrb5Conf(
        [Krb5Configuration(context_wrap(krb5_conf, path="/etc/krb5.conf"))]
    )
    ipa = IPA(ipa_conf, sssd_conf, rpms)

    identity_domain = IdentityDomain(sssd_conf, krb5_conf, ipa, None)
    ipa_mode = IPAMode.IPA_SERVER if ipa_server else IPAMode.IPA_CLIENT

    assert len(identity_domain.domains) == 1
    domain = identity_domain.domains[0]

    assert domain.name == sssd_domain
    assert domain.domain_type == DomainTypes.IPA
    assert domain.server_software == ServerSoftware.IPA
    assert domain.client_software == ClientSoftware.SSSD
    assert domain.domain == "ipa.test"
    assert domain.realm == realm
    assert domain.workgroup is None
    assert domain.ipa_mode is ipa_mode

    assert identity_domain.default_realm == realm
    assert identity_domain.dns_lookup_kdc is True
    assert identity_domain.dns_lookup_realm is True


@pytest.mark.parametrize(
    "explicit_realm", [True, False], ids=["realm_set", "realm_unset"]
)
@pytest.mark.parametrize("sssd_domain", ["ad.test", "AD"])
def test_identity_domain__sssd_ad(explicit_realm, sssd_domain):
    realm = "AD.TEST" if not explicit_realm else "MYREALM"

    sssd_conf = textwrap.dedent(
        """
        [sssd]
        domains = {domain}

        [domain/{domain}]
        id_provider = ad
        """.format(
            domain=sssd_domain
        )
    ).strip()

    if explicit_realm:
        sssd_conf += "\nkrb5_realm = " + realm

    if sssd_domain != "ad.test":
        sssd_conf += "\nad_domain = ad.test"

    sssd_conf = SSSDConfAll(
        SSSDConf(context_wrap(sssd_conf, "/etc/sssd/sssd.conf")), []
    )

    identity_domain = IdentityDomain(sssd_conf, None, None, None)

    assert len(identity_domain.domains) == 1
    domain = identity_domain.domains[0]

    assert domain.name == sssd_domain
    assert domain.domain_type == DomainTypes.AD_SSSD
    assert domain.server_software == ServerSoftware.AD
    assert domain.client_software == ClientSoftware.SSSD
    assert domain.domain == "ad.test"
    assert domain.realm == realm
    assert domain.workgroup is None
    assert domain.ipa_mode is None

    assert identity_domain.default_realm is None
    assert identity_domain.dns_lookup_kdc is True
    assert identity_domain.dns_lookup_realm is True


@pytest.mark.parametrize(
    "explicit_workgroup", [True, False], ids=["workgroup_set", "workgroup_unset"]
)
def test_identity_domain__winbind_ad(explicit_workgroup):
    smb_conf = textwrap.dedent(
        """
        # output of testparm -s
        Server role: ROLE_DOMAIN_MEMBER

        [global]
            realm = AD-WINBIND.TEST
            security = ADS
            template homedir = /home/%U@%D
            template shell = /bin/bash
            winbind offline logon = Yes
            winbind refresh tickets = Yes
            idmap config * : range = 10000-999999
            idmap config sub1 : backend = rid
            idmap config sub1 : range = 2000000-2999999
            idmap config * : backend = tdb
        """
    ).strip()

    if explicit_workgroup:
        smb_conf += "\n    workgroup = MYWORKGROUP"

    smb_conf = SambaConfigs(context_wrap(smb_conf, path="/etc/samba/smb.conf"))
    identity_domain = IdentityDomain(None, None, None, smb_conf)
    workgroup = "AD-WINBIND" if not explicit_workgroup else "MYWORKGROUP"

    assert len(identity_domain.domains) == 1
    domain = identity_domain.domains[0]

    assert domain.name == "ad-winbind.test"
    assert domain.domain_type == DomainTypes.AD_WINBIND
    assert domain.server_software == ServerSoftware.AD
    assert domain.client_software == ClientSoftware.WINBIND
    assert domain.domain == "ad-winbind.test"
    assert domain.realm == "AD-WINBIND.TEST"
    assert domain.workgroup == workgroup
    assert domain.ipa_mode is None

    assert identity_domain.default_realm is None
    assert identity_domain.dns_lookup_kdc is True
    assert identity_domain.dns_lookup_realm is True


@pytest.mark.parametrize(
    "dns_lookup_realm",
    [True, False],
    ids=["dns_lookup_realm_true", "dns_lookup_realm_false"],
)
@pytest.mark.parametrize(
    "dns_lookup_kdc", [True, False], ids=["dns_lookup_kdc_true", "dns_lookup_kdc_false"]
)
def test_identity_domain__krb5_one_realm(dns_lookup_realm, dns_lookup_kdc):
    krb5_conf = textwrap.dedent(
        """
        [libdefaults]
          dns_lookup_realm = {dns_lookup_realm}
          dns_lookup_kdc = {dns_lookup_kdc}
          default_realm = KERBEROS.TEST

        [realms]
          KERBEROS.TEST = {{
              kdc = kdc.kerberos.test
          }}

        [domain_realm]
          .kerberos.test = KERBEROS.TEST
          kerberos.test = KERBEROS.TEST
        """.format(
            dns_lookup_realm=str(dns_lookup_realm).lower(),
            dns_lookup_kdc=str(dns_lookup_kdc).lower(),
        )
    ).strip()

    krb5_conf = AllKrb5Conf(
        [Krb5Configuration(context_wrap(krb5_conf, path="/etc/krb5.conf"))]
    )

    identity_domain = IdentityDomain(None, krb5_conf, None, None)

    assert len(identity_domain.domains) == 1
    domain = identity_domain.domains[0]

    assert domain.name == "kerberos.test"
    assert domain.domain_type == DomainTypes.KRB5
    assert domain.server_software == ServerSoftware.KRB5
    assert domain.client_software == ClientSoftware.KRB5
    assert domain.domain is None
    assert domain.realm == "KERBEROS.TEST"
    assert domain.workgroup is None
    assert domain.ipa_mode is None

    assert identity_domain.default_realm == "KERBEROS.TEST"
    assert identity_domain.dns_lookup_kdc is dns_lookup_kdc
    assert identity_domain.dns_lookup_realm is dns_lookup_realm


@pytest.mark.parametrize(
    "dns_lookup_realm",
    [True, False],
    ids=["dns_lookup_realm_true", "dns_lookup_realm_false"],
)
@pytest.mark.parametrize(
    "dns_lookup_kdc", [True, False], ids=["dns_lookup_kdc_true", "dns_lookup_kdc_false"]
)
def test_identity_domain__krb5_multi_realm(dns_lookup_realm, dns_lookup_kdc):
    krb5_conf = textwrap.dedent(
        """
        [libdefaults]
          dns_lookup_realm = {dns_lookup_realm}
          dns_lookup_kdc = {dns_lookup_kdc}
          default_realm = REALM2.TEST

        [realms]
          REALM1.TEST = {{
              kdc = kdc.realm1.test
          }}

          REALM2.TEST = {{
              kdc = kdc.realm2.test
          }}

        [domain_realm]
        """.format(
            dns_lookup_realm=str(dns_lookup_realm).lower(),
            dns_lookup_kdc=str(dns_lookup_kdc).lower(),
        )
    ).strip()

    krb5_conf = AllKrb5Conf(
        [Krb5Configuration(context_wrap(krb5_conf, path="/etc/krb5.conf"))]
    )

    identity_domain = IdentityDomain(None, krb5_conf, None, None)

    assert len(identity_domain.domains) == 2

    domain = identity_domain.domains[0]
    assert domain.name == "realm1.test"
    assert domain.domain_type == DomainTypes.KRB5
    assert domain.server_software == ServerSoftware.KRB5
    assert domain.client_software == ClientSoftware.KRB5
    assert domain.domain is None
    assert domain.realm == "REALM1.TEST"
    assert domain.workgroup is None
    assert domain.ipa_mode is None

    domain = identity_domain.domains[1]
    assert domain.name == "realm2.test"
    assert domain.domain_type == DomainTypes.KRB5
    assert domain.server_software == ServerSoftware.KRB5
    assert domain.client_software == ClientSoftware.KRB5
    assert domain.domain is None
    assert domain.realm == "REALM2.TEST"
    assert domain.workgroup is None
    assert domain.ipa_mode is None

    assert identity_domain.default_realm == "REALM2.TEST"
    assert identity_domain.dns_lookup_kdc is dns_lookup_kdc
    assert identity_domain.dns_lookup_realm is dns_lookup_realm


def test_identity_domain__multi_domain():
    ipa_conf = textwrap.dedent(
        """
        [global]
        basedn = dc=ipahcc,dc=test
        realm = IPA.TEST
        domain = ipa.test
        server = server.ipa.test
        host = client91.ipa.test
        xmlrpc_uri = https://server.ipa.test/ipa/xml
        enable_ra = True
        """
    ).strip()

    krb5_conf = textwrap.dedent(
        """
        [libdefaults]
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

          KERBEROS.TEST = {
              kdc = kdc.realm1.test
          }

        [domain_realm]
          .ipa.test = IPA.TEST
          ipa.test = IPA.TEST
          .kerberos.test = KERBEROS.TEST
          kerberos.test = KERBEROS.TEST
        """
    ).strip()

    sssd_conf = textwrap.dedent(
        """
        [domain/ipa.test]
        enabled = true
        id_provider = ipa
        ipa_server_mode = false

        [domain/ldap.test]
        enabled = true
        id_provider = ldap
        """
    ).strip()

    smb_conf = textwrap.dedent(
        """
        # output of testparm -s
        Server role: ROLE_DOMAIN_MEMBER

        [global]
            realm = AD-WINBIND.TEST
            security = ADS
            template homedir = /home/%U@%D
            template shell = /bin/bash
            winbind offline logon = Yes
            winbind refresh tickets = Yes
            idmap config * : range = 10000-999999
            idmap config sub1 : backend = rid
            idmap config sub1 : range = 2000000-2999999
            idmap config * : backend = tdb
        """
    ).strip()

    rpms = InstalledRpms(context_wrap("sssd-2.9.1-1.el9.x86_64"))
    ipa_conf = IPAConfig(context_wrap(ipa_conf))
    sssd_conf = SSSDConfAll(
        SSSDConf(context_wrap(sssd_conf, "/etc/sssd/sssd.conf")), []
    )
    krb5_conf = AllKrb5Conf(
        [Krb5Configuration(context_wrap(krb5_conf, path="/etc/krb5.conf"))]
    )
    ipa = IPA(ipa_conf, sssd_conf, rpms)
    smb_conf = SambaConfigs(context_wrap(smb_conf, path="/etc/samba/smb.conf"))
    identity_domain = IdentityDomain(sssd_conf, krb5_conf, ipa, smb_conf)

    assert len(identity_domain.domains) == 4

    domain = identity_domain.domains[0]
    assert domain.name == "ipa.test"
    assert domain.domain_type == DomainTypes.IPA
    assert domain.server_software == ServerSoftware.IPA
    assert domain.client_software == ClientSoftware.SSSD
    assert domain.domain == "ipa.test"
    assert domain.realm == "IPA.TEST"
    assert domain.workgroup is None
    assert domain.ipa_mode is IPAMode.IPA_CLIENT

    domain = identity_domain.domains[1]
    assert domain.name == "ldap.test"
    assert domain.domain_type == DomainTypes.LDAP
    assert domain.server_software == ServerSoftware.LDAP
    assert domain.client_software == ClientSoftware.SSSD
    assert domain.domain is None
    assert domain.realm is None
    assert domain.workgroup is None
    assert domain.ipa_mode is None

    domain = identity_domain.domains[2]
    assert domain.name == "ad-winbind.test"
    assert domain.domain_type == DomainTypes.AD_WINBIND
    assert domain.server_software == ServerSoftware.AD
    assert domain.client_software == ClientSoftware.WINBIND
    assert domain.domain == "ad-winbind.test"
    assert domain.realm == "AD-WINBIND.TEST"
    assert domain.workgroup == "AD-WINBIND"
    assert domain.ipa_mode is None

    domain = identity_domain.domains[3]
    assert domain.name == "kerberos.test"
    assert domain.domain_type == DomainTypes.KRB5
    assert domain.server_software == ServerSoftware.KRB5
    assert domain.client_software == ClientSoftware.KRB5
    assert domain.domain is None
    assert domain.realm == "KERBEROS.TEST"
    assert domain.workgroup is None
    assert domain.ipa_mode is None

    assert identity_domain.default_realm == "IPA.TEST"
    assert identity_domain.dns_lookup_kdc is True
    assert identity_domain.dns_lookup_realm is True


def test_identity_domain_empty():
    with pytest.raises(SkipComponent):
        IdentityDomain(None, None, None, None)
