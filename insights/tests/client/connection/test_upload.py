from mock.mock import Mock, patch
import logging
from insights.client.connection import InsightsConnection


@patch('insights.client.connection.largest_spec_in_archive', return_value=("insights/big", 100, "insights.spec-big"))
def test_archive_too_big(largest_archive_file, caplog):
    config = Mock(base_url="www.example.com", proxy=None)
    connection = InsightsConnection(config)
    caplog.set_level(logging.INFO)
    with patch("insights.client.connection.os.stat", **{"return_value.st_size": 104857600}):
        connection._archive_too_big("archive_file")
        largest_archive_file.assert_called_once_with("archive_file")
        assert len(caplog.records) == 3
        assert ["insights.spec-big" in rec.message for rec in caplog.records]
        record = next(iter(caplog.records))
        assert record.message == "Archive is 100.0 MB which is larger than the maximum allowed size of 100 MB."
