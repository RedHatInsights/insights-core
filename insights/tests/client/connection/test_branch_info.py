from insights.client.connection import InsightsConnection
from mock.mock import Mock, patch


@patch("insights.client.connection.InsightsConnection.new_session")
@patch("insights.client.connection.constants.cached_branch_info", "/tmp/insights-test-cached-branchinfo")
def test_request(new_session):
    """
    The request to get branch info is issued with correct timeout set.
    """
    config = Mock(base_url="www.example.com", branch_info_url="https://www.example.com/branch_info")

    connection = InsightsConnection(config)
    connection.branch_info()

    new_session.return_value.get.assert_called_once_with(config.branch_info_url)
