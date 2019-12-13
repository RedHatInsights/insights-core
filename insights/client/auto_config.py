"""
Auto Configuration Helper
"""
from __future__ import absolute_import
import logging
import os
import requests

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

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


def set_auto_configuration(config, hostname, ca_cert, proxy, is_satellite):
    """
    Set config based on discovered data
    """
    logger.debug("Attempting to auto configure!")
    logger.debug("Attempting to auto configure hostname: %s", hostname)
    logger.debug("Attempting to auto configure CA cert: %s", ca_cert)
    logger.debug("Attempting to auto configure proxy: %s", proxy)
    saved_base_url = config.base_url
    if ca_cert is not None:
        saved_cert_verify = config.cert_verify
        config.cert_verify = ca_cert
    if proxy is not None:
        saved_proxy = config.proxy
        config.proxy = proxy
    if is_satellite:
        # satellite
        config.base_url = hostname + '/r/insights'
        logger.debug('Auto-configured base_url: %s', config.base_url)
    else:
        # connected directly to RHSM
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
            logger.debug('Connected to staging RHSM, using rhel-test')
            rhsm_hostname = 'rhel-test.cloud.redhat.com'
            rhsm_ca = False  # NOT None
        else:
            # Set the host path
            # 'rhsm_hostname' should really be named ~ 'rhsm_host_base_url'
            rhsm_hostname = rhsm_hostname + ':' + rhsm_hostport + '/redhat_access'
            is_satellite = True

        logger.debug("Trying to set auto_configuration")
        set_auto_configuration(config, rhsm_hostname, rhsm_ca, proxy, is_satellite)
        return True
    except Exception as e:
        logger.debug(e)
        logger.debug('System is NOT subscription-manager registered')
        return False


def _read_systemid_file(path):
    with open(path, "r") as systemid:
        data = systemid.read().replace('\n', '')
    return data


def _try_satellite5_configuration(config):
    """
    Attempt to determine Satellite 5 Configuration
    """
    logger.debug("Trying Satellite 5 auto_config")
    rhn_config = '/etc/sysconfig/rhn/up2date'
    systemid = '/etc/sysconfig/rhn/systemid'
    if os.path.isfile(rhn_config):
        if os.path.isfile(systemid):
            config.systemid = _read_systemid_file(systemid)
        else:
            logger.debug("Could not find Satellite 5 systemid file.")
            return False

        logger.debug("Found Satellite 5 Config")
        rhn_conf_file = open(rhn_config, 'r')
        hostname = None
        for line in rhn_conf_file:
            if line.startswith('serverURL='):
                url = urlparse(line.split('=')[1])
                hostname = url.netloc + '/redhat_access'
                logger.debug("Found hostname %s", hostname)
            if line.startswith('sslCACert='):
                rhn_ca = line.strip().split('=')[1]

            # Auto discover proxy stuff
            if line.startswith('enableProxy='):
                proxy_enabled = line.strip().split('=')[1]
            if line.startswith('httpProxy='):
                proxy_host_port = line.strip().split('=')[1]
            if line.startswith('proxyUser='):
                proxy_user = line.strip().split('=')[1]
            if line.startswith('proxyPassword='):
                proxy_password = line.strip().split('=')[1]

        if hostname:
            proxy = None
            if proxy_enabled == "1":
                proxy = "http://"
                if proxy_user != "" and proxy_password != "":
                    logger.debug("Found user and password for rhn_proxy")
                    proxy = proxy + proxy_user + ':' + proxy_password
                    proxy = proxy + "@" + proxy_host_port
                else:
                    proxy = proxy + proxy_host_port
                    logger.debug("RHN Proxy: %s", proxy)
            set_auto_configuration(config, hostname, rhn_ca, proxy, True)
        else:
            logger.debug("Could not find hostname")
            return False
        return True
    else:
        logger.debug("Could not find rhn config")
        return False


def try_auto_configuration(config):
    """
    Try to auto-configure if we are attached to a sat5/6
    """
    if config.auto_config and not config.offline:
        if not _try_satellite6_configuration(config):
            _try_satellite5_configuration(config)
    if not config.legacy_upload and 'cloud.redhat.com' not in config.base_url:
        config.base_url = config.base_url + '/platform'
    logger.debug('Updated base_url: %s', config.base_url)
