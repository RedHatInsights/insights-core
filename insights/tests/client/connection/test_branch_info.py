from insights.client.connection import InsightsConnection
from mock.mock import Mock, patch


@patch("insights.client.connection.json.dumps")
@patch("insights.client.connection.InsightsConnection.get")
@patch("insights.client.connection.InsightsConnection._init_session", Mock())
@patch("insights.client.connection.InsightsConnection.get_proxies", Mock())
@patch("insights.client.connection.constants.cached_branch_info", "/tmp/insights-test-cached-branchinfo")
def test_request(get, dumps):
    """
    The request to get branch info is issued with correct timeout set.
    """
    config = Mock(base_url="www.example.com", branch_info_url="https://www.example.com/branch_info")

    connection = InsightsConnection(config)
    connection.get_branch_info()

    get.assert_called_once_with(config.branch_info_url)
    dumps.assert_called_once_with(get.return_value.json.return_value)
