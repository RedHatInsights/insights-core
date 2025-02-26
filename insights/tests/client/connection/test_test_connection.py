import logging
import socket
import ssl
from unittest.mock import patch

import pytest
import requests
import tempfile
from mock import mock

from insights.client.config import InsightsConfig
from insights.client.constants import InsightsConstants
from insights.client.connection import InsightsConnection


class UnexpectedException(Exception):
    pass


LOGGING_FILE = "logging-file.log"
UPLOAD_URL = "https://www.example.com/insights"
LEGACY_URL = "https://www.example.com"
LEGACY_URL_SUFFIXES = ["/insights/", "", "/r", "/r/insights"]

EXCEPTION_MESSAGE = "request exception"
EXPECTED_EXCEPTIONS = [
    requests.exceptions.SSLError,
    requests.exceptions.ConnectTimeout,
    requests.exceptions.ReadTimeout,
]

parametrize_exceptions = pytest.mark.parametrize(
    ["exception"],
    [(exception,) for exception in EXPECTED_EXCEPTIONS],
)
parametrize_methods = pytest.mark.parametrize(
    ["http_method", "request_function"],
    [
        ("GET", "insights.client.connection.InsightsConnection.get"),
        ("POST", "insights.client.connection.InsightsConnection.post"),
    ],
)
parametrize_legacy_upload = pytest.mark.parametrize(
    ["legacy_upload"], [(True,), (False,)]
)


def _response(**kwargs):
    response = requests.Response()

    if "headers" in kwargs:
        headers = kwargs.pop("headers")
        response.headers.update(headers)

    for key, value in kwargs.items():
        setattr(response, key, value)
    return response


def _exception(exception, context):
    exception.__context__ = Exception()
    exception.__context__.__context__ = context
    return exception


@mock.patch("insights.client.connection.InsightsConnection._init_session")
@mock.patch("insights.client.connection.InsightsConnection.get_proxies")
def _insights_connection(get_proxies, init_session, **config_kwargs):
    config_kwargs = {
        "base_url": "www.example.com",
        "logging_file": LOGGING_FILE,
        "upload_url": UPLOAD_URL,
        **config_kwargs,
    }
    config = InsightsConfig(**config_kwargs)

    connection = InsightsConnection(config)
    connection.proxies = None

    return connection


@pytest.fixture
def insights_connection(request):
    marker = request.node.get_closest_marker("insights_config")
    config_kwargs = marker.kwargs if marker else {}
    return _insights_connection(**config_kwargs)


def _valid_auth_config(insights_connection):
    insights_connection.authmethod = "BASIC"
    insights_connection.username = "insights"
    insights_connection.password = "insights"

    return [
        (
            "insights.client.connection",
            logging.INFO,
            "Authentication: login credentials (BASIC)",
        ),
        (
            "insights.client.connection",
            logging.INFO,
            "  Username: insights",
        ),
        (
            "insights.client.connection",
            logging.INFO,
            "  Password: ********",
        ),
        ("insights.client.connection", logging.INFO, ""),
    ]


def _url_config(insights_connection):
    if insights_connection.proxies:
        proxy = "HTTPS proxy URL: {}".format(insights_connection.proxies["https"])
    else:
        proxy = "No proxy."

    messages = [
        "URL configuration:",
        "  Base URL: {}".format(insights_connection.base_url),
        "  {}".format(proxy),
        "",
    ]
    return [
        ("insights.client.connection", logging.INFO, message) for message in messages
    ]


@pytest.mark.skip
@parametrize_methods
@mock.patch("insights.client.connection.InsightsConnection._legacy_test_urls")
def test_test_urls_legacy_test_urls_call(
    legacy_test_urls, http_method, request_function, insights_connection
):
    """The non-legacy URL subtest hands over to its legacy counterpart if legacy_upload is enabled."""
    insights_connection.config.legacy_upload = True

    insights_connection._test_urls(UPLOAD_URL, http_method)

    legacy_test_urls.assert_called_once_with(UPLOAD_URL, http_method)


@pytest.mark.skip
@parametrize_methods
@mock.patch("insights.client.connection.InsightsConnection._legacy_test_urls")
def test_test_urls_legacy_test_urls_result(
    legacy_test_urls, http_method, request_function, insights_connection
):
    """The non-legacy URL subtest returns from its legacy counterpart if legacy_upload is enabled."""
    insights_connection.config.legacy_upload = True

    result = insights_connection._test_urls(UPLOAD_URL, http_method)

    assert result == legacy_test_urls.return_value


@pytest.mark.skip
@parametrize_methods
@mock.patch("insights.client.connection.TemporaryFile")
@mock.patch("insights.client.connection.InsightsConnection._legacy_test_urls")
def test_test_urls_not_legacy_test_urls(
    legacy_test_urls, temporary_file, http_method, request_function, insights_connection
):
    """The non-legacy URL subtest doesn't hand over to its legacy counterpart if legacy_upload is disabled."""
    insights_connection.config.legacy_upload = False

    with mock.patch(request_function):
        insights_connection._test_urls(UPLOAD_URL, http_method)
    legacy_test_urls.assert_not_called()


@pytest.mark.skip
@mock.patch("insights.client.connection.InsightsConnection.post")
@mock.patch("insights.client.connection.TemporaryFile")
@mock.patch("insights.client.connection.InsightsConnection.get")
def test_test_urls_get_no_catch(get, temporary_file, post, insights_connection):
    """The non-legacy URL subtest issues one GET request in case of an unknown exception."""
    get.side_effect = UnexpectedException
    insights_connection.config.legacy_upload = False

    try:
        insights_connection._test_urls(UPLOAD_URL, "GET")
    except UnexpectedException:
        pass

    get.assert_called_once_with(UPLOAD_URL)
    post.assert_not_called()


@pytest.mark.skip
@mock.patch("insights.client.connection.InsightsConnection.post")
@mock.patch("insights.client.connection.TemporaryFile")
@mock.patch("insights.client.connection.InsightsConnection.get")
def test_test_urls_get_success(get, temporary_file, post, insights_connection):
    """The non-legacy URL subtest issues one GET request if the API call succeeds."""
    insights_connection.config.legacy_upload = False

    insights_connection._test_urls(UPLOAD_URL, "GET")

    get.assert_called_once_with(UPLOAD_URL)
    post.assert_not_called()


@pytest.mark.skip
@parametrize_exceptions
@mock.patch("insights.client.connection.InsightsConnection.post")
@mock.patch("insights.client.connection.TemporaryFile")
@mock.patch("insights.client.connection.InsightsConnection.get")
def test_test_urls_get_fail(get, temporary_file, post, insights_connection, exception):
    """The non-legacy URL subtest issues one GET request if the API call fails."""
    get.side_effect = exception
    insights_connection.config.legacy_upload = False

    try:
        insights_connection._test_urls(UPLOAD_URL, "GET")
    except exception:
        pass

    get.assert_called_once_with(UPLOAD_URL)
    post.assert_not_called()


@pytest.mark.skip
@mock.patch("insights.client.connection.InsightsConnection.post")
@mock.patch("insights.client.connection.TemporaryFile")
@mock.patch("insights.client.connection.InsightsConnection.get")
def test_test_urls_post_no_catch(get, temporary_file, post, insights_connection):
    """The non-legacy URL subtest issues one POST request in case of an unknown exception."""
    post.side_effect = UnexpectedException
    insights_connection.config.legacy_upload = False

    try:
        insights_connection._test_urls(UPLOAD_URL, "POST")
    except UnexpectedException:
        pass

    post.assert_called_once_with(UPLOAD_URL, files=mock.ANY)
    get.assert_not_called()


@pytest.mark.skip
@mock.patch("insights.client.connection.InsightsConnection.post")
@mock.patch("insights.client.connection.TemporaryFile")
@mock.patch("insights.client.connection.InsightsConnection.get")
def test_test_urls_post_success(get, temporary_file, post, insights_connection):
    """The non-legacy URL subtest issues one POST request if the API call succeeds."""
    insights_connection.config.legacy_upload = False

    insights_connection._test_urls(UPLOAD_URL, "POST")
    post.assert_called_once_with(UPLOAD_URL, files=mock.ANY)
    get.assert_not_called()


@pytest.mark.skip
@parametrize_exceptions
@mock.patch("insights.client.connection.InsightsConnection.post")
@mock.patch("insights.client.connection.TemporaryFile")
@mock.patch("insights.client.connection.InsightsConnection.get")
def test_test_urls_post_fail(get, temporary_file, post, exception, insights_connection):
    """The non-legacy URL subtest issues one POST request if the API call fails."""
    post.side_effect = exception
    insights_connection.config.legacy_upload = False

    try:
        insights_connection._test_urls(UPLOAD_URL, "POST")
    except exception:
        pass

    post.assert_called_once_with(UPLOAD_URL, files=mock.ANY)
    get.assert_not_called()


@pytest.mark.skip
@parametrize_methods
@mock.patch("insights.client.connection.TemporaryFile")
def test_test_urls_no_catch(
    temporary_file, http_method, request_function, insights_connection
):
    """The non-legacy URL subtest doesn't catch unknown exceptions."""
    insights_connection.config.legacy_upload = False

    raised = UnexpectedException()

    with pytest.raises(UnexpectedException) as caught:
        with mock.patch(request_function) as request_function_mock:
            request_function_mock.side_effect = raised
            insights_connection._test_urls(UPLOAD_URL, http_method)

    assert caught.value is raised


@pytest.mark.skip
@parametrize_exceptions
@parametrize_methods
@mock.patch("insights.client.connection.TemporaryFile")
def test_test_urls_raise(
    temporary_file, http_method, request_function, exception, insights_connection
):
    """The non-legacy URL subtest re-raises the API call failure exception."""
    insights_connection.config.legacy_upload = False

    raised = exception()

    with pytest.raises(exception) as caught:
        with mock.patch(request_function) as request_function_mock:
            request_function_mock.side_effect = raised
            insights_connection._test_urls(UPLOAD_URL, http_method)

    assert caught.value is raised


@pytest.mark.skip
@parametrize_methods
def test_test_urls_error_log_no_catch(
    http_method, request_function, insights_connection, caplog
):
    """The non-legacy URL subtest doesn't log any errors in case of an unknown exception."""
    insights_connection.config.legacy_upload = False

    with caplog.at_level(logging.ERROR, logger="insights.client.connection"):
        with mock.patch(request_function) as request_function_mock:
            request_function_mock.side_effect = UnexpectedException
            try:
                insights_connection._test_urls(UPLOAD_URL, http_method)
            except UnexpectedException:
                pass

    assert not caplog.record_tuples


@pytest.mark.skip
@parametrize_methods
def test_test_urls_error_log_success(
    http_method, request_function, insights_connection, caplog
):
    """The non-legacy URL subtest doesn't log any errors if all API calls succeed."""
    insights_connection.config.legacy_upload = False

    with caplog.at_level(logging.ERROR, logger="insights.client.connection"):
        with mock.patch(request_function):
            insights_connection._test_urls(UPLOAD_URL, http_method)

    assert not caplog.record_tuples


@pytest.mark.skip
@parametrize_exceptions
@parametrize_methods
def test_test_urls_error_log_fail(
    http_method, request_function, exception, insights_connection, caplog
):
    """The non-legacy URL subtest logs an ERROR if an API call fails."""
    insights_connection.config.legacy_upload = False

    with caplog.at_level(logging.ERROR, logger="insights.client.connection"):
        try:
            with mock.patch(request_function) as request_function_mock:
                request_function_mock.side_effect = exception
                insights_connection._test_urls(UPLOAD_URL, http_method)
        except exception:
            pass

    assert caplog.record_tuples == [
        (
            "insights.client.connection",
            logging.ERROR,
            "Could not successfully connect to: {0}".format(UPLOAD_URL),
        )
    ]


@pytest.mark.skip
@parametrize_methods
def test_test_urls_print_no_catch(
    http_method, request_function, insights_connection, capsys
):
    """The non-legacy URL subtest doesn't print anything in case of an unknown exception."""
    insights_connection.config.legacy_upload = False

    with mock.patch(request_function) as request_function_mock:
        request_function_mock.side_effect = UnexpectedException
        try:
            insights_connection._test_urls(UPLOAD_URL, http_method)
        except UnexpectedException:
            pass

    out, err = capsys.readouterr()
    assert not out
    assert not err


@pytest.mark.skip
@parametrize_methods
def test_test_urls_print_success(
    http_method, request_function, insights_connection, capsys
):
    """The non-legacy URL subtest doesn't print anything if all API calls succeed."""
    insights_connection.config.legacy_upload = False

    with mock.patch(request_function):
        insights_connection._test_urls(UPLOAD_URL, http_method)

    out, err = capsys.readouterr()
    assert not out
    assert not err


