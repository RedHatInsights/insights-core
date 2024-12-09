from json import dumps
from uuid import uuid4

from mock.mock import Mock, patch
from pytest import mark
from pytest import raises
from requests import ConnectionError
from requests import Timeout
from requests import codes

from insights.core.plugins import make_metadata
from insights.client.connection import InsightsConnection
from insights.client.config import InsightsConfig
from insights.util.hostname import determine_hostname


def _get_canonical_facts_response(canonical_facts):
    d = make_metadata(**canonical_facts)
    d.update(hostname=determine_hostname(), ip='10.0.0.1')
    del d["type"]
    return d


@patch('insights.client.connection.InsightsUploadConf.get_rm_conf', return_value={})
@patch(
    "insights.client.connection.InsightsConnection._init_session", Mock())
@patch("insights.client.connection.InsightsConnection._fetch_system_by_machine_id", return_value=True)
@patch(
    "insights.client.connection.get_canonical_facts",
    return_value=_get_canonical_facts_response({"subscription_manager_id": str(uuid4())})
)
@patch(
    "insights.client.connection.InsightsConnection.post",
    **{"return_value.status_code": codes.CREATED}
)
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_canonical_facts_request(get_proxies, post, get_canonical_facts, fetch_system_by_machine_id, rm_conf):
    """
    A POST requests to the check-in endpoint is issued with correct headers and
    body containing unobfuscated Canonical Facts.
    """
    config = InsightsConfig(base_url="www.example.com", obfuscate=False)

    connection = InsightsConnection(config)
    connection.checkin()

    expected_url = connection.inventory_url + "/hosts/checkin"
    expected_headers = {"Content-Type": "application/json"}
    expected_data = get_canonical_facts.return_value
    post.assert_called_once_with(
        expected_url, headers=expected_headers, data=dumps(expected_data), log_response_text=False
    )


@patch('insights.client.connection.InsightsUploadConf.get_rm_conf', return_value={})
@patch(
    "insights.client.connection.InsightsConnection._init_session", Mock())
@patch("insights.client.connection.InsightsConnection._fetch_system_by_machine_id", return_value=True)
@patch(
    "insights.client.connection.get_canonical_facts",
    return_value=_get_canonical_facts_response({"subscription_manager_id": str(uuid4())})
)
@patch(
    "insights.client.connection.InsightsConnection.post",
    **{"return_value.status_code": codes.CREATED}
)
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_canonical_facts_request_cleaned(get_proxies, post, get_canonical_facts, fetch_system_by_machine_id, rm_conf):
    """
    A POST requests to the check-in endpoint is issued with correct headers and
    body containing obfuscateed Canonical Facts.
    """
    config = InsightsConfig(base_url="www.example.com", obfuscate=True, obfuscate_hostname=True)

    connection = InsightsConnection(config)
    connection.checkin()

    expected_url = connection.inventory_url + "/hosts/checkin"
    expected_headers = {"Content-Type": "application/json"}
    expected_data = get_canonical_facts.return_value
    expected_data = connection._clean_facts(expected_data)
    post.assert_called_once_with(
        expected_url, headers=expected_headers, data=dumps(expected_data), log_response_text=False
    )


@patch('insights.client.connection.InsightsUploadConf.get_rm_conf', return_value={})
@patch(
    "insights.client.connection.InsightsConnection._init_session", Mock())
@patch("insights.client.connection.InsightsConnection._fetch_system_by_machine_id", return_value=True)
@patch("insights.client.connection.generate_machine_id", return_value=str(uuid4()))
@patch("insights.client.connection.get_canonical_facts", side_effect=RuntimeError())
@patch(
    "insights.client.connection.InsightsConnection.post",
    **{"return_value.status_code": codes.CREATED}
)
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_insights_id_request(get_proxies, post, get_canonical_facts, generate_machine_id, fetch_system_by_machine_id, rm_conf):
    """
    A POST requests to the check-in endpoint is issued with correct headers and
    body containing only an Insights ID if Canonical Facts collection fails.
    """
    config = InsightsConfig(base_url="www.example.com")

    connection = InsightsConnection(config)
    connection.checkin()

    expected_url = connection.inventory_url + "/hosts/checkin"
    expected_headers = {"Content-Type": "application/json"}
    expected_data = {"insights_id": generate_machine_id.return_value}
    post.assert_called_once_with(
        expected_url, headers=expected_headers, data=dumps(expected_data), log_response_text=False
    )


