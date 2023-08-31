import doctest

from insights.parsers import sssd_conf
from insights.tests import context_wrap

sssd_conf_cnt = """

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
"""

sssd_conf_no_domains = """
[sssd]
debug_level = 5
"""

sssd_conf_blank_domains = """
[sssd]
debug_level = 5
domains =
"""


def test_sssd_conf():
    result = sssd_conf.SSSD_Config(context_wrap(sssd_conf_cnt))
    assert 'sssd' in result
    assert 'domain/example.com' in result

    assert result.getint('pam', 'reconnection_retries') == 3

    assert ['example.com'] == result.domains

    domain = result.domain_config('example.com')
    assert type(domain) is dict
    assert domain['id_provider'] == 'ldap'

    absent_domain = result.domain_config('example.org')
    assert type(absent_domain) is dict
    assert absent_domain == {}


def test_sssd_conf_empty_domains():
    conf = sssd_conf.SSSD_Config(context_wrap(sssd_conf_no_domains))
    assert conf.domains == []

    conf = sssd_conf.SSSD_Config(context_wrap(sssd_conf_blank_domains))
    assert conf.domains == []


def test_doc_examples():
    failed_count, tests = doctest.testmod(
        sssd_conf,
        globs={'conf': sssd_conf.SSSD_Config(context_wrap(sssd_conf_cnt))}
    )
    assert failed_count == 0
