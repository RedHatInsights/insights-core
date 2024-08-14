from logging import ERROR
from mock.mock import patch

from pytest import fixture
from pytest import mark
from requests.exceptions import ConnectTimeout
from requests.exceptions import ReadTimeout
from requests.exceptions import SSLError

from insights.client.config import InsightsConfig
from insights.client.connection import InsightsConnection

EXCEPTION_MESSAGE = "exception"
EXPECTED_EXCEPTIONS = [SSLError, ConnectTimeout, ReadTimeout]

LOGGING_FILE = "logging-file.log"

parametrize_exceptions = mark.parametrize(
    ["exception"],
    [(exception(EXCEPTION_MESSAGE),) for exception in EXPECTED_EXCEPTIONS],
)


@fixture
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
def insights_connection(get_proxies, init_session):
    config = InsightsConfig(base_url="www.example.com", logging_file=LOGGING_FILE)

    connection = InsightsConnection(config)
    connection.proxies = None

    return connection


@parametrize_exceptions
@patch("insights.client.connection.InsightsConnection._test_urls")
def test_request_failed_test_urls(test_urls, exception, insights_connection):
    """The whole connection test is stopped when an API call fails."""
    test_urls.side_effect = exception

    insights_connection.test_connection()
    test_urls.assert_called_once()


@parametrize_exceptions
@patch("insights.client.connection.InsightsConnection._test_urls")
def test_request_failed_print_exception(test_urls, exception, insights_connection, capsys):
    """A message with is printed, describing the error and pointing to the log file."""
    test_urls.side_effect = exception

    insights_connection.test_connection()
    out, err = capsys.readouterr()
    assert out == "%s\nAdditional information may be in %s\n" % (EXCEPTION_MESSAGE, LOGGING_FILE)


@parametrize_exceptions
@patch("insights.client.connection.InsightsConnection._test_urls")
def test_request_failed_error_log(test_urls, exception, insights_connection, caplog):
    """An error message is logged on the ERROR level."""
    test_urls.side_effect = exception

    with caplog.at_level(ERROR, logger="insights.client.connection"):
        insights_connection.test_connection()

    assert caplog.record_tuples == [(
        "insights.client.connection",
        ERROR,
        "Connectivity test failed! Please check your network configuration"
    )]


@parametrize_exceptions
@patch("insights.client.connection.InsightsConnection._test_urls")
def test_request_failed_return_code(test_urls, exception, insights_connection):
    """Status code 1 is returned from the function."""
    test_urls.side_effect = exception

    result = insights_connection.test_connection()
    assert result == 1
