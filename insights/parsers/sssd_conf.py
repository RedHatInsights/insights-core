"""
SSSD_Config - file ``/etc/sssd/sssd.config``
============================================

SSSD's configuration file is in a standard 'ini' format.

The 'sssd' section will define one or more active domains, which are then
configured in the 'domain/{domain}' section of the configuration.  These
domains are then available via the 'domains' method, and the configuration
of a domain can be fetched as a dictionary using the 'domain_config' method.

Example:
    >>> sssd_conf = shared[SSSD_Config]
    >>> sssd_conf.getint('nss', 'reconnection_retries')
    3
    >>> sssd_conf.domains()
    ['example.com']
    >>> domain = sssd_conf.domain_config('example.com')
    >>> 'ldap_uri' in domain
    True
"""

from .. import IniConfigFile, parser
from insights.specs import Specs


@parser(Specs.sssd_config)
class SSSD_Config(IniConfigFile):
    """
    Parse the content of the ``/etc/sssd/sssd.config`` file.

    The 'sssd' section must always exist.  Within that, the 'domains'
    parameter is usually defined to give a comma-separated list of the
    domains that sssd is to manage.
    """

    @property
    def domains(self):
        """
        Returns the list of domains defined in the 'sssd' section.  This is
        used to refer to the domain-specific sections of the configuration.
        """
        if self.has_option('sssd', 'domains'):
            domains = self.get('sssd', 'domains')
            # Return a blank list if no domains listed.
            if not domains:
                return []
            return domains.split(',')
        else:
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