@pytest.mark.skip
@parametrize_exceptions
@parametrize_methods
def test_test_urls_print_fail(
    http_method, request_function, exception, insights_connection, capsys
):
    """The non-legacy URL subtest prints the exception details if an API call fails."""
    insights_connection.config.legacy_upload = False

    with mock.patch(request_function) as request_function_mock:
        request_function_mock.side_effect = exception(EXCEPTION_MESSAGE)
        try:
            insights_connection._test_urls(UPLOAD_URL, http_method)
        except exception:
            pass

    out, err = capsys.readouterr()
    assert out == "{0}\n".format(EXCEPTION_MESSAGE)
    assert not err


@pytest.mark.skip
@mock.patch("insights.client.connection.InsightsConnection.post")
@mock.patch("insights.client.connection.InsightsConnection.get")
def test_legacy_test_urls_get_no_catch(get, post, insights_connection):
    """The legacy URL subtest issues one GET request in case of an unknown exception."""
    get.side_effect = UnexpectedException

    try:
        insights_connection._legacy_test_urls(UPLOAD_URL, "GET")
    except UnexpectedException:
        pass

    get.assert_called_once_with(LEGACY_URL + LEGACY_URL_SUFFIXES[0])
    post.assert_not_called()


@pytest.mark.skip
@mock.patch("insights.client.connection.InsightsConnection.post")
@mock.patch("insights.client.connection.InsightsConnection.get")
def test_legacy_test_urls_get_success(get, post, insights_connection):
    """The non-legacy URL subtest issues one GET request if the API call succeeds."""
    insights_connection._legacy_test_urls(UPLOAD_URL, "GET")

    get.assert_called_once_with(LEGACY_URL + LEGACY_URL_SUFFIXES[0])
    post.assert_not_called()


@pytest.mark.skip
@parametrize_exceptions
@mock.patch("insights.client.connection.InsightsConnection.post")
@mock.patch("insights.client.connection.InsightsConnection.get")
def test_legacy_test_urls_get_one_fail(get, post, exception, insights_connection):
    """The non-legacy URL subtest issues one GET request if one API call fails."""
    get.side_effect = [exception, mock.Mock()]

    insights_connection._legacy_test_urls(UPLOAD_URL, "GET")

    assert get.mock_calls == [
        mock.call(LEGACY_URL + LEGACY_URL_SUFFIXES[0]),
        mock.call(LEGACY_URL + LEGACY_URL_SUFFIXES[1]),
    ]
    post.assert_not_called()


@pytest.mark.skip
@parametrize_exceptions
@mock.patch("insights.client.connection.InsightsConnection.post")
@mock.patch("insights.client.connection.InsightsConnection.get")
def test_legacy_test_urls_get_all_fails(get, post, exception, insights_connection):
    """The non-legacy URL subtest issues one GET request for every API call if the previous one fails."""
    get.side_effect = [exception] * len(LEGACY_URL_SUFFIXES)

    try:
        insights_connection._legacy_test_urls(UPLOAD_URL, "GET")
    except exception:
        pass

    assert get.mock_calls == [
        mock.call(LEGACY_URL + suffix) for suffix in LEGACY_URL_SUFFIXES
    ]
    post.assert_not_called()


@pytest.mark.skip
@mock.patch("insights.client.connection.InsightsConnection.post")
@mock.patch("insights.client.connection.InsightsConnection.get")
def test_legacy_test_urls_post_no_catch(get, post, insights_connection):
    """The legacy URL subtest issues one POST request in case of an unknown exception."""
    post.side_effect = UnexpectedException

    try:
        insights_connection._legacy_test_urls(UPLOAD_URL, "POST")
    except UnexpectedException:
        pass

    post.assert_called_once_with(LEGACY_URL + LEGACY_URL_SUFFIXES[0], data=mock.ANY)
    get.assert_not_called()


@pytest.mark.skip
@mock.patch("insights.client.connection.InsightsConnection.post")
@mock.patch("insights.client.connection.InsightsConnection.get")
def test_legacy_test_urls_post_success(get, post, insights_connection):
    """The non-legacy URL subtest issues one POST request if the API call succeeds."""
    insights_connection._legacy_test_urls(UPLOAD_URL, "POST")

    post.assert_called_once_with(LEGACY_URL + LEGACY_URL_SUFFIXES[0], data=mock.ANY)
    get.assert_not_called()


@pytest.mark.skip
@parametrize_exceptions
@mock.patch("insights.client.connection.InsightsConnection.post")
@mock.patch("insights.client.connection.InsightsConnection.get")
def test_legacy_test_urls_post_one_fail(get, post, exception, insights_connection):
    """The non-legacy URL subtest issues one POST request if one API call fails."""
    post.side_effect = [exception, mock.Mock(status_code=requests.codes.ok)]

    insights_connection._legacy_test_urls(UPLOAD_URL, "POST")

    assert post.mock_calls == [
        mock.call(LEGACY_URL + LEGACY_URL_SUFFIXES[0], data=mock.ANY),
        mock.call(LEGACY_URL + LEGACY_URL_SUFFIXES[1], data=mock.ANY),
    ]
    get.assert_not_called()


@pytest.mark.skip
@parametrize_exceptions
@mock.patch("insights.client.connection.InsightsConnection.post")
@mock.patch("insights.client.connection.InsightsConnection.get")
def test_legacy_test_urls_post_all_fails(get, post, exception, insights_connection):
    """The non-legacy URL subtest issues one POST request for every API call if the previous one fails."""
    post.side_effect = [exception] * len(LEGACY_URL_SUFFIXES)

    try:
        insights_connection._legacy_test_urls(UPLOAD_URL, "POST")
    except exception:
        pass

    assert post.mock_calls == [
        mock.call(LEGACY_URL + suffix, data=mock.ANY) for suffix in LEGACY_URL_SUFFIXES
    ]
    get.assert_not_called()


@pytest.mark.skip
@parametrize_methods
def test_legacy_test_urls_no_catch(http_method, request_function, insights_connection):
    """The legacy URL subtest doesn't catch unknown exceptions."""
    raised = UnexpectedException()

    with pytest.raises(UnexpectedException) as caught:
        with mock.patch(request_function) as request_function_mock:
            request_function_mock.side_effect = raised
            insights_connection._legacy_test_urls(UPLOAD_URL, http_method)

    assert caught.value is raised


@pytest.mark.skip
@parametrize_exceptions
@parametrize_methods
def test_legacy_test_urls_raise(
    http_method, request_function, exception, insights_connection
):
    """The legacy URL subtest re-raises the last API call failure exception."""
    exceptions = [exception() for _ in LEGACY_URL_SUFFIXES]

    with pytest.raises(exception) as caught:
        with mock.patch(request_function) as request_function_mock:
            request_function_mock.side_effect = exceptions
            insights_connection._legacy_test_urls(UPLOAD_URL, http_method)

    assert caught.value is exceptions[-1]


@pytest.mark.skip
@parametrize_methods
def test_legacy_test_urls_error_log_no_catch(
    http_method, request_function, insights_connection, caplog
):
    """The legacy URL subtest doesn't log any errors in case of an unknown exception."""
    with caplog.at_level(logging.ERROR, logger="insights.client.connection"):
        with mock.patch(request_function) as request_function_mock:
            request_function_mock.side_effect = UnexpectedException
            try:
                insights_connection._legacy_test_urls(UPLOAD_URL, http_method)
            except UnexpectedException:
                pass

    assert not caplog.record_tuples


@pytest.mark.skip
@parametrize_exceptions
@parametrize_methods
def test_legacy_test_urls_error_log_success(
    http_method, request_function, exception, insights_connection, caplog
):
    """The legacy URL subtest doesn't log any errors if the API call succeeds."""
    with caplog.at_level(logging.ERROR, logger="insights.client.connection"):
        with mock.patch(request_function):
            insights_connection._legacy_test_urls(UPLOAD_URL, http_method)

    assert not caplog.record_tuples


@pytest.mark.skip
@parametrize_exceptions
@parametrize_methods
def test_legacy_test_urls_error_log_one_fail(
    http_method, request_function, exception, insights_connection, caplog
):
    """The legacy URL subtest logs one ERROR if one API call fails."""
    with caplog.at_level(logging.ERROR, logger="insights.client.connection"):
        try:
            with mock.patch(request_function) as request_function_mock:
                request_function_mock.side_effect = [exception(), mock.Mock()]
                insights_connection._legacy_test_urls(UPLOAD_URL, http_method)
        except exception:
            pass

    assert caplog.record_tuples == [
        (
            "insights.client.connection",
            logging.ERROR,
            "Could not successfully connect to: {0}".format(
                LEGACY_URL + LEGACY_URL_SUFFIXES[0]
            ),
        )
    ]


@pytest.mark.skip
@parametrize_exceptions
@parametrize_methods
def test_legacy_test_urls_error_log_all_fails(
    http_method, request_function, exception, insights_connection, caplog
):
    """The legacy URL subtest logs one ERROR for every failed API call."""
    with caplog.at_level(logging.ERROR, logger="insights.client.connection"):
        try:
            with mock.patch(request_function) as request_function_mock:
                request_function_mock.side_effect = [
                    exception() for _ in LEGACY_URL_SUFFIXES
                ]
                insights_connection._legacy_test_urls(UPLOAD_URL, http_method)
        except exception:
            pass

    assert caplog.record_tuples == [
        (
            "insights.client.connection",
            logging.ERROR,
            "Could not successfully connect to: {0}{1}".format(LEGACY_URL, suffix),
        )
        for suffix in LEGACY_URL_SUFFIXES
    ]


@pytest.mark.skip
@parametrize_methods
def test_legacy_test_urls_exception_print_no_catch(
    http_method, request_function, insights_connection, capsys
):
    """The legacy URL subtest doesn't print anything in case of an unknown exception."""
    with mock.patch(request_function) as request_function_mock:
        request_function_mock.side_effect = UnexpectedException
        try:
            insights_connection._legacy_test_urls(UPLOAD_URL, http_method)
        except UnexpectedException:
            pass

    out, err = capsys.readouterr()
    assert not out
    assert not err


@pytest.mark.skip
@parametrize_exceptions
@parametrize_methods
def test_legacy_test_urls_exception_print_success(
    http_method, request_function, exception, insights_connection, capsys
):
    """The legacy URL subtest prints a message pointing to a log file if the API call succeeds."""
    with mock.patch(request_function):
        insights_connection._legacy_test_urls(UPLOAD_URL, http_method)

    out, err = capsys.readouterr()
    assert not out
    assert not err


@pytest.mark.skip
@parametrize_exceptions
@parametrize_methods
def test_legacy_test_urls_exception_print_one_fail(
    http_method, request_function, exception, insights_connection, capsys
):
    """The legacy URL subtest prints the exception details if one API call fails."""
    try:
        with mock.patch(request_function) as request_function_mock:
            request_function_mock.side_effect = [
                exception(EXCEPTION_MESSAGE),
                mock.Mock(),
            ]
            insights_connection._legacy_test_urls(UPLOAD_URL, http_method)
    except exception:
        pass

    out, err = capsys.readouterr()
    assert out == "{0}\n".format(EXCEPTION_MESSAGE)
    assert not err


@pytest.mark.skip
@parametrize_exceptions
@parametrize_methods
def test_legacy_test_urls_exception_print_all_fails(
    http_method, request_function, exception, insights_connection, capsys
):
    """The legacy connection test prints the details for every exception if all API calls fail."""
    exception_messages = [
        "{0} {1}".format(EXCEPTION_MESSAGE, suffix) for suffix in LEGACY_URL_SUFFIXES
    ]
    exceptions = [exception(message) for message in exception_messages]

    try:
        with mock.patch(request_function) as request_function_mock:
            request_function_mock.side_effect = exceptions
            insights_connection._legacy_test_urls(UPLOAD_URL, http_method)
    except exception:
        pass

    out, err = capsys.readouterr()
    assert out == "".join("{0}\n".format(message) for message in exception_messages)
    assert not err


@pytest.mark.skip
@mock.patch("insights.client.connection.InsightsConnection._test_urls")
def test_test_connection_test_urls_no_catch(test_urls, insights_connection):
    """The connection test doesn't catch unknown exceptions."""
    test_urls.side_effect = UnexpectedException

    try:
        insights_connection.test_connection()
    except UnexpectedException:
        pass

    test_urls.assert_called_once()


@pytest.mark.skip
@mock.patch("insights.client.connection.InsightsConnection._test_urls")
def test_test_connection_test_urls_success(test_urls, insights_connection):
    """The connection test performs several API calls in case of no error."""
    insights_connection.test_connection()
    assert len(test_urls.mock_calls) > 1


@pytest.mark.skip
@parametrize_exceptions
@mock.patch("insights.client.connection.InsightsConnection._test_urls")
def test_test_connection_test_urls_fail(test_urls, exception, insights_connection):
    """The connection test is stopped after the first API call failure."""
    test_urls.side_effect = exception

    insights_connection.test_connection()
    test_urls.assert_called_once()


