"""
Auto Configuration Helper
"""
from __future__ import absolute_import

import collections
import logging
import os

from . import utilities

from .constants import InsightsConstants as constants
from .cert_auth import rhsmCertificate


logger = logging.getLogger(__name__)
APP_NAME = constants.app_name


try:
    import rhsm.config
    # subscription-manager recommends to use 'get_config_parser()' instead,
    # but RHEL <= 7 doesn't have the method renamed/aliased yet.
    get_rhsm_config = rhsm.config.initConfig
    _rhsm_config_exception = None  # type: Exception | None
except Exception as exc:
    import configparser
    _rhsm_config_exception = exc

    def get_rhsm_config():
        # type: () -> configparser.ConfigParser
        rhsm_config = configparser.ConfigParser()
        rhsm_config.read_string(
            u"[server]\n"
            u"hostname=subscription.rhsm.redhat.com\n"
            u"port=443\n"
            u"proxy_scheme=\n"
            u"proxy_hostname=\n"
            u"proxy_port=\n"
            u"proxy_user=\n"
            u"proxy_password=\n"
            u"no_proxy=\n"
            u"_exception={exctype}: {exc}\n".format(
                exctype=type(_rhsm_config_exception).__name__,
                exc=str(_rhsm_config_exception),
            )
        )
        return rhsm_config


# Can't use enum, it's not supported in Python below 3.4
class DeploymentType:
    PRODUCTION = "production"
    PRODUCTION_LEGACY = "production-legacy"
    STAGE = "stage"
    SATELLITE = "satellite"


def _is_console_dot(hostname):
    return hostname == 'subscription.rhsm.redhat.com'


def _is_staging_console_dot(hostname):
    return hostname == 'subscription.rhsm.stage.redhat.com'


# Can't use dataclass, it's not supported in Python below 3.7
ProxyConfig = collections.namedtuple("ProxyConfig", ["proxy", "no_proxy"])


def _read_rhsm_proxy_settings(rhsm_config):
    # type: ("rhsm.config.RhsmConfigParser") -> ProxyConfig

    rhsm_proxy_scheme = rhsm_config.get("server", "proxy_scheme").strip()  # type: str
    rhsm_proxy_hostname = rhsm_config.get('server', 'proxy_hostname').strip()  # type: str
    rhsm_proxy_port = rhsm_config.get('server', 'proxy_port').strip()  # type: str
    rhsm_proxy_user = rhsm_config.get('server', 'proxy_user').strip()  # type: str
    rhsm_proxy_pass = rhsm_config.get('server', 'proxy_password').strip()  # type: str

    proxy = None  # type: str | None
    if rhsm_proxy_hostname != "":
        proxy_credentials = ""
        obfuscated_proxy_credentials = ""
        if rhsm_proxy_user != "" and rhsm_proxy_pass != "":
            proxy_credentials = "{}:{}@".format(rhsm_proxy_user, rhsm_proxy_pass)
            obfuscated_proxy_credentials = "{}:{}@".format(rhsm_proxy_user, "***")
        proxy = "{scheme}://{credentials}{hostname}:{port}".format(
            scheme=rhsm_proxy_scheme,
            credentials=proxy_credentials,
            hostname=rhsm_proxy_hostname,
            port=rhsm_proxy_port,
        )
        logger.debug("Using RHSM proxy '{scheme}://{credentials}{hostname}:{port}'.".format(
            scheme=rhsm_proxy_scheme,
            credentials=obfuscated_proxy_credentials,
            hostname=rhsm_proxy_hostname,
            port=rhsm_proxy_port,
        ))

    rhsm_no_proxy = rhsm_config.get('server', 'no_proxy').strip()  # type: str | None
    if rhsm_no_proxy.lower() == 'none' or rhsm_no_proxy == '':
        rhsm_no_proxy = None

    return ProxyConfig(proxy, rhsm_no_proxy)


APIConfig = collections.namedtuple("APIConfig", ["url", "cert_verify", "deployment_type"])


