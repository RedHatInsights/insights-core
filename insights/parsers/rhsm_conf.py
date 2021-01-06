"""
rhsm.conf - File /etc/rhsm/rhsm.conf
====================================

Typical content of "/etc/rhsm/rhsm.conf" is::

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
"""
from .. import parser, IniConfigFile
from insights.specs import Specs


@parser(Specs.rhsm_conf)
class RHSMConf(IniConfigFile):
    """Parses content of "/etc/rhsm/rhsm.conf". """
    pass