@pytest.mark.skip
@mock.patch("insights.client.connection.InsightsConnection._test_urls")
def test_test_connection_error_log_no_catch(test_urls, insights_connection, caplog):
    """The connection test doesn't log any ERROR in case of an unknown exception."""
    test_urls.side_effect = UnexpectedException

    with caplog.at_level(logging.ERROR, logger="insights.client.connection"):
        try:
            insights_connection.test_connection()
        except UnexpectedException:
            pass

    assert not caplog.record_tuples


@pytest.mark.skip
@mock.patch("insights.client.connection.InsightsConnection._test_urls")
def test_test_connection_error_log_success(test_urls, insights_connection, caplog):
    """The connection test doesn't log any ERROR if all API calls succeed."""
    with caplog.at_level(logging.ERROR, logger="insights.client.connection"):
        insights_connection.test_connection()

    assert not caplog.record_tuples


@pytest.mark.skip
@parametrize_exceptions
@mock.patch("insights.client.connection.InsightsConnection._test_urls")
def test_test_connection_error_log_fail(
    test_urls, exception, insights_connection, caplog
):
    """An error message is logged on the ERROR level."""
    test_urls.side_effect = exception

    with caplog.at_level(logging.ERROR, logger="insights.client.connection"):
        insights_connection.test_connection()

    assert caplog.record_tuples == [
        (
            "insights.client.connection",
            logging.ERROR,
            "Connectivity test failed! Please check your network configuration",
        )
    ]


@pytest.mark.skip
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


@pytest.mark.skip
@mock.patch("insights.client.connection.InsightsConnection._test_urls")
def test_test_connection_print_success(test_urls, insights_connection, capsys):
    """The connection test prints a message pointing to a log file if all API calls succeed."""
    insights_connection.test_connection()

    out, err = capsys.readouterr()
    assert out == "See {0} or use --verbose for more details.\n".format(LOGGING_FILE)
    assert not err


@pytest.mark.skip
@parametrize_exceptions
@mock.patch("insights.client.connection.InsightsConnection._test_urls")
def test_test_connection_print_fail(test_urls, exception, insights_connection, capsys):
    """The connection test prints a message pointing to a log file if an API call fails."""
    test_urls.side_effect = exception("request exception")

    insights_connection.test_connection()
    out, err = capsys.readouterr()
    assert out == "Additional information may be in {0}\n".format(
        LOGGING_FILE,
    )
    assert not err


@pytest.mark.skip
@mock.patch("insights.client.connection.InsightsConnection._test_urls")
def test_test_connection_no_catch(test_urls, insights_connection):
    """The connection test doesn't catch and recreate an unknown exception."""
    expected = UnexpectedException()
    test_urls.side_effect = expected

    with pytest.raises(UnexpectedException) as caught:
        insights_connection.test_connection()

    assert caught.value is expected


@pytest.mark.skip
@mock.patch("insights.client.connection.InsightsConnection.post")
@mock.patch("insights.client.connection.TemporaryFile")
def test_test_connection_non_legacy_error_log_no_catch(
    temporary_file, post, insights_connection, caplog
):
    """The non-legacy connection test doesn't log any errors in case of an unknown exception."""
    post.side_effect = UnexpectedException
    insights_connection.config.legacy_upload = False

    with caplog.at_level(logging.ERROR, logger="insights.client.connection"):
        try:
            insights_connection.test_connection()
        except UnexpectedException:
            pass

    assert not caplog.record_tuples


@pytest.mark.skip
@mock.patch("insights.client.connection.InsightsConnection.get")
@mock.patch("insights.client.connection.InsightsConnection.post")
@mock.patch("insights.client.connection.TemporaryFile")
def test_test_connection_non_legacy_error_log_success(
    temporary_file, post, get, insights_connection, caplog
):
    """The non-legacy connection test doesn't log any errors if all API calls succeed."""
    insights_connection.config.legacy_upload = False

    with caplog.at_level(logging.ERROR, logger="insights.client.connection"):
        insights_connection.test_connection()

    assert not caplog.record_tuples


@pytest.mark.skip
@parametrize_exceptions
@mock.patch("insights.client.connection.InsightsConnection.post")
@mock.patch("insights.client.connection.TemporaryFile")
def test_test_connection_non_legacy_error_log_fail(
    temporary_file, post, exception, insights_connection, caplog
):
    """The connection test logs an ERROR if an API call fails."""
    post.side_effect = exception
    insights_connection.config.legacy_upload = False

    with caplog.at_level(logging.ERROR, logger="insights.client.connection"):
        insights_connection.test_connection()

    assert caplog.record_tuples == [
        ("insights.client.connection", logging.ERROR, message)
        for message in [
            "Could not successfully connect to: {0}".format(UPLOAD_URL),
            "Connectivity test failed! Please check your network configuration",
        ]
    ]


@pytest.mark.skip
@mock.patch("insights.client.connection.InsightsConnection.post")
@mock.patch("insights.client.connection.TemporaryFile")
def test_test_connection_non_legacy_print_no_catch(
    temporary_file, post, insights_connection, capsys
):
    """The non-legacy connection test doesn't print anything in case of an unknown exception."""
    post.side_effect = UnexpectedException
    insights_connection.config.legacy_upload = False

    try:
        insights_connection.test_connection()
    except UnexpectedException:
        pass

    out, err = capsys.readouterr()
    assert not out
    assert not err


@pytest.mark.skip
@mock.patch("insights.client.connection.InsightsConnection.get")
@mock.patch("insights.client.connection.InsightsConnection.post")
@mock.patch("insights.client.connection.TemporaryFile")
def test_test_connection_non_legacy_print_success(
    temporary_file, post, get, insights_connection, capsys
):
    """The non-legacy connection test prints a message pointing to a log file if all API calls succeed."""
    insights_connection.config.legacy_upload = False

    insights_connection.test_connection()

    out, err = capsys.readouterr()
    assert out == "See {0} or use --verbose for more details.\n".format(LOGGING_FILE)
    assert not err


@pytest.mark.skip
@parametrize_exceptions
@mock.patch("insights.client.connection.InsightsConnection.post")
@mock.patch("insights.client.connection.TemporaryFile")
def test_test_connection_non_legacy_print_fail(
    temporary_file, post, exception, insights_connection, capsys
):
    """The non-legacy connection test prints the exception details and a message pointing to a log file if an API call fails."""
    post.side_effect = exception(EXCEPTION_MESSAGE)
    insights_connection.config.legacy_upload = False

    insights_connection.test_connection()

    out, err = capsys.readouterr()
    assert out == "{0}\nAdditional information may be in {1}\n".format(
        EXCEPTION_MESSAGE, LOGGING_FILE
    )
    assert not err


@pytest.mark.skip
@mock.patch("insights.client.connection.InsightsConnection.post")
def test_test_connection_legacy_error_log_no_catch(post, insights_connection, caplog):
    """The legacy connection test doesn't log any errors in case of an unknown exception."""
    post.side_effect = UnexpectedException
    insights_connection.config.legacy_upload = True

    with caplog.at_level(logging.ERROR, logger="insights.client.connection"):
        try:
            insights_connection.test_connection()
        except UnexpectedException:
            pass

    assert not caplog.record_tuples


@pytest.mark.skip
@parametrize_exceptions
@mock.patch("insights.client.connection.InsightsConnection.post")
def test_test_connection_legacy_error_log_success(
    post, exception, insights_connection, caplog
):
    """The legacy connection test doesn't log any errors if all API calls succeed."""
    insights_connection.config.legacy_upload = True

    with caplog.at_level(logging.ERROR, logger="insights.client.connection"):
        insights_connection.test_connection()

    assert not caplog.record_tuples


@pytest.mark.skip
@parametrize_exceptions
@mock.patch("insights.client.connection.InsightsConnection.post")
def test_test_connection_legacy_error_log_one_fail_connection(
    post, exception, insights_connection, caplog
):
    """The connection test logs one ERROR if one API call fails."""
    post.side_effect = [exception, mock.Mock()]
    insights_connection.config.legacy_upload = True

    with caplog.at_level(logging.ERROR, logger="insights.client.connection"):
        insights_connection.test_connection()

    assert caplog.record_tuples == [
        (
            "insights.client.connection",
            logging.ERROR,
            "Could not successfully connect to: {0}".format(
                LEGACY_URL + LEGACY_URL_SUFFIXES[0]
            ),
        )
    ]


@pytest.mark.skip
@parametrize_exceptions
@mock.patch("insights.client.connection.InsightsConnection.post")
def test_test_connection_legacy_error_log_all_fails_connection(
    post, exception, insights_connection, caplog
):
    """The connection test logs one ERROR for every failed API call."""
    post.side_effect = exception
    insights_connection.config.legacy_upload = True

    with caplog.at_level(logging.ERROR, logger="insights.client.connection"):
        insights_connection.test_connection()

    legacy_test_url_errors = [
        "Could not successfully connect to: {0}{1}".format(LEGACY_URL, suffix)
        for suffix in LEGACY_URL_SUFFIXES
    ]
    test_connection_errors = [
        "Connectivity test failed! Please check your network configuration",
    ]
    assert caplog.record_tuples == [
        ("insights.client.connection", logging.ERROR, message)
        for message in legacy_test_url_errors + test_connection_errors
    ]


@pytest.mark.skip
@mock.patch("insights.client.connection.InsightsConnection.post")
@mock.patch("insights.client.connection.TemporaryFile")
def test_test_connection_legacy_print_no_catch(
    temporary_file, post, insights_connection, capsys
):
    """The legacy connection test doesn't print anything in case of an unknown exception."""
    post.side_effect = UnexpectedException
    insights_connection.config.legacy_upload = False

    try:
        insights_connection.test_connection()
    except UnexpectedException:
        pass

    out, err = capsys.readouterr()
    assert not out
    assert not err


@pytest.mark.skip
@mock.patch("insights.client.connection.InsightsConnection.post")
@mock.patch("insights.client.connection.TemporaryFile")
def test_test_connection_legacy_print_success(
    temporary_file, post, insights_connection, capsys
):
    """The legacy connection test prints a message pointing to a log file if all API calls succeed."""
    insights_connection.config.legacy_upload = False

    insights_connection.test_connection()

    out, err = capsys.readouterr()
    assert out == "See {0} or use --verbose for more details.\n".format(LOGGING_FILE)
    assert not err


@pytest.mark.skip
@parametrize_exceptions
@mock.patch("insights.client.connection.InsightsConnection.post")
def test_test_connection_legacy_print_one_fail(
    post, exception, insights_connection, capsys
):
    """The legacy connection test prints the exception details and a message pointing to a log file if one API call fails."""
    post.side_effect = [exception(EXCEPTION_MESSAGE), mock.Mock()]
    insights_connection.config.legacy_upload = True

    insights_connection.test_connection()

    out, err = capsys.readouterr()
    assert out == "{0}\nSee {1} or use --verbose for more details.\n".format(
        EXCEPTION_MESSAGE, LOGGING_FILE
    )
    assert not err


@pytest.mark.skip
@parametrize_exceptions
@mock.patch("insights.client.connection.InsightsConnection.post")
def test_test_connection_legacy_print_all_fails(
    post, exception, insights_connection, capsys
):
    """The legacy connection test prints the details for every exception and a message pointing to a log file if all API calls fail."""
    exception_messages = [
        exception("{0} {1}".format(EXCEPTION_MESSAGE, suffix))
        for suffix in LEGACY_URL_SUFFIXES
    ]
    post.side_effect = [exception(message) for message in exception_messages]
    insights_connection.config.legacy_upload = True

    insights_connection.test_connection()

    out, err = capsys.readouterr()

    test_urls_messages = ["{0}\n".format(message) for message in exception_messages]
    test_connection_messages = [
        "Additional information may be in {0}\n".format(LOGGING_FILE)
    ]

    assert out == "".join(test_urls_messages + test_connection_messages)
    assert not err


@pytest.mark.parametrize(
    ["username", "password", "info_username", "info_password", "errors"],
    [
        (None, "insights", "NOT SET", "********", ["Username NOT SET"]),
        (None, "insights", "NOT SET", "********", ["Username NOT SET"]),
        ("insights", None, "insights", "NOT SET", ["Password NOT SET"]),
        (None, None, "NOT SET", "NOT SET", ["Username NOT SET", "Password NOT SET"]),
    ],
)
def test_test_connection_basic_auth_incomplete_credentials_log(
    username,
    password,
    info_username,
    info_password,
    errors,
    insights_connection,
    caplog,
):
    """An error is printed if BASIC auth credentials are incomplete: a username or a password is missing."""
    insights_connection.authmethod = "BASIC"
    insights_connection.username = username
    insights_connection.password = password

    with caplog.at_level(logging.INFO):
        insights_connection.test_connection()

    messages = (
        [
            (logging.INFO, "Authentication: login credentials (BASIC)"),
            (logging.INFO, "  Username: {}".format(info_username)),
            (logging.INFO, "  Password: {}".format(info_password)),
            (logging.INFO, ""),
            (logging.ERROR, "ERROR. Cannot authenticate:"),
        ]
        + [(logging.ERROR, "  {}.".format(error)) for error in errors]
        + [
            (
                logging.ERROR,
                '  Check your "username" and "password" in {}.'.format(
                    insights_connection.config.conf
                ),
            ),
            (logging.ERROR, ""),
        ]
    )
    record_tuples = [
        ("insights.client.connection", loglevel, message)
        for loglevel, message in messages
    ]
    assert caplog.record_tuples == record_tuples


