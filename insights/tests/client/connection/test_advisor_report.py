import json
import os
import pytest
from unittest.mock import MagicMock, Mock, mock_open, patch
from insights.client.constants import InsightsConstants as constants
from insights.client.connection import InsightsConnection
from insights.client.config import InsightsConfig


@patch("insights.client.connection.InsightsConnection._init_session")
@patch('insights.client.utilities.generate_machine_id')
@patch('insights.client.connection.InsightsConnection.get')
@patch('insights.client.connection.os.path.isfile', return_value=False)
def test_unregistered_check_results(_is_file, get, generate_machine_id, _init_session):
    config = InsightsConfig()
    connection = InsightsConnection(config)

    with pytest.raises(Exception):
        connection.get_advisor_report()

    assert not os.path.isfile(constants.registered_files[0])
    generate_machine_id.assert_not_called()
    get.assert_not_called()


def _response(status, body):
    res = MagicMock()
    res.status_code = status
    res.content = json.dumps(body).encode("utf-8")
    return res


@patch("builtins.open", mock_open())
@patch("os.makedirs")
@patch("os.path.exists", return_value=True)
@patch("insights.client.connection.os.path.isfile", return_value=True)
@patch("insights.client.connection.generate_machine_id", return_value="machine-1")
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
@pytest.mark.parametrize("legacy,document_status,expected,urls", [
    # a system document is returned as-is
    (False, 200, {"reports": 1}, [
        "https://example.com/inventory/v1/hosts?insights_id=machine-1",
        "https://example.com/insights/v1/system/inv-1",
    ]),
    # not indexed yet: the reports collection is the result --check-results needs
    (False, 404, [], [
        "https://example.com/inventory/v1/hosts?insights_id=machine-1",
        "https://example.com/insights/v1/system/inv-1",
        "https://example.com/insights/v1/system/inv-1/reports/",
    ]),
    # legacy keeps the document and the reports under different roots
    (True, 404, [], [
        "https://example.com/platform/inventory/v1/hosts?insights_id=machine-1",
        "https://example.com/v1/system/inv-1",
        "https://example.com/platform/insights/v1/system/inv-1/reports/",
    ]),
    # anything but a 404 is a failure, not an indexing gap
    (False, 500, None, [
        "https://example.com/inventory/v1/hosts?insights_id=machine-1",
        "https://example.com/insights/v1/system/inv-1",
    ]),
])
def test_advisor_report(get_proxies, _init_session, _machine_id, _isfile, _exists, _makedirs,
                        legacy, document_status, expected, urls):
    config = Mock(legacy_upload=legacy, base_url="example.com")
    conn = InsightsConnection(config)
    hosts = _response(200, {"total": 1, "results": [{"id": "inv-1"}]})
    document = _response(document_status, {"reports": 1})
    reports = _response(200, [])

    def _get(url, **kwargs):
        if "/hosts?" in url:
            return hosts
        if url.endswith("/reports/"):
            return reports
        return document

    conn.get = MagicMock(side_effect=_get)
    assert conn.get_advisor_report() == expected
    assert [call[0][0] for call in conn.get.call_args_list] == urls
