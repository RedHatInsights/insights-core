from insights.client.auto_config import try_auto_configuration
from insights.client.config import InsightsConfig
from insights.client.connection import InsightsConnection
from mock.mock import Mock
from mock.mock import patch
from pytest import mark
from sys import argv


@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_inventory_url_from_base_url(get_proxies, init_session):
    """
    Inventory URL is composed correctly from the given base URL.
    """
    config = Mock(base_url="www.example.com")
    connection = InsightsConnection(config)
    assert connection.inventory_url == "https://www.example.com/inventory/v1"


@mark.parametrize(("config_kwargs",), (({"check_results": True},), ({"checkin": True},)))
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
@patch("insights.client.auto_config._try_satellite6_configuration")
@patch('insights.client.config.sys.argv', [argv[0]])
def test_inventory_url_from_phase(
        try_satellite6_configuration,
        get_proxies,
        init_session,
        config_kwargs
):
    """
    Inventory URL is composed correctly from the default configuration.
    """
    config = InsightsConfig(**config_kwargs)
    config.load_all()  # Disables legacy upload.
    try_auto_configuration(config)  # Updates base_url if legacy upload is disabled.
    connection = InsightsConnection(config)
    assert connection.inventory_url == "https://cert-api.access.redhat.com/r/insights/platform/inventory/v1"
