from json import dumps
from uuid import uuid4

from mock.mock import Mock, patch
from pytest import mark
from pytest import raises
from requests import ConnectionError
from requests import Timeout
from requests import codes

from insights.client.connection import InsightsConnection


@patch("insights.client.connection.get_canonical_facts", return_value={"subscription_manager_id": str(uuid4())})
@patch(
    "insights.client.connection.InsightsConnection._init_session",
    **{"return_value.put.return_value.status_code": codes.OK}
)
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_canonical_facts_request(get_proxies, init_session, get_canonical_facts):
    """
    A PUT requests to the check-in endpoint is issued with correct headers and
    body containing Canonical Facts.
    """
    config = Mock(base_url="www.example.com")

    connection = InsightsConnection(config)
    connection.checkin()

    expected_url = connection.inventory_url + "/hosts/checkin"
    expected_headers = {"Content-Type": "application/json"}
    expected_data = {"canonical_facts": get_canonical_facts.return_value}
    init_session.return_value.put.assert_called_once_with(
        expected_url, headers=expected_headers, data=dumps(expected_data)
    )


@patch("insights.client.connection.generate_machine_id", return_value=str(uuid4()))
@patch("insights.client.connection.get_canonical_facts", side_effect=RuntimeError())
@patch(
    "insights.client.connection.InsightsConnection._init_session",
    **{"return_value.put.return_value.status_code": codes.OK}
)
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_insights_id_request(get_proxies, init_session, get_canonical_facts, generate_machine_id):
    """
    A PUT requests to the check-in endpoint is issued with correct headers and
    body containing only an Insights ID if Canonical Facts collection fails.
    """
    config = Mock(base_url="www.example.com")

    connection = InsightsConnection(config)
    connection.checkin()

    expected_url = connection.inventory_url + "/hosts/checkin"
    expected_headers = {"Content-Type": "application/json"}
    expected_data = {"canonical_facts": {"insights_id": generate_machine_id.return_value}}
    init_session.return_value.put.assert_called_once_with(
        expected_url, headers=expected_headers, data=dumps(expected_data)
    )


@mark.parametrize(("exception",), ((ConnectionError,), (Timeout,)))
@patch("insights.client.connection.get_canonical_facts", return_value={})
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_request_http_failure(get_proxies, init_session, get_canonical_facts, exception):
    """
    If the checkin-request fails, None is returned.
    """
    init_session.return_value.put.side_effect = exception

    config = Mock(base_url="www.example.com")

    connection = InsightsConnection(config)
    result = connection.checkin()
    assert result is None


@patch("insights.client.connection.get_canonical_facts", return_value={})
@patch("insights.client.connection.InsightsConnection._init_session", **{"return_value.put.side_effect": RuntimeError()})
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_request_unknown_exception(get_proxies, init_session, get_canonical_facts):
    """
    If an unknown exception occurs, the call crashes.
    """
    config = Mock(base_url="www.example.com")
    connection = InsightsConnection(config)

    expected_exception = type(init_session.return_value.put.side_effect)
    with raises(expected_exception):
        connection.checkin()


@mark.parametrize(("status_code",), ((codes.OK,), (codes.CREATED,)))
@patch("insights.client.connection.get_canonical_facts", return_value={})
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_response_success(get_proxies, init_session, get_canonical_facts, status_code):
    """
    If an unknown exception occurs, the call crashes.
    """
    init_session.return_value.put.return_value.status_code = status_code

    config = Mock(base_url="www.example.com")
    connection = InsightsConnection(config)

    result = connection.checkin()
    assert result is True


@mark.parametrize(("status_code",), ((codes.BAD_REQUEST,), (codes.NOT_FOUND,), (codes.SERVER_ERROR,)))
@patch("insights.client.connection.get_canonical_facts", return_value={})
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_response_failure(get_proxies, init_session, get_canonical_facts, status_code):
    """
    If an unknown exception occurs, the call crashes.
    """
    init_session.return_value.put.return_value.status_code = status_code

    config = Mock(base_url="www.example.com")
    connection = InsightsConnection(config)

    with raises(Exception):
        connection.checkin()
