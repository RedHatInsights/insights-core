from mock.mock import Mock, patch
from insights.client.connection import InsightsConnection


@patch('insights.client.connection.largest_spec_in_archive', return_value=("insights/big", 100, "insights.spec-big"))
def test_archive_too_big(largest_archive_file):
    config = Mock(base_url="www.example.com", proxy=None)
    connection = InsightsConnection(config)
    with patch("insights.client.connection.os.stat", **{"return_value.st_size": 104857600}):
        with patch('insights.client.connection.logger.info') as mock_logger:
            connection._archive_too_big("archive_file")
            largest_archive_file.assert_called_once_with("archive_file")
            assert mock_logger.call_count == 3
            assert ["insights.spec-big" in args[0][0] for args in mock_logger.call_args_list]
