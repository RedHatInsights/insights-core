from insights.client.connection import InsightsConnection
from mock.mock import Mock, patch


@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_request(get_proxies, patch_init_session):
    """
    The request to get branch info is issued with correct timeout set.
    """
    config = Mock(base_url="www.example.com", branch_info_url="https://www.example.com/branch_info")

    connection = InsightsConnection(config)
    connection.branch_info()

    patch_init_session.return_value.get.assert_called_once_with(config.branch_info_url, timeout=config.http_timeout)
