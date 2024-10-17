import pytest
import requests
from mock import mock

from insights.client.config import InsightsConfig
from insights.client.connection import InsightsConnection

LOGGING_FILE = "logging-file.log"

EXPECTED_EXCEPTIONS = [
    requests.exceptions.SSLError,
    requests.exceptions.ConnectTimeout,
    requests.exceptions.ReadTimeout,
]
parametrize_exceptions = pytest.mark.parametrize(
    ["exception"],
    [(exception,) for exception in EXPECTED_EXCEPTIONS],
)


class UnexpectedException(Exception):
    pass


@pytest.fixture
@mock.patch("insights.client.connection.InsightsConnection._init_session")
@mock.patch("insights.client.connection.InsightsConnection.get_proxies")
def insights_connection(get_proxies, init_session):
    config = InsightsConfig(base_url="www.example.com", logging_file=LOGGING_FILE)

    connection = InsightsConnection(config)
    connection.proxies = None

    return connection


@mock.patch("insights.client.connection.InsightsConnection._test_urls")
def test_test_connection_test_urls_no_catch(test_urls, insights_connection):
    """The connection test is stopped in case of an unknown exception."""
    test_urls.side_effect = UnexpectedException

    try:
        insights_connection.test_connection()
    except UnexpectedException:
        pass

    test_urls.assert_called_once()


@mock.patch("insights.client.connection.InsightsConnection._test_urls")
def test_test_connection_test_urls_success(test_urls, insights_connection):
    """The connection test performs several API calls in case of no error."""
    insights_connection.test_connection()
    assert len(test_urls.mock_calls) > 1


@parametrize_exceptions
@mock.patch("insights.client.connection.InsightsConnection._test_urls")
def test_test_connection_test_urls_fail(test_urls, exception, insights_connection):
    """The connection test is stopped after the first API call failure."""
    test_urls.side_effect = exception

    insights_connection.test_connection()
    test_urls.assert_called_once()


@mock.patch("insights.client.connection.logger")
@mock.patch("insights.client.connection.InsightsConnection._test_urls")
def test_test_connection_error_log_no_catch(test_urls, logger, insights_connection):
    """The connection test doesn't log any ERROR in case of an unknown exception."""
    test_urls.side_effect = UnexpectedException

    try:
        insights_connection.test_connection()
    except UnexpectedException:
        pass

    logger.error.assert_not_called()


@mock.patch("insights.client.connection.logger")
@mock.patch("insights.client.connection.InsightsConnection._test_urls")
def test_test_connection_error_log_success(test_urls, logger, insights_connection):
    """The connection test doesn't log any ERROR if all API calls succeed."""
    insights_connection.test_connection()

    logger.error.assert_not_called()


@parametrize_exceptions
@mock.patch("insights.client.connection.logger")
@mock.patch("insights.client.connection.InsightsConnection._test_urls")
def test_test_connection_error_log_fail(
    test_urls, logger, exception, insights_connection
):
    """An error message is logged on the ERROR level."""
    test_urls.side_effect = exception

    insights_connection.test_connection()

    logger.error.assert_called_once_with(
        "Connectivity test failed! Please check your network configuration"
    )


@mock.patch("insights.client.connection.InsightsConnection._test_urls")
def test_test_connection_print_no_catch(test_urls, insights_connection, capsys):
    """The connection test doesn't print anything in case of an unknown exception."""
    test_urls.side_effect = UnexpectedException

    try:
        insights_connection.test_connection()
    except UnexpectedException:
        pass

    out, err = capsys.readouterr()
    assert not out
    assert not err


@mock.patch("insights.client.connection.InsightsConnection._test_urls")
def test_test_connection_print_success(test_urls, insights_connection, capsys):
    """The connection test prints a message pointing to a log file if all API calls succeed."""
    insights_connection.test_connection()

    out, err = capsys.readouterr()
    assert out == "See {0} for more details.\n".format(
        LOGGING_FILE,
    )
    assert not err


@parametrize_exceptions
@mock.patch("insights.client.connection.InsightsConnection._test_urls")
def test_test_connection_print_fail(test_urls, exception, insights_connection, capsys):
    """The connection test prints a message pointing to a log file if an API call fails."""
    message = "request exception"
    test_urls.side_effect = exception(message)

    insights_connection.test_connection()
    out, err = capsys.readouterr()
    assert out == "{0}\nAdditional information may be in {1}\n".format(
        message,
        LOGGING_FILE,
    )
    assert not err


@mock.patch("insights.client.connection.InsightsConnection._test_urls")
def test_test_connection_no_catch(test_urls, insights_connection):
    """The connection test doesn't catch and recreate an unknown exception."""
    expected = UnexpectedException()
    test_urls.side_effect = expected

    with pytest.raises(UnexpectedException) as caught:
        insights_connection.test_connection()

    assert caught.value is expected