@pytest.mark.parametrize(
    ["username", "password", "expected_rc"],
    [
        ("insights", "insights", 0),
        (None, "insights", 1),
        ("insights", None, 1),
        (None, None, 1),
    ],
)
def test_test_connection_basic_auth_incomplete_credentials_return_value(
    username, password, expected_rc, insights_connection
):
    """An exit code 1 (error) is returned if BASIC auth credentials are incomplete."""
    insights_connection.authmethod = "BASIC"
    insights_connection.username = username
    insights_connection.password = password

    insights_connection.session.request.return_value = _response(
        status_code=requests.codes.ok
    )

    actual_rc = insights_connection.test_connection()
    assert expected_rc == actual_rc


@pytest.mark.parametrize(
    ("certificate_exists", "key_exists"),
    [
        (True, False),
        (False, True),
        (False, False),
    ],
)
@mock.patch("insights.client.connection.rhsmCertificate.keypath")
@mock.patch("insights.client.connection.rhsmCertificate.certpath")
def test_test_connection_basic_auth_incomplete_key_pair_log(
    certpath,
    keypath,
    certificate_exists,
    key_exists,
    insights_connection,
    caplog,
):
    """An error is printed if a CERT key pair file (a certificate or a key) is missing."""
    insights_connection.authmethod = "CERT"

    tempfiles = []
    errors = []
    for exists, path, title in [
        (certificate_exists, certpath, "Certificate"),
        (key_exists, keypath, "Key"),
    ]:
        if exists:
            file = tempfile.NamedTemporaryFile("w")
            tempfiles.append(file)
            path.return_value = file.name
        else:
            path.return_value = "invalid"
            errors.append("{} file {} MISSING.".format(title, path.return_value))

    with caplog.at_level(logging.INFO):
        try:
            insights_connection.test_connection()
        finally:
            for file in tempfiles:
                file.close()

    exists_description = {True: "exists", False: "NOT FOUND"}
    messages = (
        [
            (logging.INFO, "Authentication: identity certificate (CERT)"),
            (
                logging.INFO,
                "  Certificate: {} ({})".format(
                    certpath.return_value, exists_description[certificate_exists]
                ),
            ),
            (
                logging.INFO,
                "  Key: {} ({})".format(
                    keypath.return_value, exists_description[key_exists]
                ),
            ),
            (logging.INFO, ""),
            (logging.ERROR, "ERROR. Cannot authenticate:"),
        ]
        + [(logging.ERROR, "  {}".format(error)) for error in errors]
        + [
            (
                logging.ERROR,
                '  Re-register the system by running "subscription-manager unregister" and then '
                '"subscription-manager register".',
            ),
            (logging.ERROR, ""),
        ]
    )

    record_tuples = [
        ("insights.client.connection", loglevel, message)
        for loglevel, message in messages
    ]
    assert caplog.record_tuples == record_tuples


@pytest.mark.insights_config(authmethod="INVALID")
def test_test_connection_unknown_auth_log(insights_connection, caplog):
    with caplog.at_level(logging.INFO):
        insights_connection.test_connection()

    messages = [
        (logging.INFO, "Authentication: unknown"),
        (logging.INFO, ""),
        (logging.ERROR, "ERROR. Cannot authenticate:"),
        (logging.ERROR, '  Unknown authentication method "INVALID".'),
        (
            logging.ERROR,
            '  Set "authmethod" in {} to "BASIC" for username/password login or to "CERT" for authentication'
            " with a certificate.".format(insights_connection.config.conf),
        ),
        (logging.ERROR, ""),
    ]

    record_tuples = [
        ("insights.client.connection", loglevel, message)
        for loglevel, message in messages
    ]
    assert caplog.record_tuples == record_tuples


@pytest.mark.insights_config(authmethod="INVALID")
def test_test_connection_unknown_auth_return_value(insights_connection):
    rc = insights_connection.test_connection()
    assert rc == 1


@pytest.mark.parametrize(
    ("certificate_exists", "key_exists", "expected_rc"),
    [
        (True, True, 0),
        (True, False, 1),
        (False, True, 1),
        (False, False, 1),
    ],
)
@mock.patch("insights.client.connection.rhsmCertificate.keypath")
@mock.patch("insights.client.connection.rhsmCertificate.certpath")
def test_test_connection_basic_auth_incomplete_key_pair_return_value(
    certpath,
    keypath,
    certificate_exists,
    key_exists,
    expected_rc,
    insights_connection,
):
    """An exit code 1 (error) is returned if a CERT key pair file (a certificate or a key) is missing."""
    insights_connection.authmethod = "CERT"
    insights_connection.session.request.return_value = _response(
        status_code=requests.codes.ok
    )

    tempfiles = []
    for exists, path, title in [
        (certificate_exists, certpath, "Certificate"),
        (key_exists, keypath, "Key"),
    ]:
        if exists:
            file = tempfile.NamedTemporaryFile("w")
            tempfiles.append(file)
            path.return_value = file.name
        else:
            path.return_value = "invalid"

    try:
        actual_rc = insights_connection.test_connection()
    finally:
        for file in tempfiles:
            file.close()

    assert actual_rc == expected_rc


@pytest.mark.parametrize(
    ["proxy_url", "proxy_url_loglevel", "proxy_url_line", "proxy_url_errors"],
    [
        (
            "http://insights:insights:localhost",
            logging.ERROR,
            "HTTPS proxy URL: http://insights:insights:localhost (INVALID!)",
            ["INVALID HTTPS proxy URL"],
        ),
        (
            "http:///",
            logging.ERROR,
            "HTTPS proxy URL: http:/// (INCOMPLETE!)",
            ["Hostname MISSING in HTTPS proxy URL"],
        ),
        (
            "localhost",
            logging.ERROR,
            "HTTPS proxy URL: localhost (INCOMPLETE!)",
            ["Protocol MISSING in HTTPS proxy URL"],
        ),
    ],
)
@pytest.mark.parametrize(
    ["base_url", "base_url_loglevel", "base_url_line", "base_url_errors"],
    [
        (
            "https://insights:insights:insights/",
            logging.ERROR,
            "Base URL: https://insights:insights:insights/ (INVALID!)",
            ["INVALID Base URL"],
        ),
        (
            "https:///",
            logging.ERROR,
            "Base URL: https:/// (INCOMPLETE!)",
            ["Hostname MISSING in Base URL"],
        ),
        (
            "insights",
            logging.ERROR,
            "Base URL: insights (INCOMPLETE!)",
            ["Protocol MISSING in Base URL"],
        ),
    ],
)
def test_test_connection_url_invalid_log(
    base_url,
    base_url_loglevel,
    base_url_line,
    base_url_errors,
    proxy_url,
    proxy_url_loglevel,
    proxy_url_line,
    proxy_url_errors,
    insights_connection,
    caplog,
):
    """An error is printed if the Base or the Proxy URL is invalid or incomplete."""
    insights_connection.base_url = base_url
    insights_connection.proxies = {"https": proxy_url}
    auth_record_tuples = _valid_auth_config(insights_connection)

    with caplog.at_level(logging.INFO):
        insights_connection.test_connection()

    errors = base_url_errors + proxy_url_errors
    messages = [
        (logging.INFO, "URL configuration:"),
        (base_url_loglevel, "  {}".format(base_url_line)),
        (proxy_url_loglevel, "  {}".format(proxy_url_line)),
        (logging.INFO, ""),
        (logging.ERROR, "ERROR. Invalid URL configuration:"),
    ]

    for url_errors, url_message in [
        (base_url_errors, 'Check "base_url" in {}'),
        (proxy_url_errors, 'Check "proxy" in {} and "https_proxy" environment value'),
    ]:
        messages += [(logging.ERROR, "  {}.".format(error)) for error in url_errors]
        messages += [
            (
                logging.ERROR,
                "  {}.".format(url_message.format(insights_connection.config.conf)),
            )
        ]

    messages += [(logging.ERROR, "")]

    record_tuples = [
        ("insights.client.connection", loglevel, message)
        for loglevel, message in messages
    ]
    assert caplog.record_tuples == auth_record_tuples + record_tuples


@pytest.mark.parametrize(
    ["base_url", "proxy_url", "expected_rc"],
    [
        ("https://www.example.com/", None, 0),
        ("https://insights:insights:insights/", None, 1),
        ("https:///", None, 1),
        ("insights", None, 1),
        ("https://www.example.com/", "http://localhost", 0),
        ("https://insights:insights:insights/", "http://localhost", 1),
        ("https:///", "http://localhost", 1),
        ("insights", "http://localhost", 1),
        ("https://www.example.com/", "http://insights:insights:localhost", 1),
        ("https://www.example.com/", "http:///", 1),
        ("https://www.example.com/", "localhost", 1),
        (
            "https://insights:insights:insights/",
            "http://insights:insights:localhost",
            1,
        ),
        ("https:///", "http:///", 1),
        ("insights", "localhost", 1),
    ],
)
def test_test_connection_url_invalid_return_value(
    base_url, proxy_url, expected_rc, insights_connection
):
    """An exit code 1 (error) is returned if the Base or the Proxy URL is invalid or incomplete."""
    insights_connection.base_url = base_url
    insights_connection.proxies = {"https": proxy_url} if proxy_url else None
    _valid_auth_config(insights_connection)
    insights_connection.session.request.return_value = _response(
        status_code=requests.codes.ok
    )

    actual_rc = insights_connection.test_connection()
    assert actual_rc == expected_rc


@pytest.mark.parametrize(
    [
        "legacy_upload",
        "config_upload_url",
        "full_upload_url",
        "full_inventory_url",
        "full_ping_url",
    ],
    [
        (
            True,
            None,
            "https://www.example.com/uploads",
            "https://www.example.com/platform/inventory/v1",
            "https://www.example.com/",
        ),
        (
            False,
            None,
            "https://www.example.com/ingress/v1/upload",
            "https://www.example.com/inventory/v1",
            "https://www.example.com/apicast-tests/ping",
        ),
        (
            True,
            "https://insights.example.com/uploads",
            "https://insights.example.com/uploads",
            "https://www.example.com/platform/inventory/v1",
            "https://www.example.com/",
        ),
        (
            False,
            "https://insights.example.com/uploads",
            "https://insights.example.com/uploads",
            "https://www.example.com/inventory/v1",
            "https://www.example.com/apicast-tests/ping",
        ),
    ],
)
def test_test_connection_urls_legacy_log(
    legacy_upload,
    config_upload_url,
    full_upload_url,
    full_inventory_url,
    full_ping_url,
    caplog,
):
    """Upload, Inventory and Ping URLs are determined differently for (non-)legacy. The Upload URL can be overridden."""
    connection = _insights_connection(
        upload_url=config_upload_url, legacy_upload=legacy_upload
    )
    connection.session.request.return_value = _response(status_code=requests.codes.ok)

    auth_record_tuples = _valid_auth_config(connection)
    url_record_tuples = _url_config(connection)

    with caplog.at_level(logging.INFO):
        connection.test_connection()

    messages = [
        "Running Connection Tests against Satellite...",
        "  Upload URL: {}".format(full_upload_url),
        "  Inventory URL: {}".format(full_inventory_url),
        "  Ping URL: {}".format(full_ping_url),
        "",
        "  Uploading a file to Ingress...",
        "    Testing {}".format(full_upload_url),
        "    SUCCESS.",
        "",
        "  Getting hosts from Inventory...",
        "    Testing {}/hosts".format(full_inventory_url),
        "    SUCCESS.",
        "",
        "  Pinging the API...",
        "    Testing {}".format(full_ping_url),
        "    SUCCESS.",
        "",
        "    See {} or use --verbose for more details.".format(LOGGING_FILE),
        "",
    ]
    record_tuples = [
        ("insights.client.connection", logging.INFO, message) for message in messages
    ]
    assert (
        caplog.record_tuples == auth_record_tuples + url_record_tuples + record_tuples
    )


