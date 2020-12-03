from mock.mock import Mock
from mock.mock import patch
from insights.client.connection import InsightsConnection


@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_inventory_url(get_proxies, init_session):
    """
    Inventory URL is composed correctly.
    """
    config = Mock(base_url="www.example.com", insecure_connection=False)
    connection = InsightsConnection(config)
    assert connection.inventory_url == "https://www.example.com/inventory/v1"
