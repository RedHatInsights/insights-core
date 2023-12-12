"""
rhsm.conf - File /etc/rhsm/rhsm.conf
====================================
"""
from insights.core import IniConfigFile
from insights.core.filters import add_filter
from insights.core.plugins import parser
from insights.specs import Specs

add_filter(Specs.rhsm_conf, '[')


@parser(Specs.rhsm_conf)
class RHSMConf(IniConfigFile):
    """
    Parses content of "/etc/rhsm/rhsm.conf".

    Typical content of "/etc/rhsm/rhsm.conf" is::

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

    Examples:
        >>> type(conf)
        <class 'insights.parsers.rhsm_conf.RHSMConf'>
        >>> conf.sections()
        ['server', 'rhsm', 'rhsmcertd']
        >>> conf.has_option('rhsm', 'ca_cert_dir')
        True
        >>> conf.get("rhsm", "baseurl")
        'https://cdn.redhat.com'
        >>> conf.get("rhsm", "pluginDir")
        '/usr/share/rhsm-plugins'
        >>> conf.getboolean("rhsm", "manage_repos")
        True
    """
    pass
