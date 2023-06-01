"""
Identity Domain - Combiner for domain enrollment
================================================

The combiner detects enrollment into identity domains such as IPA,
Active Directory, generic Kerberos realm, and generic LDAP. It parses
domains and realms from SSSD, KRB5, IPA, and Samba configuration.

Supported domain types
----------------------

* IPA (RHEL IdM, FreeIPA)
* Active Directory (SSSD)
* Active Directory (Samba winbind)
* generic LDAP domain (SSSD)
* generic LDAP domain with Kerberos authentication (SSSD)
* generic Kerberos realm (from ``krb5.conf``)

The combiner cannot detect generic Kerberos realms that solely rely upon
DNS realm lookup (``dns_lookup_realm``).

Examples::

    DomainInfo(
        name="ipa.test",
        domain_type="IPA",
        server_software="IPA",
        client_software="SSSD",
        domain="ipa.test",
        realm="IPA.TEST",
        workgroup=None,
        ipa_mode="client",
    )

    DomainInfo(
        name="ad-winbind.test",
        domain_type="Active Directory (winbind)",
        server_software="Active Directory",
        client_software="winbind",
        domain="ad-winbind.test",
        realm="AD-WINBIND.TEST",
        workgroup="AD-WINBIND",
        ipa_mode=None,
    )
"""
import collections

from insights.core.exceptions import SkipComponent
from insights.core.plugins import combiner
from insights.combiners.ipa import IPA
from insights.parsers.samba import SambaConfigs
from insights.parsers.sssd_conf import SSSD_Config
from insights.combiners.krb5 import AllKrb5Conf


class DomainTypes(object):
    """Human readable domain type"""

    # SSSD domain types
    IPA = "IPA"
    AD_SSSD = "Active Directory (SSSD)"
    LDAP = "LDAP"
    LDAP_KRB5 = "LDAP/Kerberos"
    # krb5.conf but not in sssd.conf
    KRB5 = "Kerberos"
    # Samba winbind
    AD_WINBIND = "Active Directory (winbind)"


class ServerSoftware(object):
    """Server software"""

    IPA = "IPA"
    AD = "Active Directory"
    LDAP = "generic LDAP"
    LDAP_KRB5 = "generic LDAP/Kerberos"
    KRB5 = "generic Kerberos"


class ClientSoftware(object):
    """Client software"""

    SSSD = "SSSD"
    WINBIND = "winbind"
    KRB5 = "Kerberos"


class IPAMode(object):
    """IPA mode (server or client-only)"""

    IPA_CLIENT = "client"
    IPA_SERVER = "server"


DomainInfo = collections.namedtuple(
    "DomainInfo",
    [
        "name",
        "domain_type",
        "server_software",
        "client_software",
        "domain",
        "realm",
        "workgroup",
        "ipa_mode",
    ],
)
"""Identity domain information

Attributes:
    name (str): user-friendly name
        either SSSD's domain name, domain name, or lower-case realm name
    domain_type (str): domain type, e.g. ``IPA`` or ``Active Directory (SSSD)``
    server_software (str): name of the server software, e.g. ``Active Directory``
    client_software (str): name of the client software, e.g. ``SSSD`` or ``winbind``
    domain (str, None): name of the identity domain,
        not set for generic Kerberos or LDAP
    realm (str, None): Kerberos realm name,
        not set for generic LDAP
    workgroup (str, None): workgroup name,
        only set for AD with winbind
    ipa_mode (str, None): IPA mode (server or client),
        only set for IPA
"""


