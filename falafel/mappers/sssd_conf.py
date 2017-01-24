from .. import IniConfigFile, mapper


@mapper('sssd_config')
class SSSD_Config(IniConfigFile):
    """
    Parse the content of the /etc/sssd/sssd.config file.

    The 'sssd' section must always exist.  Within that, the 'domains'
    parameter is usually defined to give a comma-separated list of the
    domains that sssd is to manage.
    """

    def domains(self):
        """
        Returns the list of domains defined in the 'sssd' section.  This is
        used to refer to the domain-specific sections of the configuration.
        """
        domains = self.get('sssd', 'domains')
        if not domains:
            return domains
        return domains.split(',')

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
