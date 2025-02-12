from insights.client.auto_config import APIConfig, DeploymentType
from insights.client.auto_config import ProxyConfig  # noqa: F401
from insights.client.auto_config import (
    _maybe_switch_to_legacy,
    _read_rhsm_settings,
    _read_rhsm_proxy_settings,
    autoconfigure_network,
)

try:
    from unittest import mock
except ImportError:
    import mock

import pytest
import configparser


def test_read_rhsm_proxy_settings__none():
    rhsm_config = configparser.ConfigParser()
    rhsm_config.read_string(
        "[server]\n"
        "proxy_scheme=http\nproxy_hostname=\nproxy_port=\n"
        "proxy_user=\nproxy_password=\n"
        "no_proxy=\n"
    )
    result = _read_rhsm_proxy_settings(rhsm_config)  # type: ProxyConfig
    assert result.proxy is None
    assert result.no_proxy is None


def test_read_rhsm_proxy_settings__no_auth_proxy():
    rhsm_config = configparser.ConfigParser()
    rhsm_config.read_string(
        "[server]\n"
        "proxy_scheme=http\nproxy_hostname=proxy.internal\nproxy_port=8888\n"
        "proxy_user=\nproxy_password=\n"
        "no_proxy=\n"
    )
    result = _read_rhsm_proxy_settings(rhsm_config)  # type: ProxyConfig
    assert result.proxy == "http://proxy.internal:8888"
    assert result.no_proxy is None


def test_read_rhsm_proxy_settings__auth_proxy():
    rhsm_config = configparser.ConfigParser()
    rhsm_config.read_string(
        "[server]\n"
        "proxy_scheme=https\nproxy_hostname=proxy.internal\nproxy_port=8888\n"
        "proxy_user=user\nproxy_password=password\n"
        "no_proxy=\n"
    )
    result = _read_rhsm_proxy_settings(rhsm_config)  # type: ProxyConfig
    assert result.proxy == "https://user:password@proxy.internal:8888"
    assert result.no_proxy is None


def test_read_rhsm_proxy_settings__no_proxy():
    rhsm_config = configparser.ConfigParser()
    rhsm_config.read_string(
        "[server]\n"
        "proxy_scheme=http\nproxy_hostname=\nproxy_port=\n"
        "proxy_user=\nproxy_password=\n"
        "no_proxy=hostname.internal\n"
    )
    result = _read_rhsm_proxy_settings(rhsm_config)  # type: ProxyConfig
    assert result.no_proxy == "hostname.internal"


API_CONFIG_PRODUCTION = APIConfig(
    url="cert.cloud.redhat.com/api",
    cert_verify=True,
    deployment_type=DeploymentType.PRODUCTION,
)
API_CONFIG_LEGACY = APIConfig(
    url="cert-api.access.redhat.com/r/insights",
    cert_verify=None,
    deployment_type=DeploymentType.PRODUCTION,
)
API_CONFIG_STAGE = APIConfig(
    url="cert.console.stage.redhat.com/api",
    cert_verify=True,
    deployment_type=DeploymentType.STAGE,
)
API_CONFIG_SATELLITE = APIConfig(
    url="satellite.internal:443/redhat_access/r/insights",
    cert_verify=True,
    deployment_type=DeploymentType.SATELLITE,
)


def test_read_rhsm_settings__production(*args):
    rhsm_config = configparser.ConfigParser()
    rhsm_config.read_string("[server]\nhostname=subscription.rhsm.redhat.com\nport=443\n")
    result = _read_rhsm_settings(rhsm_config)
    assert result == API_CONFIG_PRODUCTION
    # This is always PRODUCTION, no matter the RHEL version.
    # Downgrade to LEGACY is done by different method (_maybe_switch_to_legacy)
    # as it is a special compatibility case.


def test_read_rhsm_settings__stage():
    rhsm_config = configparser.ConfigParser()
    rhsm_config.read_string("[server]\nhostname=subscription.rhsm.stage.redhat.com\nport=443\n")
    result = _read_rhsm_settings(rhsm_config)
    assert result == API_CONFIG_STAGE


def test_read_rhsm_settings__satellite():
    rhsm_config = configparser.ConfigParser()
    rhsm_config.read_string("[server]\nhostname=satellite.internal\nport=443\n")
    result = _read_rhsm_settings(rhsm_config)
    assert result == API_CONFIG_SATELLITE


@pytest.mark.parametrize(
    "rhel,config_legacy_upload,expected",
    [
        (9, True, API_CONFIG_LEGACY),
        (9, False, API_CONFIG_PRODUCTION),
        (10, True, API_CONFIG_PRODUCTION),
        (10, False, API_CONFIG_PRODUCTION),
    ],
    ids=["el9,legacy=True", "el9,legacy=False", "el10,legacy=True", "el10,legacy=False"],
)
def test_legacy_api(rhel, config_legacy_upload, expected):
    """Keep using legacy API on RHEL <= 9, where it is the default."""
    client_config = mock.Mock(legacy_upload=config_legacy_upload)
    with mock.patch("insights.client.auto_config.utilities.get_rhel_version", return_value=rhel):
        result = _maybe_switch_to_legacy(client_config, API_CONFIG_PRODUCTION)
        assert result == expected


@pytest.mark.parametrize(
    "rhel,legacy_enabled,rhsm_url,expected_url",
    [
        (9, True, "subscription.rhsm.redhat.com", API_CONFIG_LEGACY.url),
        (9, False, "subscription.rhsm.redhat.com", API_CONFIG_PRODUCTION.url),
        (10, True, "subscription.rhsm.redhat.com", API_CONFIG_PRODUCTION.url),
        (10, False, "subscription.rhsm.redhat.com", API_CONFIG_PRODUCTION.url),
        (8, True, "subscription.rhsm.stage.redhat.com", API_CONFIG_STAGE.url),
        (8, True, "satellite.internal", API_CONFIG_SATELLITE.url),
        (8, False, "satellite.internal", API_CONFIG_SATELLITE.url),
    ],
    ids=[
        "el9,legacy=True",
        "el9,legacy=False",
        "el10,legacy=True",
        "el10,legacy=False",
        "el8,legacy=True,stage",
        "el8,legacy=True,satellite",
        "el8,legacy=False,satellite",
    ],
)
@mock.patch("insights.client.auto_config.rhsmCertificate.existsAndValid", return_value=True)
@mock.patch("insights.client.auto_config.get_rhsm_config")
def test_autoconfigure_network(get_config_parser, _cert_exists, rhel, legacy_enabled, rhsm_url, expected_url):
    rhsm_config = configparser.ConfigParser()
    rhsm_config.read_string(
        "[server]\nhostname={}\nport=443\n".format(rhsm_url) +
        "proxy_scheme=https\nproxy_hostname=proxy.internal\nproxy_port=443\n" +
        "proxy_user=user\nproxy_password=password\nno_proxy=\n"
    )
    get_config_parser.return_value = rhsm_config
    client_config = mock.Mock(offline=False, auto_config=True, legacy_upload=legacy_enabled)

    with mock.patch("insights.client.auto_config.utilities.get_rhel_version", return_value=rhel):
        autoconfigure_network(client_config=client_config)

    assert client_config.base_url == expected_url
    assert client_config.proxy == "https://user:password@proxy.internal:443"
