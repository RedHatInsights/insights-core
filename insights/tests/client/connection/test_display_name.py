import json
import requests
import pytest
from unittest.mock import MagicMock, Mock, patch

from insights.client.connection import InsightsConnection


def _response(status, body):
    res = MagicMock()
    res.status_code = status
    res.content = json.dumps(body).encode("utf-8")
    res.text = json.dumps(body)
    return res


@pytest.mark.parametrize("status", [404, 409])
@patch("insights.client.connection.generate_machine_id", return_value="machine-1")
@patch("insights.client.connection.InsightsConnection._init_session", Mock())
@patch("insights.client.connection.InsightsConnection.get_proxies", Mock())
@patch("insights.client.connection.constants.registered_files", [__file__])
def test_legacy_set_display_name_falls_back_to_inventory(_machine_id, status):
    '''
    The classic system lookup misses while Inventory has no insights_id
    for the host (CCT-2662). The name is set through Inventory instead of
    reporting the host as not registered.
    '''
    conn = InsightsConnection(Mock(legacy_upload=True, base_url="example.com"))
    conn.get = MagicMock(return_value=_response(status, {"detail": "not found"}))
    conn.patch = MagicMock(return_value=_response(200, {}))
    with patch.object(conn, "_fetch_system_by_machine_id",
                      return_value={"id": "inv-1"}) as fetch:
        assert conn.set_display_name("new-name") is True

    fetch.assert_called_once()
    url = conn.patch.call_args[0][0]
    assert url == "https://example.com/platform/inventory/v1/hosts/inv-1"
    assert conn.patch.call_args[1]["json"] == {"display_name": "new-name"}


@patch("insights.client.connection.generate_machine_id", return_value="machine-1")
@patch("insights.client.connection.InsightsConnection._init_session", Mock())
@patch("insights.client.connection.InsightsConnection.get_proxies", Mock())
@patch("insights.client.connection.constants.registered_files", [__file__])
def test_legacy_set_display_name_keeps_classic_path(_machine_id):
    '''
    A classic 200 is still handled by the classic PUT, without Inventory.
    '''
    conn = InsightsConnection(Mock(legacy_upload=True, base_url="example.com"))
    conn.get = MagicMock(
        return_value=_response(200, {"display_name": "old-name"}))
    conn.put = MagicMock(return_value=_response(200, {}))
    conn.patch = MagicMock()
    with patch.object(conn, "_fetch_system_by_machine_id") as fetch:
        assert conn.set_display_name("new-name") is True

    fetch.assert_not_called()
    conn.patch.assert_not_called()
    assert conn.put.call_args[1]["data"] == json.dumps(
        {"display_name": "new-name"})


@patch("insights.client.connection.InsightsConnection._init_session", Mock())
@patch("insights.client.connection.InsightsConnection.get_proxies", Mock())
@patch("insights.client.connection.constants.registered_files", [__file__])
def test_legacy_set_display_name_unreachable():
    '''
    A connection error is still a failure, not a not-found host.
    '''
    conn = InsightsConnection(Mock(legacy_upload=True, base_url="example.com"))
    conn.get = MagicMock(side_effect=requests.ConnectionError)
    assert conn.set_display_name("new-name") is False


@pytest.mark.parametrize("legacy_upload", [True, False])
@patch("insights.client.connection.InsightsConnection._init_session", Mock())
@patch("insights.client.connection.InsightsConnection.get_proxies", Mock())
@patch("insights.client.connection.constants.registered_files",
       ["/nonexistent/insights-client/.registered"])
def test_set_display_name_requires_registration(legacy_upload):
    '''
    An unregistered system must not be renamed, even though Inventory
    already holds the host subscription-manager created (CCT-2662).
    '''
    conn = InsightsConnection(Mock(legacy_upload=legacy_upload, base_url="example.com"))
    conn.get = MagicMock()
    conn.put = MagicMock()
    conn.patch = MagicMock()
    assert conn.set_display_name("new-name") is False
    conn.get.assert_not_called()
    conn.put.assert_not_called()
    conn.patch.assert_not_called()