@combiner(optional=[SSSD_Config, AllKrb5Conf, IPA, SambaConfigs])
class IdentityDomain(object):
    """
    A combiner for identity domains.

    Raises:
        SkipComponent: When no identity domains are detected.

    Attributes:
        domains (list): List of the namedtuple `DomainInfo`
        default_realm (str, None): default realm name (if configured)
        dns_lookup_realm (bool): is Kerberos realm DNS lookup enabled?
        dns_lookup_kdc (bool): is Kerberos KDC DNS lookup enabled?
    """

    def __init__(self, sssd=None, krb5=None, ipa=None, smb=None):
        if sssd is None and krb5 is None and smb is None:
            # ipa depends on sssd
            raise SkipComponent("KRB5, SSSD, and Samba are not configured")

        self.domains = []
        self._realms = set()

        if krb5 is not None:
            self.default_realm = krb5.default_realm
            self.dns_lookup_realm = krb5.dns_lookup_realm
            self.dns_lookup_kdc = krb5.dns_lookup_kdc
        else:
            self.default_realm = None
            # krb5.conf default is True
            self.dns_lookup_realm = True
            self.dns_lookup_kdc = True

        if sssd is not None:
            self._parse_sssd(sssd, ipa)
        if smb is not None:
            self._parse_smb(smb)
        if krb5 is not None:
            # parse /etc/krb5.conf last to skip SSSD and Samba realms
            self._parse_krb5(krb5)

        if not self.domains:
            raise SkipComponent("No identity domains detected")

    def _add_domaininfo(
        self, name, dtype, srv, clnt, domain, realm, workgroup=None, ipa_mode=None
    ):
        if realm is not None:
            if realm in self._realms:
                # already configured
                return
            self._realms.add(realm)

        di = DomainInfo(name, dtype, srv, clnt, domain, realm, workgroup, ipa_mode)
        self.domains.append(di)

    def _parse_sssd(self, sssd, ipa):
        """Extract domains from sssd.conf

        Supports id_providers "ad", "ipa", and "ldap".
        """
        id_auth_providers = set(["ldap", "krb5", "ipa", "ad", "proxy"])
        for name in sssd.domains:
            if "/" in name:
                # Ignore trusted domain (subdomain) configuration. Subdomain
                # settings are configured as
                # `[domain/parent.example/subdomain.example]`.
                continue
            conf = sssd.domain_config(name)
            id_provider = conf.get("id_provider")
            ipa_mode = None

            auth_provider = conf.get("auth_provider")
            if auth_provider is None and id_provider in id_auth_providers:
                # most id providers are also an auth providers
                auth_provider = id_provider
            elif auth_provider == "none":
                auth_provider = None

            if id_provider == "ad":
                dtype = DomainTypes.AD_SSSD
                srv = ServerSoftware.AD
                domain = conf.get("ad_domain", name)
                realm = conf.get("krb5_domain", domain.upper())
            elif id_provider == "ipa":
                if ipa is None or not ipa.is_client:
                    # unsupported configuration
                    continue
                dtype = DomainTypes.IPA
                srv = ServerSoftware.IPA
                domain = conf.get("ipa_domain", name)
                realm = conf.get("krb5_domain", domain.upper())
                ipa_mode = IPAMode.IPA_SERVER if ipa.is_server else IPAMode.IPA_CLIENT
            elif id_provider == "ldap":
                if auth_provider == "ldap":
                    dtype = DomainTypes.LDAP
                    srv = ServerSoftware.LDAP
                    domain = None
                    realm = None
                elif auth_provider == "krb5":
                    dtype = DomainTypes.LDAP_KRB5
                    srv = ServerSoftware.LDAP_KRB5
                    domain = None
                    # krb5_domain is required
                    realm = conf.get("krb5_realm", name.upper())
                else:
                    # unsupported configuration
                    continue
            elif id_provider in ("proxy", "files"):
                # not an identity domain
                continue
            else:
                # unsupported configuration
                continue

            self._add_domaininfo(
                name, dtype, srv, ClientSoftware.SSSD, domain, realm, ipa_mode=ipa_mode
            )

    def _parse_smb(self, smb):
        """Parse smb.conf to detect AD with winbind

        We ignore IPA DC here as the information is already provided by
        `sssd.conf`. IPA DC has either server role `ROLE_IPA_DC`
        (Samba >= 4.16.0) or `ROLE_DOMAIN_PDC`, and always
        `security=user`.
        """
        if (
            smb.server_role != "ROLE_DOMAIN_MEMBER" or
            not smb.has_option("global", "security") or
            smb.get("global", "security").upper() != "ADS" or
            not smb.has_option("global", "realm")
        ):
            return
        realm = smb.get("global", "realm")
        domain = realm.lower()

        if smb.has_option("global", "workgroup"):
            workgroup = smb.get("global", "workgroup")
        else:
            workgroup = realm.split(".", 1)[0]

        self._add_domaininfo(
            domain,
            DomainTypes.AD_WINBIND,
            ServerSoftware.AD,
            ClientSoftware.WINBIND,
            domain,
            realm,
            workgroup,
        )

    def _parse_krb5(self, krb5):
        """Parse krb5.conf to detect additional generic Kerberos realms"""
        for realm in krb5.realms:
            self._add_domaininfo(
                realm.lower(),
                DomainTypes.KRB5,
                ServerSoftware.KRB5,
                ClientSoftware.KRB5,
                None,
                realm,
            )
