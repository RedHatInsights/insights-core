from insights.tests import context_wrap
from insights.parsers.cobbler_modules_conf import CobblerModulesConf

conf_content = """
# cobbler module configuration file
# =================================

# authentication:
# what users can log into the WebUI and Read-Write XMLRPC?
# choices:
#    authn_denyall    -- no one (default)
#    authn_configfile -- use /etc/cobbler/users.digest (for basic setups)
#    authn_passthru   -- ask Apache to handle it (used for kerberos)
#    authn_ldap       -- authenticate against LDAP
#    authn_spacewalk  -- ask Spacewalk/Satellite (experimental)
#    authn_testing    -- username/password is always testing/testing (debug)
#    (user supplied)  -- you may write your own module
# WARNING: this is a security setting, do not choose an option blindly.
# for more information:
# https://fedorahosted.org/cobbler/wiki/CobblerWebInterface
# https://fedorahosted.org/cobbler/wiki/CustomizableSecurity
# https://fedorahosted.org/cobbler/wiki/CobblerWithKerberos
# https://fedorahosted.org/cobbler/wiki/CobblerWithLdap

[authentication]
module = authn_spacewalk

# authorization:
# once a user has been cleared by the WebUI/XMLRPC, what can they do?
# choices:
#    authz_allowall   -- full access for all authneticated users (default)
#    authz_ownership  -- use users.conf, but add object ownership semantics
#    (user supplied)  -- you may write your own module
# WARNING: this is a security setting, do not choose an option blindly.
# If you want to further restrict cobbler with ACLs for various groups,
# pick authz_ownership.  authz_allowall does not support ACLs.  configfile
# does but does not support object ownership which is useful as an additional
# layer of control.

# for more information:
# https://fedorahosted.org/cobbler/wiki/CobblerWebInterface
# https://fedorahosted.org/cobbler/wiki/CustomizableSecurity
# https://fedorahosted.org/cobbler/wiki/CustomizableAuthorization
# https://fedorahosted.org/cobbler/wiki/AuthorizationWithOwnership
# https://fedorahosted.org/cobbler/wiki/AclFeature

[authorization]
module = authz_allowall

# dns:
# chooses the DNS management engine if manage_dns is enabled
# in /etc/cobbler/settings, which is off by default.
# choices:
#    manage_bind    -- default, uses BIND/named
#    manage_dnsmasq -- uses dnsmasq, also must select dnsmasq for dhcp below
# NOTE: more configuration is still required in /etc/cobbler
# for more information:
# https://fedorahosted.org/cobbler/wiki/ManageDns

[dns]
module = manage_bind

# dhcp:
# chooses the DHCP management engine if manage_dhcp is enabled
# in /etc/cobbler/settings, which is off by default.
# choices:
#    manage_isc     -- default, uses ISC dhcpd
#    manage_dnsmasq -- uses dnsmasq, also must select dnsmasq for dns above
# NOTE: more configuration is still required in /etc/cobbler
# for more information:
# https://fedorahosted.org/cobbler/wiki/ManageDhcp

[dhcp]
module = manage_isc

#--------------------------------------------------
""".strip()


def test_cobbler_modules_conf():
    result = CobblerModulesConf(context_wrap(conf_content))
    assert result.get('authentication', 'module') == 'authn_spacewalk'
    assert result.get('dhcp', 'module') == 'manage_isc'
