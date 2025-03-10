"""
Auto Configuration Helper
"""
from __future__ import absolute_import
import logging
import requests
import re

from .constants import InsightsConstants as constants
from .cert_auth import rhsmCertificate
from .connection import InsightsConnection

logger = logging.getLogger(__name__)
APP_NAME = constants.app_name


def _is_rhn_or_rhsm(hostname):
    return (hostname == 'subscription.rhn.redhat.com' or
            hostname == 'subscription.rhsm.redhat.com')


def _is_staging_rhsm(hostname):
    return hostname == 'subscription.rhsm.stage.redhat.com'


def verify_connectivity(config):
    """
    Verify connectivity to satellite server
    """
    logger.debug("Verifying Connectivity")
    ic = InsightsConnection(config)
    try:
        branch_info = ic.get_branch_info()
    except requests.ConnectionError as e:
        logger.debug(e)
        logger.debug("Failed to connect to satellite")
        return False
    except LookupError as e:
        logger.debug(e)
        logger.debug("Failed to parse response from satellite")
        return False

    try:
        remote_leaf = branch_info['remote_leaf']
        return remote_leaf
    except LookupError as e:
        logger.debug(e)
        logger.debug("Failed to find accurate branch_info")
        return False


def set_auto_configuration(config, hostname, ca_cert, proxy, is_satellite, is_stage, rhsm_no_proxy=None):
    """
    Set config based on discovered data
    """
    logger.debug("Attempting to auto configure!")
    logger.debug("Attempting to auto configure hostname: %s", hostname)
    logger.debug("Attempting to auto configure CA cert: %s", ca_cert)
    logger.debug("Attempting to auto configure proxy: %s", proxy)
    logger.debug("Attempting to auto configure no_proxy: %s", rhsm_no_proxy)
    saved_base_url = config.base_url
    if ca_cert is not None:
        saved_cert_verify = config.cert_verify
        config.cert_verify = ca_cert
    if proxy is not None:
        saved_proxy = config.proxy
        config.proxy = proxy
    if rhsm_no_proxy and rhsm_no_proxy != '':
        config.no_proxy = rhsm_no_proxy
    if is_satellite:
        # satellite
        config.base_url = hostname + '/r/insights'
        logger.debug('Auto-configured base_url: %s', config.base_url)
    else:
        # connected directly to RHSM
        if is_stage:
            config.base_url = hostname + '/api'
        else:
            config.base_url = hostname + '/r/insights'
        logger.debug('Auto-configured base_url: %s', config.base_url)
        logger.debug('Not connected to Satellite, skipping branch_info')
        # direct connection to RHSM, skip verify_connectivity
        return

    if not verify_connectivity(config):
        logger.warn("Could not auto configure, falling back to static config")
        logger.warn("See %s for additional information",
                    constants.default_log_file)
        config.base_url = saved_base_url
        if proxy is not None:
            if saved_proxy is not None and saved_proxy.lower() == 'none':
                saved_proxy = None
            config.proxy = saved_proxy
        if ca_cert is not None:
            config.cert_verify = saved_cert_verify


def _importInitConfig():
    from rhsm.config import initConfig
    return initConfig()


def _try_satellite6_configuration(config):
    """
    Try to autoconfigure for Satellite 6
    """
    try:
        rhsm_config = _importInitConfig()

        logger.debug('Trying to autoconfigure...')
        cert = open(rhsmCertificate.certpath(), 'r').read()
        key = open(rhsmCertificate.keypath(), 'r').read()
        rhsm = rhsmCertificate(key, cert)
        is_satellite = False
        is_stage = False

        # This will throw an exception if we are not registered
        logger.debug('Checking if system is subscription-manager registered')
        rhsm.getConsumerId()
        logger.debug('System is subscription-manager registered')

        rhsm_hostname = rhsm_config.get('server', 'hostname')
        rhsm_hostport = rhsm_config.get('server', 'port')
        rhsm_proxy_hostname = rhsm_config.get('server', 'proxy_hostname').strip()
        rhsm_proxy_port = rhsm_config.get('server', 'proxy_port').strip()
        rhsm_proxy_user = rhsm_config.get('server', 'proxy_user').strip()
        rhsm_proxy_pass = rhsm_config.get('server', 'proxy_password').strip()
        rhsm_no_proxy = rhsm_config.get('server', 'no_proxy').strip()
        if rhsm_no_proxy.lower() == 'none' or rhsm_no_proxy == '':
            rhsm_no_proxy = None

        proxy = None

        if rhsm_proxy_hostname != "":
            logger.debug("Found rhsm_proxy_hostname %s", rhsm_proxy_hostname)
            proxy = "http://"
            if rhsm_proxy_user != "" and rhsm_proxy_pass != "":
                logger.debug("Found user and password for rhsm_proxy")
                proxy = proxy + rhsm_proxy_user + ":" + rhsm_proxy_pass + "@"
            proxy = proxy + rhsm_proxy_hostname + ':' + rhsm_proxy_port
            logger.debug("RHSM Proxy: %s", proxy)
        logger.debug("Found %sHost: %s, Port: %s",
                     ('' if _is_rhn_or_rhsm(rhsm_hostname) or
                         _is_staging_rhsm(rhsm_hostname)
                         else 'Satellite 6 Server '),
                     rhsm_hostname, rhsm_hostport)
        rhsm_ca = rhsm_config.get('rhsm', 'repo_ca_cert')
        logger.debug("Found CA: %s", rhsm_ca)
        logger.debug("Setting authmethod to CERT")
        config.authmethod = 'CERT'

        # Directly connected to Red Hat, use cert auth directly with the api
        if _is_rhn_or_rhsm(rhsm_hostname):
            # URL changes. my favorite
            logger.debug("Connected to Red Hat Directly, using cert-api")
            rhsm_hostname = 'cert-api.access.redhat.com'
            rhsm_ca = None
        elif _is_staging_rhsm(rhsm_hostname):
            logger.debug('Connected to staging RHSM, using cert.cloud.stage.redhat.com')
            rhsm_hostname = 'cert.cloud.stage.redhat.com'
            # never use legacy upload for staging
            config.legacy_upload = False
            config.cert_verify = True
            is_stage = True
            rhsm_ca = None
        else:
            # Set the host path
            # 'rhsm_hostname' should really be named ~ 'rhsm_host_base_url'
            rhsm_hostname = rhsm_hostname + ':' + rhsm_hostport + '/redhat_access'
            is_satellite = True

        logger.debug("Trying to set auto_configuration")
        set_auto_configuration(config, rhsm_hostname, rhsm_ca, proxy, is_satellite, is_stage, rhsm_no_proxy=rhsm_no_proxy)
        return True
    except Exception as e:
        logger.debug(e)
        logger.debug('System is NOT subscription-manager registered')
        return False


def try_auto_configuration(config):
    """
    Try to auto-configure if we are attached to a sat6
    """
    if config.auto_config and not config.offline:
        _try_satellite6_configuration(config)
    if not config.legacy_upload and re.match(r'(.+)?\/r\/insights', config.base_url):
        # When to append /platform
        #   base url ~= console.redhat.com/r/insights
        #   base url ~= cert-api.access.redhat.com/r/insights
        #   base url ~= satellite.host.example.com/redhat_access/r/insights
        # When not to append /platform
        #   base url ~= console.redhat.com/api
        config.base_url = config.base_url + '/platform'
    logger.debug('Updated base_url: %s', config.base_url)
