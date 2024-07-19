"""
IPA - Combiner for RHEL IdM / FreeIPA information
=================================================
"""

from insights.combiners.sssd_conf import SSSDConfAll
from insights.core.exceptions import SkipComponent
from insights.core.plugins import combiner
from insights.parsers.installed_rpms import InstalledRpms
from insights.parsers.ipa_conf import IPAConfig


@combiner(IPAConfig, SSSDConfAll, InstalledRpms)
class IPA(object):
    """Combiner for IPA, SSSD, and installed RPMs

    Provides additional information, e.g. whether the host is an IPA server.
    """

    def __init__(self, ipa_conf, sssd_conf, rpms):
        self._ipa_conf = ipa_conf
        self._sssd_conf = sssd_conf

        self._is_client = None
        self._is_server = None
        self._ipa_domains = None

        self._check_installed_packages(rpms)

    def _check_installed_packages(self, rpms):
        # IPA is relying on SSSD which will be installed on both client and server
        if rpms.get_max("sssd") is None:
            raise SkipComponent("sssd package is not installed")

    @property
    def ipa_conf(self):
        """Get IPAConfig object"""
        return self._ipa_conf

    @property
    def sssd_conf(self):
        """Get SSSD_Config object"""
        return self._sssd_conf

    @property
    def sssd_ipa_domains(self):
        """Get all SSSD domains where id_provider is set to ipa"""
        if self._ipa_domains is None:
            self._ipa_domains = []
            for domain in self.sssd_conf.enabled_domains:
                id_provider = self.sssd_conf.domain_get(domain, "id_provider")
                if id_provider == "ipa":
                    self._ipa_domains.append(domain)

        return self._ipa_domains

    @property
    def is_client(self):
        """Is the host an IPA client?"""
        # Check if there is at least one IPA domain in SSSD.
        if self._is_client is None:
            self._is_client = len(self.sssd_ipa_domains) > 0

        return self._is_client

    @property
    def is_server(self):
        """Is the host an IPA server?"""
        if self._is_server is None:
            for domain in self.sssd_ipa_domains:
                self._is_server = self.sssd_conf.domain_getboolean(
                    domain, "ipa_server_mode", False
                )

                # Break if there is at least one IPA domain in server mode
                if self._is_server:
                    break

        return self._is_server