@pytest.mark.parametrize(
    ["verbose", "hostname", "description"],
    [
        (False, "cert-api.access.redhat.com", "Red Hat Insights"),
        (False, "cert.cloud.stage.redhat.com", "Red Hat Insights (staging)"),
        (False, "localhost", "Satellite"),
        (True, "cert-api.access.redhat.com", "Red Hat Insights (production)"),
        (True, "cert.cloud.stage.redhat.com", "Red Hat Insights (staging)"),
        (True, "localhost", "Satellite"),
    ],
)
def test_test_connection_hostname_description_log(
    verbose, hostname, description, insights_connection, caplog
):
    """Production, Staging and Satellite environments are recognized by the hostname."""
    insights_connection.config.verbose = verbose

    insights_connection.base_url = "https://{}/r/insights/platform/".format(hostname)
    insights_connection.upload_url = insights_connection.base_url + "ingress/v1/upload"
    insights_connection.inventory_url = insights_connection.base_url + "inventory/v1"
    insights_connection.ping_url = insights_connection.base_url + "apicast-tests/ping"

    insights_connection.session.request.return_value = _response(
        status_code=requests.codes.ok
    )

    auth_record_tuples = _valid_auth_config(insights_connection)
    url_record_tuples = _url_config(insights_connection)

    with caplog.at_level(logging.INFO):
        insights_connection.test_connection()

    messages = [
        "Running Connection Tests against {}...".format(description),
        "  Upload URL: {}".format(insights_connection.upload_url),
        "  Inventory URL: {}".format(insights_connection.inventory_url),
        "  Ping URL: {}".format(insights_connection.ping_url),
        "",
        "  Uploading a file to Ingress...",
        "    Testing {}".format(insights_connection.upload_url),
        "    SUCCESS.",
        "",
        "  Getting hosts from Inventory...",
        "    Testing {}/hosts".format(insights_connection.inventory_url),
        "    SUCCESS.",
        "",
        "  Pinging the API...",
        "    Testing {}".format(insights_connection.ping_url),
        "    SUCCESS.",
        "",
        "    See {} or use --verbose for more details.".format(LOGGING_FILE),
        "",
    ]
    record_tuples = [
        ("insights.client.connection", logging.INFO, message) for message in messages
    ]
    assert (
        caplog.record_tuples == auth_record_tuples + url_record_tuples + record_tuples
    )


@pytest.mark.parametrize(
    ["status_code"],
    [
        (requests.codes.ok,),
        (requests.codes.created,),
        (requests.codes.accepted,),
    ],
)
@parametrize_legacy_upload
def test_test_connection_success_status_code_log(legacy_upload, status_code, caplog):
    """All URLs are tested on any success HTTP status code."""
    connection = _insights_connection(legacy_upload=legacy_upload)
    connection.session.request.return_value = _response(status_code=status_code)

    auth_record_tuples = _valid_auth_config(connection)
    url_record_tuples = _url_config(connection)

    with caplog.at_level(logging.INFO):
        connection.test_connection()

    messages = [
        "Running Connection Tests against Satellite...",
        "  Upload URL: {}".format(connection.upload_url),
        "  Inventory URL: {}".format(connection.inventory_url),
        "  Ping URL: {}".format(connection.ping_url),
        "",
        "  Uploading a file to Ingress...",
        "    Testing {}".format(connection.upload_url),
        "    SUCCESS.",
        "",
        "  Getting hosts from Inventory...",
        "    Testing {}/hosts".format(connection.inventory_url),
        "    SUCCESS.",
        "",
        "  Pinging the API...",
        "    Testing {}".format(connection.ping_url),
        "    SUCCESS.",
        "",
        "    See {} or use --verbose for more details.".format(LOGGING_FILE),
        "",
    ]
    record_tuples = [
        ("insights.client.connection", logging.INFO, message) for message in messages
    ]
    assert (
        caplog.record_tuples == auth_record_tuples + url_record_tuples + record_tuples
    )


@pytest.mark.parametrize(
    ["status_code"],
    [
        (requests.codes.ok,),
        (requests.codes.created,),
        (requests.codes.accepted,),
    ],
)
@parametrize_legacy_upload
def test_test_connection_success_status_code_return_value(legacy_upload, status_code):
    """An exit code 1 (error) is returned on success."""
    connection = _insights_connection(legacy_upload=legacy_upload)
    _valid_auth_config(connection)
    connection.session.request.return_value = _response(status_code=status_code)

    rc = connection.test_connection()
    assert rc == 0


@parametrize_legacy_upload
def test_test_connection_result_unknown_log(legacy_upload, caplog):
    """An unexpected return value from _test_url is properly handled."""
    connection = _insights_connection(legacy_upload=legacy_upload)

    auth_record_tuples = _valid_auth_config(connection)
    url_record_tuples = _url_config(connection)

    with caplog.at_level(logging.INFO):
        connection.test_connection()

    messages = [
        (logging.INFO, "Running Connection Tests against Satellite..."),
        (logging.INFO, "  Upload URL: {}".format(connection.upload_url)),
        (logging.INFO, "  Inventory URL: {}".format(connection.inventory_url)),
        (logging.INFO, "  Ping URL: {}".format(connection.ping_url)),
        (logging.INFO, ""),
        (logging.INFO, "  Uploading a file to Ingress..."),
        (logging.INFO, "    Testing {}".format(connection.upload_url)),
        (logging.ERROR, "    FAILED."),
        (logging.ERROR, ""),
        (
            logging.ERROR,
            "    Error in Insights Client: unknown result {}. Contact Red Hat support.".format(
                connection.session.request.return_value
            ),
        ),
        (
            logging.ERROR,
            "    Additional details of network communication are in {}.".format(
                LOGGING_FILE
            ),
        ),
        (logging.ERROR, ""),
    ]
    record_tuples = [
        ("insights.client.connection", loglevel, message)
        for loglevel, message in messages
    ]
    assert (
        caplog.record_tuples == auth_record_tuples + url_record_tuples + record_tuples
    )


@parametrize_legacy_upload
def test_test_connection_result_unknown_return_value(legacy_upload):
    """An exit code 1 (error) is returned in case of an unexpected return value from _test_url."""
    connection = _insights_connection(legacy_upload=legacy_upload)
    _valid_auth_config(connection)

    rc = connection.test_connection()
    assert rc == 1


@pytest.mark.parametrize(
    ["proxies", "status_code", "content_type", "content", "error_message"],
    [
        (
            None,
            requests.codes.im_a_teapot,
            "text/plain",
            "",
            "Unknown response 418 Reason. Check status of Red Hat services at https://status.redhat.com/ or contact Red Hat support",
        ),
        (
            {"https": "http://localhost"},
            requests.codes.im_a_teapot,
            "text/plain",
            "",
            "Unknown response 418 Reason. Check your proxy server, status of Red Hat services at https://status.redhat.com/, or contact Red Hat support",
        ),
        (
            None,
            requests.codes.too_many_requests,
            "text/plain",
            "",
            "Too many requests. Wait a few minutes and try again",
        ),
        (
            None,
            requests.codes.unauthorized,
            "text/plain",
            "",
            "Unknown response 401 Reason. Check status of Red Hat services at https://status.redhat.com/ or contact Red Hat support",
        ),
        (
            None,
            requests.codes.unauthorized,
            "application/json",
            "[]",
            "Unknown response 401 Reason. Check status of Red Hat services at https://status.redhat.com/ or contact Red Hat support",
        ),
        (
            None,
            requests.codes.unauthorized,
            "application/json",
            "{}",
            "Unknown response 401 Reason. Check status of Red Hat services at https://status.redhat.com/ or contact Red Hat support",
        ),
        (
            None,
            requests.codes.unauthorized,
            "application/json",
            '{"errors": {}}',
            "Unknown response 401 Reason. Check status of Red Hat services at https://status.redhat.com/ or contact Red Hat support",
        ),
        (
            None,
            requests.codes.unauthorized,
            "application/json",
            '{"errors": []}',
            "Unknown response 401 Reason. Check status of Red Hat services at https://status.redhat.com/ or contact Red Hat support",
        ),
        (
            None,
            requests.codes.unauthorized,
            "application/json",
            '{"errors": [1]}',
            "Unknown response 401 Reason. Check status of Red Hat services at https://status.redhat.com/ or contact Red Hat support",
        ),
        (
            None,
            requests.codes.unauthorized,
            "application/json",
            '{"errors": [{}]}',
            "Unknown response 401 Reason. Check status of Red Hat services at https://status.redhat.com/ or contact Red Hat support",
        ),
        (
            None,
            requests.codes.unauthorized,
            "application/json",
            '{"errors": [{"status": 401}]}',
            "Unknown response 401 Reason. Check status of Red Hat services at https://status.redhat.com/ or contact Red Hat support",
        ),
        (
            None,
            requests.codes.unauthorized,
            "application/json",
            '{"errors": [{"status": 401, "meta": 1}]}',
            "Unknown response 401 Reason. Check status of Red Hat services at https://status.redhat.com/ or contact Red Hat support",
        ),
        (
            None,
            requests.codes.unauthorized,
            "application/json",
            '{"errors": [{"status": 401, "meta": []}]}',
            "Unknown response 401 Reason. Check status of Red Hat services at https://status.redhat.com/ or contact Red Hat support",
        ),
        (
            None,
            requests.codes.unauthorized,
            "application/json",
            '{"errors": [{"status": 401, "meta": {}}]}',
            "Unknown response 401 Reason. Check status of Red Hat services at https://status.redhat.com/ or contact Red Hat support",
        ),
        (
            None,
            requests.codes.unauthorized,
            "application/json",
            '{"errors": [{"status": 401, "meta": {"response_by": 1}}]}',
            "Unknown response 401 Reason. Check status of Red Hat services at https://status.redhat.com/ or contact Red Hat support",
        ),
        (
            None,
            requests.codes.unauthorized,
            "application/json",
            '{"errors": ["meta": {"response_by": "gateway"}}]}',
            "Unknown response 401 Reason. Check status of Red Hat services at https://status.redhat.com/ or contact Red Hat support",
        ),
        (
            None,
            requests.codes.unauthorized,
            "application/json",
            '{"errors": [{"status": 403, "meta": {"response_by": "gateway"}}]}',
            "Unknown response 401 Reason. Check status of Red Hat services at https://status.redhat.com/ or contact Red Hat support",
        ),
        (
            None,
            requests.codes.unauthorized,
            "application/json",
            '{"errors": [{"status": 401, "meta": {"response_by": "gateway"}}]}',
            'Authentication failed. Check your "username" and "password" in {}'.format(
                InsightsConstants.default_conf_file
            ),
        ),
    ],
)
@parametrize_legacy_upload
def test_test_connection_error_response_log(
    legacy_upload,
    proxies,
    status_code,
    content_type,
    content,
    error_message,
    caplog,
):
    """A non-success response is properly handled. Rate limit is recognized by a status code, bad credentials by
    a combination of a status code and expected values in the returned JSON object."""
    connection = _insights_connection(legacy_upload=legacy_upload)
    connection.proxies = proxies
    connection.session.request.return_value = _response(
        status_code=status_code,
        reason="Reason",
        headers={"Content-Type": content_type},
        _content=content.encode("utf-8"),
    )

    auth_record_tuples = _valid_auth_config(connection)
    url_record_tuples = _url_config(connection)

    with caplog.at_level(logging.INFO):
        connection.test_connection()

    messages = [
        (logging.INFO, "Running Connection Tests against Satellite..."),
        (logging.INFO, "  Upload URL: {}".format(connection.upload_url)),
        (logging.INFO, "  Inventory URL: {}".format(connection.inventory_url)),
        (logging.INFO, "  Ping URL: {}".format(connection.ping_url)),
        (logging.INFO, ""),
        (logging.INFO, "  Uploading a file to Ingress..."),
        (logging.INFO, "    Testing {}".format(connection.upload_url)),
        (logging.ERROR, "    FAILED."),
        (logging.ERROR, ""),
        (logging.ERROR, "    {}.".format(error_message)),
        (
            logging.ERROR,
            "    Additional details of network communication are in {}.".format(
                LOGGING_FILE
            ),
        ),
        (logging.ERROR, ""),
    ]
    record_tuples = [
        ("insights.client.connection", loglevel, message)
        for loglevel, message in messages
    ]
    assert (
        caplog.record_tuples == auth_record_tuples + url_record_tuples + record_tuples
    )


