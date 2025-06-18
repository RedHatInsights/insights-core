"""
SSSD Configuration - files ``/etc/sssd/sssd.conf`` and ``/etc/sssd.conf.d/*``
=============================================================================

SSSD configuration files are in INI format.

Example:
    [sssd]
    services = nss, sudo
    domains = test

    [sudo]
    debug_level = 0xfff0

    [domain/test]
    id_provider = ldap
    ldap_uri = ldap://ldap.test


SSSDConf - file ``/etc/sssd/sssd.conf``
----------------------------------------

SSSDConfd - files under ``/etc/sssd/conf.d/*.conf``
---------------------------------------------------
"""

from insights.core import IniConfigFile
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.sssd_config)
class SSSDConf(IniConfigFile):
    """
    Parse the content of the ``/etc/sssd/sssd.conf``.

    The file format is standard ini file.
    """

    def getboolean(self, section, option):
        """
        Returns:
            bool: Returns boolean form based on the data from get.
        """
        val = self.get(section, option)
        boolean_states = {
            "true": True,
            "false": False,
        }

        if val.lower() not in boolean_states:
            raise ValueError("Not a boolean: %s" % val)

        return boolean_states[val.lower()]

    def _set(self, section, option, value=None):
        """
        Sets the value of the specified section option.

        Note: This should only be used by
        :class:`insights.combiners.sssd_conf.SSSDConfAll`.

        Args:
            section (str): The section str to set for. option (str): The option
            str to set for. value (str): The value to set.
        """
        section = section.strip()
        option = option.strip().lower()

        if section not in self._dict:
            self._dict[section] = {}

        self._dict[section][option] = value

    @property
    def domains(self):
        """
        Returns the list of domains defined in the 'sssd' section.  This is
        used to refer to the domain-specific sections of the configuration.
        """
        if self.has_option('sssd', 'domains'):
            domains = self.get('sssd', 'domains')
            if domains:
                return [domain.strip() for domain in domains.split(',')]

        # Return a blank list if no domains.
        return []

    def domain_config(self, domain):
        """
        Return the configuration dictionary for a specific domain, given as
        the raw name as listed in the 'domains' property of the sssd section.
        This then looks for the equivalent 'domain/{domain}' section of the
        config file.
        """
        full_domain = 'domain/' + domain
        if full_domain not in self:
            return {}
        return self.items(full_domain)


@parser(Specs.sssd_conf_d)
class SSSDConfd(SSSDConf):
    """
    Parse the content of configuration snippet under ``/etc/sssd/conf.d/*.conf``.

    The file format is standard ini file.
    """

    pass
