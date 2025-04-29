import configparser

from insights.client.auto_config import autoconfigure_network
from insights.client.config import InsightsConfig
from insights.client.connection import InsightsConnection
from mock.mock import Mock
from mock.mock import patch
from pytest import mark


@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_inventory_url_from_base_url(get_proxies, init_session):
    """
    Inventory URL is composed correctly from the given base URL.
    """
    config = Mock(base_url="www.example.com")
    connection = InsightsConnection(config)
    assert connection.inventory_url == "https://www.example.com/inventory/v1"


@mark.parametrize(
    "input",
    [{"check_results": True}, {"checkin": True}],
    ids=["--check-results", "--checkin"]
)
@patch("insights.client.auto_config.rhsmCertificate.existsAndValid", return_value=True)
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
@patch('insights.client.config.argparse.ArgumentParser.parse_args')
def test_inventory_url_from_phase(
    _parse_args,
    _get_proxies,
    _init_session,
    _rhsm_is_registered,
    input,
):
    """Inventory URL is composed correctly from the default configuration."""
    rhsm_config = configparser.ConfigParser()
    rhsm_config.read_string(
        u"[server]\n"
        u"hostname=subscription.rhsm.redhat.com\nport=443\n"
        u"proxy_scheme=http\nproxy_hostname=\nproxy_port=\n"
        u"proxy_user=\nproxy_password=\n"
        u"no_proxy=\n"
    )

    config = InsightsConfig(**input)
    with patch("insights.client.auto_config.get_rhsm_config", return_value=rhsm_config):
        with patch("insights.client.auto_config.utilities.get_rhel_version", return_value=9):
            autoconfigure_network(config)
    connection = InsightsConnection(config)
    assert connection.inventory_url == "https://cert.cloud.redhat.com/api/inventory/v1"