@pytest.mark.parametrize(
    ["status_code", "content_type", "content"],
    [
        (requests.codes.im_a_teapot, "text/plain", ""),
        (requests.codes.too_many_requests, "text/plain", ""),
        (requests.codes.unauthorized, "text/plain", ""),
        (
            requests.codes.unauthorized,
            "application/json",
            "[]",
        ),
        (
            requests.codes.unauthorized,
            "application/json",
            "{}",
        ),
        (
            requests.codes.unauthorized,
            "application/json",
            '{"errors": {}}',
        ),
        (
            requests.codes.unauthorized,
            "application/json",
            '{"errors": []}',
        ),
        (
            requests.codes.unauthorized,
            "application/json",
            '{"errors": [1]}',
        ),
        (
            requests.codes.unauthorized,
            "application/json",
            '{"errors": [{}]}',
        ),
        (
            requests.codes.unauthorized,
            "application/json",
            '{"errors": [{"status": 401}]}',
        ),
        (
            requests.codes.unauthorized,
            "application/json",
            '{"errors": [{"status": 401, "meta": 1}]}',
        ),
        (
            requests.codes.unauthorized,
            "application/json",
            '{"errors": [{"status": 401, "meta": []}]}',
        ),
        (
            requests.codes.unauthorized,
            "application/json",
            '{"errors": [{"status": 401, "meta": {}}]}',
        ),
        (
            requests.codes.unauthorized,
            "application/json",
            '{"errors": [{"status": 401, "meta": {"response_by": 1}}]}',
        ),
        (
            requests.codes.unauthorized,
            "application/json",
            '{"errors": ["meta": {"response_by": "gateway"}}]}',
        ),
        (
            requests.codes.unauthorized,
            "application/json",
            '{"errors": [{"status": 403, "meta": {"response_by": "gateway"}}]}',
        ),
        (
            requests.codes.unauthorized,
            "application/json",
            '{"errors": [{"status": 401, "meta": {"response_by": "gateway"}}]}',
        ),
    ],
)
@parametrize_legacy_upload
def test_test_connection_error_response_return_value(
    legacy_upload,
    status_code,
    content_type,
    content,
):
    """An exit code 1 (error) is return in case of an error response. Rate limit is recognized by a status code, bad
    credentials by a combination of a status code and expected values in the returned JSON object.
    """
    connection = _insights_connection(legacy_upload=legacy_upload)
    _valid_auth_config(connection)
    connection.session.request.return_value = _response(
        status_code=status_code,
        reason="Reason",
        headers={"Content-Type": content_type},
        _content=content.encode("utf-8"),
    )

    rc = connection.test_connection()
    assert rc == 1


@pytest.mark.parametrize(
    ["proxies", "error"],
    [
        (None, "Unknown error unknown error. Contact Red Hat support"),
        (
            {"https": "http://localhost"},
            "Unknown error unknown error. Check your proxy or contact Red Hat support",
        ),
    ],
)
@pytest.mark.parametrize(
    ["legacy_upload", "messages"],
    [
        (
            False,
            [
                (logging.INFO, "    Testing https://www.example.com/ingress/v1/upload"),
                (logging.ERROR, "    FAILED."),
            ],
        ),
        (
            True,
            [
                (logging.INFO, "    Testing https://www.example.com/uploads"),
                (logging.ERROR, "      Failed."),
                (logging.INFO, "    Testing https://www.example.com"),
                (logging.ERROR, "      Failed."),
                (logging.INFO, "    Testing https://www.example.com/r"),
                (logging.ERROR, "      Failed."),
                (logging.INFO, "    Testing https://www.example.com/r/insights"),
                (logging.ERROR, "      Failed."),
                (logging.ERROR, "    FAILED."),
            ],
        ),
    ],
)
def test_test_connection_exception_unknown_log(
    legacy_upload, messages, proxies, error, caplog
):
    """An unknown error is properly handled. Legacy upload tries several URLs in case of a failure."""
    connection = _insights_connection(legacy_upload=legacy_upload, upload_url=None)
    connection.session.request.side_effect = RuntimeError("unknown error")
    connection.proxies = proxies

    auth_record_tuples = _valid_auth_config(connection)
    url_record_tuples = _url_config(connection)

    with caplog.at_level(logging.INFO):
        with patch(
            "insights.client.connection.REQUEST_FAILED_EXCEPTIONS", (RuntimeError,)
        ):
            connection.test_connection()

    pre_messages = [
        (logging.INFO, "Running Connection Tests against Satellite..."),
        (logging.INFO, "  Upload URL: {}".format(connection.upload_url)),
        (logging.INFO, "  Inventory URL: {}".format(connection.inventory_url)),
        (logging.INFO, "  Ping URL: {}".format(connection.ping_url)),
        (logging.INFO, ""),
        (logging.INFO, "  Uploading a file to Ingress..."),
    ]
    post_messages = [
        (logging.ERROR, ""),
        (
            logging.ERROR,
            "    {}.".format(error),
        ),
        (
            logging.ERROR,
            "    Additional details of network communication are in {}.".format(
                LOGGING_FILE
            ),
        ),
        (logging.ERROR, ""),
    ]

    record_tuples = [
        ("insights.client.connection", loglevel, message)
        for loglevel, message in pre_messages + messages + post_messages
    ]
    assert (
        caplog.record_tuples == auth_record_tuples + url_record_tuples + record_tuples
    )


@parametrize_legacy_upload
def test_test_connection_exception_unknown_return_value(legacy_upload):
    """An exit code 1 (error) is returned in case of an unknown error."""
    connection = _insights_connection(legacy_upload=legacy_upload)
    connection.session.request.side_effect = RuntimeError("unknown error")

    with patch("insights.client.connection.REQUEST_FAILED_EXCEPTIONS", (RuntimeError,)):
        rc = connection.test_connection()

    assert rc == 1


@pytest.mark.parametrize(
    ["proxies", "exception_type", "exception_context", "message"],
    [
        (
            None,
            requests.exceptions.ConnectionError,
            None,
            "Connection error error. Check your network and status of Red Hat services or contact Red Hat Support",
        ),
        (
            {"https": "http://localhost:3128"},
            requests.exceptions.ConnectionError,
            None,
            "Connection error error. Check your network, proxy, and status of Red Hat services or contact Red Hat Support",
        ),
        (
            None,
            requests.exceptions.ConnectionError,
            OSError("[Errno 101] Network is unreachable"),
            "Connection error error. Check your network and status of Red Hat services or contact Red Hat Support",
        ),
        (
            {"https": "http://localhost:3128"},
            requests.exceptions.ConnectionError,
            OSError("[Errno 101] Network is unreachable"),
            "Connection error error. Check your network, proxy, and status of Red Hat services or contact Red Hat Support",
        ),
        (
            None,
            requests.exceptions.ConnectionError,
            ConnectionAbortedError(54, "Connection reset by peer"),
            "Connection error error. Check your network and status of Red Hat services or contact Red Hat Support",
        ),
        (
            {"https": "http://localhost:3128"},
            requests.exceptions.ConnectionError,
            ConnectionAbortedError(54, "Connection reset by peer"),
            "Connection error error. Check your network, proxy, and status of Red Hat services or contact Red Hat Support",
        ),
        (
            None,
            requests.exceptions.ConnectionError,
            ConnectionRefusedError(111, "Connection refused"),
            "Connection refused. Check your network and status of Red Hat services or contact Red Hat Support",
        ),
        (
            {"https": "http://localhost:3128"},
            requests.exceptions.ConnectionError,
            ConnectionRefusedError(111, "Connection refused"),
            "Connection refused. Check your network, proxy, and status of Red Hat services or contact Red Hat Support",
        ),
        (
            None,
            requests.exceptions.ConnectionError,
            ConnectionResetError(104, "Connection reset by peer"),
            "Connection refused. Check your network and status of Red Hat services or contact Red Hat Support",
        ),
        (
            {"https": "http://localhost:3128"},
            requests.exceptions.ConnectionError,
            ConnectionResetError(104, "Connection reset by peer"),
            "Connection refused. Check your network, proxy, and status of Red Hat services or contact Red Hat Support",
        ),
        (
            None,
            requests.exceptions.SSLError,
            ssl.SSLError(336265225, "[SSL] PEM lib (_ssl.c:2959)"),
            'SSL error. Check your network or re-register the system by running "subscription-manager unregister" and then "subscription-manager register"',
        ),
        (
            {"https": "http://localhost:3128"},
            requests.exceptions.SSLError,
            ssl.SSLError(336265225, "[SSL] PEM lib (_ssl.c:2959)"),
            'SSL error. Check your network and proxy or re-register the system by running "subscription-manager unregister" and then "subscription-manager register"',
        ),
        (
            None,
            requests.exceptions.SSLError,
            ssl.SSLError(
                1,
                "[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1129)",
            ),
            "Invalid SSL key or certificate. Check your network and proxy or re-register the system by"
            ' running "subscription-manager unregister" and then "subscription-manager register"',
        ),
        (
            {"https": "http://localhost:3128"},
            requests.exceptions.SSLError,
            ssl.SSLError(
                1,
                "[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1129)",
            ),
            "Invalid SSL key or certificate. Check your network and proxy or re-register the "
            'system by running "subscription-manager unregister" and then "subscription-manager '
            'register"',
        ),
        (
            {"https": "https://localhost:3128"},
            requests.exceptions.SSLError,
            ssl.SSLError(
                1,
                "[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1129)",
            ),
            "Invalid SSL key or certificate. Check your proxy configuration. Alternatively, "
            're-register the system by running "subscription-manager unregister" and then '
            '"subscription-manager register"',
        ),
        (
            None,
            requests.exceptions.SSLError,
            ssl.SSLError(
                1, "[SSL: WRONG_VERSION_NUMBER] wrong version number (_ssl.c:1129)"
            ),
            'Invalid protocol. Check that "base_url" in {} points to an HTTPS (not HTTP) '
            "endpoint".format(InsightsConstants.default_conf_file),
        ),
        (
            {"https": "gopher://localhost:3128"},
            requests.exceptions.SSLError,
            ssl.SSLError(
                1, "[SSL: WRONG_VERSION_NUMBER] wrong version number (_ssl.c:1129)"
            ),
            'Invalid protocol. Check that "proxy" in {} or "https_proxy" environment value points to the correct port of the proxy. Alternatively, check whether "base_url" points to an HTTPS (not HTTP) endpoint'.format(
                InsightsConstants.default_conf_file
            ),
        ),
        (
            {"https": "https://localhost:3128"},
            requests.exceptions.SSLError,
            ssl.SSLError(
                1, "[SSL: WRONG_VERSION_NUMBER] wrong version number (_ssl.c:1129)"
            ),
            'Invalid protocol. Check that "proxy" in {} or "https_proxy" environment value points to an HTTPS (not HTTP) port of the proxy. Alternatively, check whether "base_url" points to an HTTPS (not HTTP) endpoint'.format(
                InsightsConstants.default_conf_file
            ),
        ),
        (
            {"https": "http://localhost:3128"},
            requests.exceptions.SSLError,
            ssl.SSLError(
                1, "[SSL: WRONG_VERSION_NUMBER] wrong version number (_ssl.c:1129)"
            ),
            'Invalid protocol. Check that "proxy" in {} or "https_proxy" environment value points to an HTTP (not HTTPS) port of the proxy. Alternatively, check whether "base_url" points to an HTTPS (not HTTP) endpoint'.format(
                InsightsConstants.default_conf_file
            ),
        ),
        (
            {"https": "http://localhost:3128"},
            requests.exceptions.ProxyError,
            ConnectionAbortedError(54, "Connection reset by peer"),
            "HTTPS proxy http://localhost:3128 error error. Check your proxy configuration or restart its service",
        ),
        (
            {"https": "http://localhost:3128"},
            requests.exceptions.ProxyError,
            ConnectionRefusedError(111, "Connection refused"),
            "Connection to HTTPS proxy http://localhost:3128 refused. Check your proxy configuration or restart its service",
        ),
        (
            {"https": "http://localhost:3128"},
            requests.exceptions.ProxyError,
            ConnectionResetError(104, "Connection reset by peer"),
            "Connection to HTTPS proxy http://localhost:3128 refused. Check your proxy configuration or restart its service",
        ),
        (
            {"https": "http://localhost:3128"},
            requests.exceptions.ProxyError,
            None,
            "HTTPS proxy http://localhost:3128 error error. Check your proxy configuration or restart its service",
        ),
        (
            {"https": "http://localhost:3128"},
            requests.exceptions.ProxyError,
            OSError("Tunnel connection failed: 500 Internal Server Error"),
            "HTTPS proxy http://localhost:3128 error error. Check your proxy configuration or restart its service",
        ),
        (
            {"https": "http://localhost:3128"},
            requests.exceptions.ProxyError,
            OSError("Tunnel connection failed: 407 Proxy Authentication Required"),
            'Invalid HTTPS proxy credentials http://localhost:3128. Check "proxy" username and password in {} or "https_proxy" environment variable'.format(
                InsightsConstants.default_conf_file
            ),
        ),
    ],
)
@pytest.mark.insights_config(legacy_upload=False, upload_url=None)
def test_test_connection_exception_connection_error_log(
    proxies, exception_type, exception_context, message, insights_connection, caplog
):
    """Exceptions are properly handled by type, unknown exceptions are partially recognized too."""
    insights_connection.proxies = proxies
    insights_connection.session.request.side_effect = _exception(
        exception_type("error"), exception_context
    )

    auth_record_tuples = _valid_auth_config(insights_connection)
    url_record_tuples = _url_config(insights_connection)

    with caplog.at_level(logging.INFO):
        insights_connection.test_connection()

    messages = [
        (logging.INFO, "Running Connection Tests against Satellite..."),
        (logging.INFO, "  Upload URL: {}".format(insights_connection.upload_url)),
        (logging.INFO, "  Inventory URL: {}".format(insights_connection.inventory_url)),
        (logging.INFO, "  Ping URL: {}".format(insights_connection.ping_url)),
        (logging.INFO, ""),
        (logging.INFO, "  Uploading a file to Ingress..."),
        (logging.INFO, "    Testing https://www.example.com/ingress/v1/upload"),
        (logging.ERROR, "    FAILED."),
        (logging.ERROR, ""),
        (logging.ERROR, "    {}.".format(message)),
        (
            logging.ERROR,
            "    Additional details of network communication are in {}.".format(
                LOGGING_FILE
            ),
        ),
        (logging.ERROR, ""),
    ]

    record_tuples = [
        ("insights.client.connection", loglevel, message)
        for loglevel, message in messages
    ]
    assert (
        caplog.record_tuples == auth_record_tuples + url_record_tuples + record_tuples
    )


