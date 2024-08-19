"""
SSSD Configuration
==================

Provides access to complete SSSD configuration: /etc/sssd/sssd.conf with merged
configuration snippets from /etc/sssd/conf.d.
"""

from copy import deepcopy

from insights.core.exceptions import SkipComponent
from insights.core.plugins import combiner
from insights.parsers.sssd_conf import SSSDConf, SSSDConfd


@combiner(optional=[SSSDConf, SSSDConfd])
class SSSDConfAll(object):
    """
    Provides access to complete SSSD configuration: /etc/sssd/sssd.conf with
    merged configuration snippets from /etc/sssd/conf.d.
    """

    def __init__(self, sssd_conf=None, sssd_conf_d=None):
        if sssd_conf is None and not sssd_conf_d:
            raise SkipComponent("SSSD is not configured")

        conf = sssd_conf
        conf_d = []

        if sssd_conf_d is not None:
            conf_d = sorted(sssd_conf_d, key=lambda x: x.file_name)

        if conf is None:
            conf = conf_d.pop(0)

        self.config = deepcopy(conf)

        for parser in conf_d:
            if parser.file_name.startswith("."):
                continue

            for section in parser.sections():
                for key, value in parser.items(section).items():
                    self.config._set(section, key, value)

        self._enabled_domains = None

    @property
    def enabled_domains(self):
        """
        Returns the list of enabled domains.

        Domains can be enabled either using the ``domains`` option in the
        ``sssd`` section of the configuration file or using the ``enabled``
        option in the domain configuration.

        [sssd]
        domains = a, b

        [domain/a]
        ...

        [domain/b]
        ...

        [domain/c]
        enabled = true

        """
        if self._enabled_domains is None:
            enabled_domains = []

            if self.config.has_option("sssd", "domains"):
                domains = self.config.get("sssd", "domains")
                enabled_domains = [domain.strip() for domain in domains.split(",")]

            prefix = "domain/"
            for section in self.config.sections():
                # Ignore if this is not a domain configuration
                if not section.startswith(prefix):
                    continue

                name = section[len(prefix):].strip()
                if not name:
                    # Invalid configuration
                    continue

                # Ignore if this is a subdomain configuration
                # `domain/$dom/$subdom`
                if "/" in name:
                    continue

                if self.config.has_option(section, "enabled"):
                    enabled = self.config.getboolean(section, "enabled")

                    if enabled and name not in enabled_domains:
                        enabled_domains.append(name)
                    elif not enabled and name in enabled_domains:
                        enabled_domains.remove(name)

            self._enabled_domains = enabled_domains

        return self._enabled_domains

    def domain_config(self, domain):
        """
        Return the configuration dictionary for a specific domain, given as
        the raw name as listed in the 'domains' property of the sssd section.
        This then looks for the equivalent 'domain/{domain}' section of the
        config file.
        """
        full_domain = self.domain_section(domain)
        if full_domain not in self.config:
            return {}

        return self.config.items(full_domain)

    def domain_section(self, domain):
        """
        Transform plain SSSD domain name into a configuration section.

        ipa.test -> domain/ipa.test

        Args:
            domain (str): SSSD domain name.

        Returns:
            str: Returns the configuration section.
        """
        return "domain/" + domain

    def domain_get(self, domain, option, default=None):
        """
        Lookup option in domain.

        Args:
            domain (str): The SSSD domain name.
            option (str): The option str to search for.
            default (any): Default value if the option is not found.

        Returns:
            str: Returns the value of the option in the specified section.
        """
        section = self.domain_section(domain)

        if not self.config.has_option(section, option):
            return default

        return self.config.get(section, option)

    def domain_getboolean(self, domain, option, default=None):
        """
        Lookup boolean option in domain.

        Args:
            domain (str): The SSSD domain name.
            option (str): The option str to search for.
            default (any): Default value if the option is not found.

        Returns:
            bool: Returns boolean form based on the data from get.
        """
        section = self.domain_section(domain)

        if not self.config.has_option(section, option):
            return default

        return self.config.getboolean(section, option)
