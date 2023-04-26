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
        if not self._client_rpm:
            return False
        cfg = self.sssd_domain_config
        if not cfg.get("id_provider") == "ipa":
            return False
        return True

    @property
    def is_server(self):
        """Is the host an IPA server?"""
        if not self.is_client:
            # all servers are also clients
            return False
        if not self._server_rpm:
            return False
        if not self._ipa_conf.ldap_uri.startswith("ldapi://"):
            # only servers use LDAPI (LDAP over Unix socket)
            return False
        cfg = self.sssd_domain_config
        if cfg.get("ipa_server_mode", "false").lower() != "true":
            # all servers have ipa_server_mode enabled
            return False
        return True