@pytest.mark.parametrize(
    ["base_url_hostname", "description", "red_hat_fallback_ip"],
    [
        ("cert-api.access.redhat.com", "Red Hat Insights", "23.37.45.238"),
        (
            "cert-api.access.stage.redhat.com",
            "Red Hat Insights (staging)",
            "23.53.5.13",
        ),
        ("www.example.com", "Satellite", None),
    ],
)
@pytest.mark.parametrize(
    ["exception_type", "exception_context", "message", "test_red_hat"],
    [
        (
            requests.exceptions.ConnectionError,
            socket.gaierror("[Errno -2] Name or service not known"),
            "Could not resolve base URL host {0}",
            True,
        ),
        (
            requests.exceptions.ConnectTimeout,
            socket.timeout("timed out"),
            "Connection timed out",
            True,
        ),
        (
            requests.exceptions.ReadTimeout,
            socket.timeout("timed out"),
            "Read timed out",
            True,
        ),
        (
                requests.exceptions.Timeout,
                socket.timeout("timed out"),
                "Timeout error",
                True,
        ),
        (
            requests.exceptions.ProxyError,
            socket.gaierror("[Errno -2] Name or service not known"),
            "Could not resolve HTTPS proxy URL host {1}",
            False,
        ),
    ],
)
def test_test_connection_test_connection_fail_log(
    exception_type,
    exception_context,
    message,
    test_red_hat,
    base_url_hostname,
    description,
    red_hat_fallback_ip,
    caplog,
):
    """Name resolution and timeout errors are properly recognized and handled by a network connection test. A correct
    fallback IP is picked based on the base URL hostname."""
    connection = _insights_connection(
        base_url=base_url_hostname, legacy_upload=False, upload_url=None
    )
    proxy_url_hostname = "localhost"
    connection.proxies = {"https": "http://{}:3128".format(proxy_url_hostname)}
    connection.session.request.side_effect = _exception(
        exception_type("error"), exception_context
    )

    auth_record_tuples = _valid_auth_config(connection)
    url_record_tuples = _url_config(connection)

    with caplog.at_level(logging.INFO):
        connection.test_connection()

    messages = [
        (logging.INFO, "Running Connection Tests against {}...".format(description)),
        (logging.INFO, "  Upload URL: {}".format(connection.upload_url)),
        (logging.INFO, "  Inventory URL: {}".format(connection.inventory_url)),
        (logging.INFO, "  Ping URL: {}".format(connection.ping_url)),
        (logging.INFO, ""),
        (logging.INFO, "  Uploading a file to Ingress..."),
        (
            logging.INFO,
            "    Testing https://{}/ingress/v1/upload".format(base_url_hostname),
        ),
        (logging.ERROR, "    FAILED."),
        (logging.ERROR, ""),
        (
            logging.ERROR,
            "    {}.".format(message.format(base_url_hostname, proxy_url_hostname)),
        ),
        (logging.ERROR, ""),
        (logging.INFO, "  Verifying network connection..."),
    ]
    if test_red_hat and red_hat_fallback_ip:
        messages += [
            (logging.INFO, "    Testing https://{}/".format(red_hat_fallback_ip)),
            (logging.ERROR, "      Failed."),
        ]
    messages += [
        (logging.INFO, "    Testing https://one.one.one.one/"),
        (logging.ERROR, "      Failed."),
        (logging.INFO, "    Testing https://1.1.1.1/"),
        (logging.ERROR, "      Failed."),
        (logging.ERROR, "    FAILED."),
        (
            logging.ERROR,
            "    Additional details of network communication are in {}.".format(
                LOGGING_FILE
            ),
        ),
        (logging.ERROR, ""),
    ]

    record_tuples = [
        ("insights.client.connection", loglevel, message)
        for loglevel, message in messages
    ]
    assert (
        caplog.record_tuples == auth_record_tuples + url_record_tuples + record_tuples
    )


@pytest.mark.parametrize(
    ["exception_type", "exception_context"],
    [
        (requests.exceptions.ConnectionError, None),
        (
            requests.exceptions.ConnectionError,
            OSError("[Errno 101] Network is unreachable"),
        ),
        (
            requests.exceptions.ConnectionError,
            ConnectionAbortedError(54, "Connection reset by peer"),
        ),
        (
            requests.exceptions.ConnectionError,
            ConnectionRefusedError(111, "Connection refused"),
        ),
        (
            requests.exceptions.ConnectionError,
            ConnectionResetError(104, "Connection reset by peer"),
        ),
        (
            requests.exceptions.SSLError,
            ssl.SSLError(
                1,
                "[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1129)",
            ),
        ),
        (
            requests.exceptions.SSLError,
            ssl.SSLError(
                1, "[SSL: WRONG_VERSION_NUMBER] wrong version number (_ssl.c:1129)"
            ),
        ),
        (
            requests.exceptions.SSLError,
            ssl.SSLError(336265225, "[SSL] PEM lib (_ssl.c:2959)"),
        ),
        (
            requests.exceptions.ProxyError,
            None,
        ),
        (
            requests.exceptions.ProxyError,
            ConnectionAbortedError(54, "Connection reset by peer"),
        ),
        (
            requests.exceptions.ProxyError,
            ConnectionRefusedError(111, "Connection refused"),
        ),
        (
            requests.exceptions.ProxyError,
            ConnectionResetError(104, "Connection reset by peer"),
        ),
        (
            requests.exceptions.ProxyError,
            OSError("Tunnel connection failed: 500 Internal Server Error"),
        ),
        (
            requests.exceptions.ProxyError,
            OSError("Tunnel connection failed: 407 Proxy Authentication Required"),
        ),
        (
            requests.exceptions.ConnectionError,
            socket.gaierror("[Errno -2] Name or service not known"),
        ),
        (
            requests.exceptions.ConnectTimeout,
            socket.timeout("timed out"),
        ),
        (
            requests.exceptions.ReadTimeout,
            socket.timeout("timed out"),
        ),
        (requests.exceptions.Timeout, socket.timeout("timed out")),
        (
            requests.exceptions.ProxyError,
            socket.gaierror("[Errno -2] Name or service not known"),
        ),
    ],
)
@mock.patch("insights.client.connection.InsightsConnection._init_session")
def test_test_connection_exception_connection_error_return_value(
    init_session, exception_type, exception_context
):
    """An exit code 1 (error) is returned in case of at least partially known exception."""
    config = InsightsConfig(
        base_url="www.example.com",
        legacy_upload=False,
        logging_file=LOGGING_FILE,
    )
    connection = InsightsConnection(config)
    connection.proxies = {"https": "http://localhost:3128"}
    _valid_auth_config(connection)
    connection.session.request.side_effect = _exception(
        exception_type("error"), exception_context
    )

    rc = connection.test_connection()
    assert rc == 1


@pytest.mark.parametrize(
    ["side_effect", "messages"],
    [
        (
            [
                requests.exceptions.ConnectTimeout,
                requests.exceptions.ConnectTimeout,
                requests.exceptions.ConnectTimeout,
            ],
            [
                (logging.INFO, "    Testing https://23.37.45.238/"),
                (logging.ERROR, "      Failed."),
                (logging.INFO, "    Testing https://one.one.one.one/"),
                (logging.ERROR, "      Failed."),
                (logging.INFO, "    Testing https://1.1.1.1/"),
                (logging.ERROR, "      Failed."),
                (logging.ERROR, "    FAILED."),
            ],
        ),
        (
            [
                requests.exceptions.ConnectTimeout,
                requests.exceptions.ConnectTimeout,
                _response(status_code=200),
            ],
            [
                (logging.INFO, "    Testing https://23.37.45.238/"),
                (logging.ERROR, "      Failed."),
                (logging.INFO, "    Testing https://one.one.one.one/"),
                (logging.ERROR, "      Failed."),
                (logging.INFO, "    Testing https://1.1.1.1/"),
                (logging.INFO, "    SUCCESS."),
            ],
        ),
        (
            [requests.exceptions.ConnectTimeout, requests.Response()],
            [
                (logging.INFO, "    Testing https://23.37.45.238/"),
                (logging.ERROR, "      Failed."),
                (logging.INFO, "    Testing https://one.one.one.one/"),
                (logging.INFO, "    SUCCESS."),
            ],
        ),
        (
            [requests.Response()],
            [
                (logging.INFO, "    Testing https://23.37.45.238/"),
                (logging.INFO, "    SUCCESS."),
            ],
        ),
    ],
)
@pytest.mark.insights_config(
    base_url="cert-api.access.redhat.com", legacy_upload=False, upload_url=None
)
def test_test_connection_test_connection_log(
    side_effect, messages, insights_connection, caplog
):
    """Fallback URLs are tried until first success."""

    insights_connection.session.request.side_effect = [
        requests.exceptions.ConnectTimeout
    ] + side_effect

    auth_record_tuples = _valid_auth_config(insights_connection)
    url_record_tuples = _url_config(insights_connection)

    with caplog.at_level(logging.INFO):
        insights_connection.test_connection()

    pre_messages = [
        (logging.INFO, "Running Connection Tests against Red Hat Insights..."),
        (logging.INFO, "  Upload URL: {}".format(insights_connection.upload_url)),
        (logging.INFO, "  Inventory URL: {}".format(insights_connection.inventory_url)),
        (logging.INFO, "  Ping URL: {}".format(insights_connection.ping_url)),
        (logging.INFO, ""),
        (logging.INFO, "  Uploading a file to Ingress..."),
        (
            logging.INFO,
            "    Testing https://cert-api.access.redhat.com/ingress/v1/upload",
        ),
        (logging.ERROR, "    FAILED."),
        (logging.ERROR, ""),
        (logging.ERROR, "    Connection timed out."),
        (logging.ERROR, ""),
        (logging.INFO, "  Verifying network connection..."),
    ]
    post_messages = [
        (
            logging.ERROR,
            "    Additional details of network communication are in {}.".format(
                LOGGING_FILE
            ),
        ),
        (logging.ERROR, ""),
    ]
    messages = pre_messages + messages + post_messages

    record_tuples = [
        ("insights.client.connection", loglevel, message)
        for loglevel, message in messages
    ]
    assert (
        caplog.record_tuples == auth_record_tuples + url_record_tuples + record_tuples
    )


@pytest.mark.parametrize(
    ["side_effect"],
    [
        (
            [
                requests.exceptions.ConnectTimeout,
                requests.exceptions.ConnectTimeout,
                requests.exceptions.ConnectTimeout,
            ],
        ),
        (
            [
                requests.exceptions.ConnectTimeout,
                requests.exceptions.ConnectTimeout,
                _response(),
            ],
        ),
        ([requests.exceptions.ConnectTimeout, _response()],),
        ([_response()],),
    ],
)
@pytest.mark.insights_config(base_url="cert-api.access.redhat.com", legacy_upload=False)
def test_test_connection_test_connection_return_value(side_effect, insights_connection):
    """Fallback URLs are tried until first success."""

    _valid_auth_config(insights_connection)
    insights_connection.session.request.side_effect = [
        requests.exceptions.ConnectTimeout
    ] + side_effect

    rc = insights_connection.test_connection()
    assert rc == 1