def _read_rhsm_settings(rhsm_config, rhel_version):
    # type: ("rhsm.config.RhsmConfigParser", int) -> APIConfig
    """Interpret RHSM configuration to figure out where are Insights."""

    rhsm_hostname = rhsm_config.get('server', 'hostname')  # type: str
    rhsm_port = rhsm_config.get('server', 'port')  # type: str
    logger.debug("RHSM is configured for '{}:{}'.".format(rhsm_hostname, rhsm_port))

    if _is_console_dot(rhsm_hostname):
        logger.debug("RHSM is pointed at ConsoleDot.")
        if rhel_version >= 10:
            # This is the default ConsoleDot API URL these days.
            api_url = constants.consoledot_fqdn + "/api"
        else:
            # The non-legacy API has historically been CloudDot, let's keep it that way.
            api_url = constants.clouddot_fqdn + "/api"
        deployment_type = DeploymentType.PRODUCTION
    elif _is_staging_console_dot(rhsm_hostname):
        logger.debug('RHSM is pointed at staging ConsoleDot.')
        api_url = constants.consoledot_fqdn_stage + "/api"
        deployment_type = DeploymentType.STAGE
    else:
        # Satellite, Capsule or other deployment at customer site
        logger.debug("RHSM is pointed at Satellite.")
        api_url = "{}:{}/redhat_access/r/insights".format(rhsm_hostname, rhsm_port)
        deployment_type = DeploymentType.SATELLITE

    return APIConfig(
        url=api_url,
        cert_verify=True,
        deployment_type=deployment_type,
    )


def _should_use_legacy_api(client_config, rhel_version):
    """Should we use the legacy API?

    Legacy API is at cert-api.access.redhat.com. The newer one is ConsoleDot
    at cert.{cloud,console}.redhat.com. We cannot simply change the URLs we
    talk to, the customer firewalls might not be configured to do so, and we
    wouldn't be able to operate.

    :type client_config: insights.client.config.InsightsConfig
    :param rhel_version: Version-dependent behavior. Passing in 0 (e.g. because
        the RHEL version couldn't be determined) keeps the legacy behavior.
    :type rhel_version: int
    :rtype: bool
    """
    if os.getenv("INSIGHTS_FORCE_ACCESSDOT_API", None) is not None:
        logger.debug("Forcing legacy API through environment variable.")
        return True

    if client_config.legacy_upload is False:
        logger.debug("Legacy API is explicitly disabled (reason: {}).".format(client_config._legacy_upload_reason))
        return False

    if rhel_version >= 10:
        logger.debug("RHEL 10 doesn't support legacy API.")
        return False

    return True


def autoconfigure_network(client_config):
    """Autoconfigure to connect to Hosted or Satellite.

    :type client_config: insights.client.config.InsightsConfig
    :rtype: None
    """
    logger.debug("Detecting API URLs.")
    if client_config.offline:
        logger.debug("Autoconfiguration is not necessary in offline mode.")
        return
    if not rhsmCertificate.existsAndValid():
        logger.debug("No reason to autoconfigure, host isn't registered with subscription-manager.")
        return
    if not client_config.auto_config:
        logger.debug("Autoconfiguration is disabled, API URL is '{}'.".format(client_config.base_url))
        return

    try:
        rhel_version = utilities.get_rhel_version()
    except ValueError:
        rhel_version = 0

    rhsm_config = get_rhsm_config()  # type: "rhsm.config.RhsmConfigParser"
    try:
        exc = rhsm_config.get("server", "_exception")
        # We cannot log this fact at import time, logging isn't initialized yet.
        logger.debug(
            "The 'rhsm.config' module isn't available. "
            "Using in-memory version of '/etc/rhsm/rhsm.conf' instead. ({})".format(exc)
        )
    except Exception:
        pass
    api_config = _read_rhsm_settings(rhsm_config, rhel_version)  # type: APIConfig
    proxy_config = _read_rhsm_proxy_settings(rhsm_config)  # type: ProxyConfig

    if api_config.deployment_type == DeploymentType.PRODUCTION and _should_use_legacy_api(client_config, rhel_version):
        api_config = APIConfig(
            url="cert-api.access.redhat.com/r/insights",
            cert_verify=None,  # the connection.py treats None as 'use dedicated certificate'
            deployment_type=DeploymentType.PRODUCTION_LEGACY,
        )

    logger.debug("Parsed RHSM configuration: deployment={deployment}, authorization={authn}.".format(
        deployment=api_config.deployment_type,
        authn="legacy certificate" if api_config.cert_verify is None else str(api_config.cert_verify),
    ))

    apply_network_configuration(
        client_config,
        api_config,
        proxy_config,
    )

    logger.debug("API URL is '{}'.".format(client_config.base_url))


def apply_network_configuration(client_config, api_config, proxy_config):
    """Update configuration based on discovered data.

    :type client_config: insights.client.config.InsightsConfig
    :type api_config: APIConfig
    :type proxy_config: ProxyConfig
    """
    client_config.base_url = api_config.url
    # This won't be necessary when CERT becomes the default in config.py
    client_config.authmethod = "CERT"

    client_config.legacy_upload = api_config.deployment_type == DeploymentType.PRODUCTION_LEGACY

    if api_config.cert_verify is not None:
        client_config.cert_verify = api_config.cert_verify

    if proxy_config.proxy is not None:
        client_config.proxy = proxy_config.proxy
    if proxy_config.no_proxy is not None:
        client_config.no_proxy = proxy_config.no_proxy
