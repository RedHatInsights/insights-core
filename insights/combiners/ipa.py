"""
IPA - Combiner for RHEL IdM / FreeIPA information
=================================================
"""
from insights.core.plugins import combiner
from insights.core.exceptions import SkipComponent
from insights.parsers.installed_rpms import InstalledRpms
from insights.parsers.redhat_release import RedhatRelease
from insights.parsers.ipa_conf import IPAConfig
from insights.parsers.sssd_conf import SSSD_Config


@combiner(IPAConfig, SSSD_Config, InstalledRpms, RedhatRelease)
class IPA(object):
    """Combiner for IPA, SSSD, and installed RPMs

    Provides additional information, e.g. whether the host is an IPA server.
    """

    def __init__(self, ipa_conf, sssd_conf, rpms, release):
        self._ipa_conf = ipa_conf
        self._sssd_conf = sssd_conf
        # IPA package names are different on Fedora
        if release.is_fedora:
            self._client_rpm = rpms.get_max("freeipa-client")
            self._server_rpm = rpms.get_max("freeipa-server")
        else:
            self._client_rpm = rpms.get_max("ipa-client")
            self._server_rpm = rpms.get_max("ipa-server")
        if self._client_rpm is None:
            raise SkipComponent("IPA client package is not installed")
        self._is_client = None
        self._is_server = None

    @property
    def ipa_conf(self):
        """Get IPAConfig object"""
        return self._ipa_conf

    @property
    def sssd_conf(self):
        """Get SSSD_Config object"""
        return self._sssd_conf

    @property
    def sssd_domain_config(self):
        """Get SSSD domain configuration for host's IPA domain"""
        return self._sssd_conf.domain_config(self._ipa_conf.domain)

    @property
    def is_client(self):
        """Is the host an IPA client?"""
        # IPAConfig validates that /etc/ipa/default.conf exists and is a
        # valid IPA config file with all required values present.
        if self._is_client is None:
            id_provider = self.sssd_domain_config.get("id_provider")
            if id_provider == "ipa":
                self._is_client = True
            else:
                self._is_client = False

        return self._is_client

    @property
    def is_server(self):
        """Is the host an IPA server?"""
        if self._is_server is None:
            server_mode = self.sssd_domain_config.get(
                "ipa_server_mode", "false"
            )
            if (
                self._server_rpm and
                # all servers are also clients
                self.is_client and
                # only servers use LDAPI (LDAP over Unix socket)
                self._ipa_conf.ldap_uri.startswith("ldapi://") and
                # SSSD domain must be in server mode
                server_mode.lower() == "true"
            ):
                self._is_server = True
            else:
                self._is_server = False

        return self._is_server