@pytest.mark.parametrize(
    ["side_effect", "messages"],
    [
        (
            [
                requests.exceptions.ConnectionError("error 0"),
                requests.exceptions.ConnectionError("error 1"),
                requests.exceptions.ConnectionError("error 2"),
                requests.exceptions.ConnectionError("error 3"),
            ],
            [
                (logging.ERROR, "      Failed."),
                (
                    logging.INFO,
                    "    Testing https://www.example.com",
                ),
                (logging.ERROR, "      Failed."),
                (
                    logging.INFO,
                    "    Testing https://www.example.com/r",
                ),
                (logging.ERROR, "      Failed."),
                (
                    logging.INFO,
                    "    Testing https://www.example.com/r/insights",
                ),
                (logging.ERROR, "      Failed."),
            ],
        ),
        (
            [
                requests.exceptions.ConnectionError("error 0"),
                requests.exceptions.ConnectionError("error 1"),
                requests.exceptions.ConnectionError("error 2"),
                _response(status_code=requests.codes.ok),
                _response(status_code=requests.codes.ok),
                _response(status_code=requests.codes.ok),
            ],
            [
                (logging.ERROR, "      Failed."),
                (
                    logging.INFO,
                    "    Testing https://www.example.com",
                ),
                (logging.ERROR, "      Failed."),
                (
                    logging.INFO,
                    "    Testing https://www.example.com/r",
                ),
                (logging.ERROR, "      Failed."),
                (
                    logging.INFO,
                    "    Testing https://www.example.com/r/insights",
                ),
                (logging.INFO, "    SUCCESS."),
            ],
        ),
        (
            [
                requests.exceptions.ConnectionError("error 0"),
                requests.exceptions.ConnectionError("error 1"),
                _response(status_code=requests.codes.ok),
                _response(status_code=requests.codes.ok),
                _response(status_code=requests.codes.ok),
            ],
            [
                (logging.ERROR, "      Failed."),
                (
                    logging.INFO,
                    "    Testing https://www.example.com",
                ),
                (logging.ERROR, "      Failed."),
                (
                    logging.INFO,
                    "    Testing https://www.example.com/r",
                ),
                (logging.INFO, "    SUCCESS."),
            ],
        ),
        (
            [
                requests.exceptions.ConnectionError("error 0"),
                _response(status_code=requests.codes.ok),
                _response(status_code=requests.codes.ok),
                _response(status_code=requests.codes.ok),
            ],
            [
                (logging.ERROR, "      Failed."),
                (
                    logging.INFO,
                    "    Testing https://www.example.com",
                ),
                (logging.INFO, "    SUCCESS."),
            ],
        ),
        (
            [
                _response(status_code=requests.codes.ok),
                _response(status_code=requests.codes.ok),
                _response(status_code=requests.codes.ok),
            ],
            [
                (logging.INFO, "    SUCCESS."),
            ],
        ),
    ],
)
@pytest.mark.insights_config(legacy_upload=True)
def test_test_connection_legacy_path_fallback_log(
    side_effect, messages, insights_connection, caplog
):
    """Several paths are tried for legacy upload until first success."""
    insights_connection.session.request.side_effect = side_effect

    auth_record_tuples = _valid_auth_config(insights_connection)
    url_record_tuples = _url_config(insights_connection)

    with caplog.at_level(logging.INFO):
        insights_connection.test_connection()

    pre_messages = [
        (logging.INFO, "Running Connection Tests against Satellite..."),
        (logging.INFO, "  Upload URL: {}".format(insights_connection.upload_url)),
        (logging.INFO, "  Inventory URL: {}".format(insights_connection.inventory_url)),
        (logging.INFO, "  Ping URL: {}".format(insights_connection.ping_url)),
        (logging.INFO, ""),
        (logging.INFO, "  Uploading a file to Ingress..."),
        (
            logging.INFO,
            "    Testing https://www.example.com/insights",
        ),
    ]

    if isinstance(side_effect[-1], requests.Response):
        post_messages = [
            (logging.INFO, ""),
            (logging.INFO, "  Getting hosts from Inventory..."),
            (
                logging.INFO,
                "    Testing https://www.example.com/platform/inventory/v1/hosts",
            ),
            (logging.INFO, "    SUCCESS."),
            (logging.INFO, ""),
            (logging.INFO, "  Pinging the API..."),
            (logging.INFO, "    Testing https://www.example.com/"),
            (logging.INFO, "    SUCCESS."),
            (logging.INFO, ""),
            (
                logging.INFO,
                "    See {} or use --verbose for more details.".format(LOGGING_FILE),
            ),
            (logging.INFO, ""),
        ]
    elif isinstance(side_effect[-1], requests.exceptions.ConnectionError):
        post_messages = [
            (logging.ERROR, "    FAILED."),
            (logging.ERROR, ""),
            (logging.ERROR, "    Connection error {}. Check your network and status of Red Hat services or contact Red Hat Support.".format(side_effect[-1])),
            (
                logging.ERROR,
                "    Additional details of network communication are in {}.".format(
                    LOGGING_FILE
                ),
            ),
            (logging.ERROR, ""),
        ]
    else:
        raise ValueError("Invalid result.")
    messages = pre_messages + messages + post_messages

    record_tuples = [
        ("insights.client.connection", loglevel, message)
        for loglevel, message in messages
    ]
    assert (
        caplog.record_tuples == auth_record_tuples + url_record_tuples + record_tuples
    )


@pytest.mark.parametrize(
    ["side_effect", "expected_rc"],
    [
        (
            [
                requests.exceptions.ConnectionError(),
                requests.exceptions.ConnectionError(),
                requests.exceptions.ConnectionError(),
                requests.exceptions.ConnectionError(),
            ],
            1,
        ),
        (
            [
                requests.exceptions.ConnectionError(),
                requests.exceptions.ConnectionError(),
                requests.exceptions.ConnectionError(),
                _response(status_code=requests.codes.ok),
                _response(status_code=requests.codes.ok),
                _response(status_code=requests.codes.ok),
            ],
            0,
        ),
        (
            [
                requests.exceptions.ConnectionError(),
                requests.exceptions.ConnectionError(),
                _response(status_code=requests.codes.ok),
                _response(status_code=requests.codes.ok),
                _response(status_code=requests.codes.ok),
            ],
            0,
        ),
        (
            [
                requests.exceptions.ConnectionError(),
                _response(status_code=requests.codes.ok),
                _response(status_code=requests.codes.ok),
                _response(status_code=requests.codes.ok),
            ],
            0,
        ),
        (
            [
                _response(status_code=requests.codes.ok),
                _response(status_code=requests.codes.ok),
                _response(status_code=requests.codes.ok),
            ],
            0,
        ),
    ],
)
@pytest.mark.insights_config(legacy_upload=True)
def test_test_connection_legacy_path_fallback_return_value(
    side_effect, expected_rc, insights_connection
):
    """An exit code 1 (error) is only returned if all fallback paths fail. Even a single success results in code 0
    (success)."""
    _valid_auth_config(insights_connection)
    insights_connection.session.request.side_effect = side_effect

    actual_rc = insights_connection.test_connection()
    assert actual_rc == expected_rc


@pytest.mark.parametrize(
    ["side_effect", "messages"],
    [
        (
            [
                _response(status_code=requests.codes.ok),
                _response(status_code=requests.codes.ok),
                _response(status_code=requests.codes.ok),
            ],
            [
                (logging.INFO, "  Uploading a file to Ingress..."),
                (
                    logging.INFO,
                    "    Testing https://www.example.com/insights",
                ),
                (logging.INFO, "    SUCCESS."),
                (logging.INFO, ""),
                (logging.INFO, "  Getting hosts from Inventory..."),
                (
                    logging.INFO,
                    "    Testing https://www.example.com/inventory/v1/hosts",
                ),
                (logging.INFO, "    SUCCESS."),
                (logging.INFO, ""),
                (logging.INFO, "  Pinging the API..."),
                (
                    logging.INFO,
                    "    Testing https://www.example.com/apicast-tests/ping",
                ),
                (logging.INFO, "    SUCCESS."),
                (logging.INFO, ""),
                (
                    logging.INFO,
                    "    See {} or use --verbose for more details.".format(
                        LOGGING_FILE
                    ),
                ),
                (logging.INFO, ""),
            ],
        ),
        (
            [
                _response(status_code=requests.codes.ok),
                _response(status_code=requests.codes.ok),
                requests.exceptions.ConnectionError("error"),
            ],
            [
                (logging.INFO, "  Uploading a file to Ingress..."),
                (
                    logging.INFO,
                    "    Testing https://www.example.com/insights",
                ),
                (logging.INFO, "    SUCCESS."),
                (logging.INFO, ""),
                (logging.INFO, "  Getting hosts from Inventory..."),
                (
                    logging.INFO,
                    "    Testing https://www.example.com/inventory/v1/hosts",
                ),
                (logging.INFO, "    SUCCESS."),
                (logging.INFO, ""),
                (logging.INFO, "  Pinging the API..."),
                (
                    logging.INFO,
                    "    Testing https://www.example.com/apicast-tests/ping",
                ),
                (logging.ERROR, "    FAILED."),
                (logging.ERROR, ""),
                (
                    logging.ERROR,
                    "    Connection error error. Check your network and status of Red Hat services or contact Red Hat Support.",
                ),
                (
                    logging.ERROR,
                    "    Additional details of network communication are in {}.".format(
                        LOGGING_FILE
                    ),
                ),
                (logging.ERROR, ""),
            ],
        ),
        (
            [
                _response(status_code=requests.codes.ok),
                requests.exceptions.ConnectionError("error"),
            ],
            [
                (logging.INFO, "  Uploading a file to Ingress..."),
                (
                    logging.INFO,
                    "    Testing https://www.example.com/insights",
                ),
                (logging.INFO, "    SUCCESS."),
                (logging.INFO, ""),
                (logging.INFO, "  Getting hosts from Inventory..."),
                (
                    logging.INFO,
                    "    Testing https://www.example.com/inventory/v1/hosts",
                ),
                (logging.ERROR, "    FAILED."),
                (logging.ERROR, ""),
                (
                    logging.ERROR,
                    "    Connection error error. Check your network and status of Red Hat services or contact Red Hat Support.",
                ),
                (
                    logging.ERROR,
                    "    Additional details of network communication are in {}.".format(
                        LOGGING_FILE
                    ),
                ),
                (logging.ERROR, ""),
            ],
        ),
        (
            [
                requests.exceptions.ConnectionError("error"),
            ],
            [
                (logging.INFO, "  Uploading a file to Ingress..."),
                (
                    logging.INFO,
                    "    Testing https://www.example.com/insights",
                ),
                (logging.ERROR, "    FAILED."),
                (logging.ERROR, ""),
                (
                    logging.ERROR,
                    "    Connection error error. Check your network and status of Red Hat services or contact Red Hat Support.",
                ),
                (
                    logging.ERROR,
                    "    Additional details of network communication are in {}.".format(
                        LOGGING_FILE
                    ),
                ),
                (logging.ERROR, ""),
            ],
        ),
    ],
)
@pytest.mark.insights_config(legacy_upload=False)
def test_test_connection_urls_until_fail_log(
    side_effect, messages, insights_connection, caplog
):
    """An Upload URL, an Inventory URL and a Ping URL are tested until the first failure."""

    insights_connection.session.request.side_effect = side_effect

    auth_record_tuples = _valid_auth_config(insights_connection)
    url_record_tuples = _url_config(insights_connection)

    with caplog.at_level(logging.INFO):
        insights_connection.test_connection()

    pre_messages = [
        (logging.INFO, "Running Connection Tests against Satellite..."),
        (logging.INFO, "  Upload URL: {}".format(insights_connection.upload_url)),
        (logging.INFO, "  Inventory URL: {}".format(insights_connection.inventory_url)),
        (logging.INFO, "  Ping URL: {}".format(insights_connection.ping_url)),
        (logging.INFO, ""),
    ]

    messages = pre_messages + messages

    record_tuples = [
        ("insights.client.connection", loglevel, message)
        for loglevel, message in messages
    ]
    assert (
        caplog.record_tuples == auth_record_tuples + url_record_tuples + record_tuples
    )


@pytest.mark.parametrize(
    ["side_effect", "expected_rc"],
    [
        (
            [
                _response(status_code=requests.codes.ok),
                _response(status_code=requests.codes.ok),
                _response(status_code=requests.codes.ok),
            ],
            0,
        ),
        (
            [
                _response(status_code=requests.codes.ok),
                _response(status_code=requests.codes.ok),
                requests.exceptions.ConnectionError("error"),
            ],
            1,
        ),
        (
            [
                _response(status_code=requests.codes.ok),
                requests.exceptions.ConnectionError("error"),
            ],
            1,
        ),
        (
            [
                requests.exceptions.ConnectionError("error"),
            ],
            1,
        ),
    ],
)
@pytest.mark.insights_config(legacy_upload=False)
def test_test_connection_urls_until_fail_return_value(
    side_effect, expected_rc, insights_connection
):
    """An Upload URL, an Inventory URL and a Ping URL are tested until the first failure."""
    _valid_auth_config(insights_connection)
    insights_connection.session.request.side_effect = side_effect

    actual_rc = insights_connection.test_connection()
    assert actual_rc == expected_rc
