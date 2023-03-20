"""
SSSD_Config - file ``/etc/sssd/sssd.config``
============================================
"""
from insights.core import IniConfigFile
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.sssd_config)
class SSSD_Config(IniConfigFile):
    """
    Parse the content of the ``/etc/sssd/sssd.config`` file.

    The 'sssd' section must always exist.  Within that, the 'domains'
    parameter is usually defined to give a comma-separated list of the
    domains that sssd is to manage.

    The 'sssd' section will define one or more active domains, which are then
    configured in the 'domain/{domain}' section of the configuration.  These
    domains are then available via the 'domains' method, and the configuration
    of a domain can be fetched as a dictionary using the 'domain_config' method.

    Sample configuration::

        [sssd]
        config_file_version = 2

        # Number of times services should attempt to reconnect in the
        # event of a crash or restart before they give up
        reconnection_retries = 3

        # If a back end is particularly slow you can raise this timeout here
        sbus_timeout = 30
        services = nss, pam

        # SSSD will not start if you do not configure any domains.
        # Add new domain configurations as [domain/<NAME>] sections, and
        # then add the list of domains (in the order you want them to be
        # queried) to the "domains" attribute below and uncomment it.
        # domains = LOCAL,LDAP
        domains = example.com
        debug_level = 9

        [nss]
        # The following prevents SSSD from searching for the root user/group in
        # all domains (you can add here a comma-separated list of system accounts that
        # are always going to be /etc/passwd users, or that you want to filter out).
        filter_groups = root
        filter_users = root
        reconnection_retries = 3

        [pam]
        reconnection_retries = 3

        [domain/example.com]
        id_provider = ldap
        lookup_family_order = ipv4_only
        ldap_uri = ldap://ldap.example.com/
        ldap_search_base = dc=example,dc=com
        enumerate = False
        hbase_directory= /home
        create_homedir = True
        override_homedir = /home/%u
        auth_provider = krb5
        krb5_server = kerberos.example.com
        krb5_realm = EXAMPLE.COM

    Example:
        >>> type(conf)
        <class 'insights.parsers.sssd_conf.SSSD_Config'>
        >>> conf.get('nss', 'filter_users')
        'root'
        >>> conf.getint('pam', 'reconnection_retries')
        3
        >>> conf.domains
        ['example.com']
        >>> domain = conf.domain_config('example.com')
        >>> 'ldap_uri' in domain
        True
    """
    @property
    def domains(self):
        """
        Returns the list of domains defined in the 'sssd' section.  This is
        used to refer to the domain-specific sections of the configuration.
        """
        if self.has_option('sssd', 'domains'):
            domains = self.get('sssd', 'domains')
            if domains:
                return domains.split(',')

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