@mark.parametrize(("exception",), ((ConnectionError,), (Timeout,)))
@patch('insights.client.connection.InsightsUploadConf.get_rm_conf', return_value={})
@patch("insights.client.connection.InsightsConnection._init_session", Mock())
@patch("insights.client.connection.InsightsConnection._fetch_system_by_machine_id", return_value=True)
@patch(
    "insights.client.connection.get_canonical_facts",
    return_value=_get_canonical_facts_response({"subscription_manager_id": "notauuid"})
)
@patch("insights.client.connection.InsightsConnection.post")
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_request_http_failure(get_proxies, post, get_canonical_facts, fetch_system_by_machine_id, rm_conf, exception):
    """
    If the checkin-request fails, None is returned.
    """
    post.side_effect = exception

    config = InsightsConfig(base_url="www.example.com")

    connection = InsightsConnection(config)
    result = connection.checkin()
    assert result is None


@patch('insights.client.connection.InsightsUploadConf.get_rm_conf', return_value={})
@patch("insights.client.connection.InsightsConnection._init_session", Mock())
@patch("insights.client.connection.InsightsConnection._fetch_system_by_machine_id", return_value=True)
@patch("insights.client.connection.get_canonical_facts", return_value={})
@patch(
    "insights.client.connection.InsightsConnection.post",
    **{"side_effect": RuntimeError()}
)
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_request_unknown_exception(get_proxies, post, get_canonical_facts, fetch_system_by_machine_id, rm_conf):
    """
    If an unknown exception occurs, the call crashes.
    """
    config = InsightsConfig(base_url="www.example.com")
    connection = InsightsConnection(config)

    expected_exception = type(post.side_effect)
    with raises(expected_exception):
        connection.checkin()


@patch('insights.client.connection.InsightsUploadConf.get_rm_conf', return_value={})
@patch("insights.client.connection.InsightsConnection._init_session", Mock())
@patch("insights.client.connection.InsightsConnection._fetch_system_by_machine_id", return_value=True)
@patch("insights.client.connection.get_canonical_facts", return_value={})
@patch(
    "insights.client.connection.InsightsConnection.post",
    **{"return_value.status_code": codes.CREATED}
)
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_response_success(get_proxies, post, get_canonical_facts, fetch_system_by_machine_id, rm_conf):
    """
    If a CREATED status code is received, the check-in was successful.
    """
    config = InsightsConfig(base_url="www.example.com")
    connection = InsightsConnection(config)

    result = connection.checkin()
    assert result is True


@mark.parametrize(
    ("status_code",),
    ((codes.OK,), (codes.BAD_REQUEST,), (codes.NOT_FOUND,), (codes.SERVER_ERROR,))
)
@patch('insights.client.connection.InsightsUploadConf.get_rm_conf', return_value={})
@patch("insights.client.connection.InsightsConnection._init_session", Mock())
@patch("insights.client.connection.InsightsConnection._fetch_system_by_machine_id", return_value=True)
@patch("insights.client.connection.get_canonical_facts", return_value=_get_canonical_facts_response({}))
@patch("insights.client.connection.InsightsConnection.post")
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_response_failure(get_proxies, post, get_canonical_facts, fetch_system_by_machine_id, rm_conf, status_code):
    """
    If an unexpected status code is received, the check-in failed and an exception is raised.
    """
    post.return_value.status_code = status_code

    config = InsightsConfig(base_url="www.example.com")
    connection = InsightsConnection(config)

    with raises(Exception):
        connection.checkin()


@patch('insights.client.connection.InsightsUploadConf.get_rm_conf', return_value={})
@patch("insights.client.connection.InsightsConnection._init_session", Mock())
@patch("insights.client.connection.InsightsConnection._fetch_system_by_machine_id", return_value=False)
@patch("insights.client.connection.get_canonical_facts")
@patch("insights.client.connection.InsightsConnection.post")
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_unregistered_host(get_proxies, post, get_canonical_facts, fetch_system_by_machine_id, rm_conf):
    """
    If the host is not registered, the checkin fails.
    """
    config = InsightsConfig(base_url="www.example.com")
    connection = InsightsConnection(config)

    result = connection.checkin()
    assert result is False
    get_canonical_facts.assert_not_called()
    post.assert_not_called()
