from insights.tests import context_wrap
from insights.parsers import rhsm_conf
CONFIG = """
# Red Hat Subscription Manager Configuration File:

# Unified Entitlement Platform Configuration
[server]
# Server hostname:
hostname = subscription.rhn.redhat.com

# Server prefix:
prefix = /subscription

# Server port:
port = 443

# Set to 1 to disable certificate validation:
insecure = 0

# Set the depth of certs which should be checked
# when validating a certificate
ssl_verify_depth = 3

# an http proxy server to use
proxy_hostname =

# port for http proxy server
proxy_port =

# user name for authenticating to an http proxy, if needed
proxy_user =

# password for basic http proxy auth, if needed
proxy_password =

[rhsm]
# Content base URL:
baseurl= https://cdn.redhat.com

# Server CA certificate location:
ca_cert_dir = /etc/rhsm/ca/

# Default CA cert to use when generating yum repo configs:
repo_ca_cert = %(ca_cert_dir)sredhat-uep.pem

# Where the certificates should be stored
productCertDir = /etc/pki/product
entitlementCertDir = /etc/pki/entitlement
consumerCertDir = /etc/pki/consumer

# Manage generation of yum repositories for subscribed content:
manage_repos = 1

# Refresh repo files with server overrides on every yum command
full_refresh_on_yum = 0

# If set to zero, the client will not report the package profile to
# the subscription management service.
report_package_profile = 1

# The directory to search for subscription manager plugins
pluginDir = /usr/share/rhsm-plugins

# The directory to search for plugin configuration files
pluginConfDir = /etc/rhsm/pluginconf.d

[rhsmcertd]
# Interval to run cert check (in minutes):
certCheckInterval = 240
# Interval to run auto-attach (in minutes):
autoAttachInterval = 1440

""".strip()

RETURN_VALUE = """
{'rhsmcertd': {'certCheckInterval': '240', 'autoAttachInterval': '1440'}, 'rhsm': {'pluginConfDir': '/etc/rhsm/pluginconf.d', 'full_refresh_on_yum': '0', 'manage_repos': '1', 'baseurl': 'https://cdn.redhat.com', 'productCertDir': '/etc/pki/product', 'ca_cert_dir': '/etc/rhsm/ca/', 'entitlementCertDir': '/etc/pki/entitlement', 'report_package_profile': '1', 'consumerCertDir': '/etc/pki/consumer', 'pluginDir': '/usr/share/rhsm-plugins', 'repo_ca_cert': '%(ca_cert_dir)sredhat-uep.pem'}, 'server': {'proxy_hostname': '', 'proxy_user': '', 'insecure': '0', 'hostname': 'subscription.rhn.redhat.com', 'ssl_verify_depth': '3', 'proxy_password': '', 'proxy_port': '', 'prefix': '/subscription', 'port': '443'}}
""".strip()


def test_rhsm_conf():
        resault = rhsm_conf.RHSMConf(context_wrap(CONFIG))

        assert resault.get('rhsm', 'pluginConfDir') == '/etc/rhsm/pluginconf.d'
        assert resault.get('rhsm', 'full_refresh_on_yum') == '0'
        assert resault.get('rhsm', 'consumerCertDir') == '/etc/pki/consumer'
        assert resault.get('rhsm', 'repo_ca_cert') == '%(ca_cert_dir)sredhat-uep.pem'
