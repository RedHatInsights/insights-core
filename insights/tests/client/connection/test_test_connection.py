import pytest
import requests
from mock import mock

from insights.client.config import InsightsConfig
from insights.client.connection import InsightsConnection


class UnexpectedException(Exception):
    pass


LOGGING_FILE = "logging-file.log"
UPLOAD_URL = "https://www.example.com/insights"
LEGACY_URL = "https://www.example.com"
LEGACY_URL_SUFFIXES = ["/insights/", "", "/r", "/r/insights"]

EXPECTED_EXCEPTIONS = [
    requests.exceptions.SSLError,
    requests.exceptions.ConnectTimeout,
    requests.exceptions.ReadTimeout,
]
parametrize_methods = pytest.mark.parametrize(
    ["http_method", "request_function"],
    [
        ("GET", "insights.client.connection.InsightsConnection.get"),
        ("POST", "insights.client.connection.InsightsConnection.post"),
    ],
)


def parametrize_exceptions(exceptions):
    return pytest.mark.parametrize(
        ["exception"],
        [(exception,) for exception in exceptions],
    )


@pytest.fixture
@mock.patch("insights.client.connection.InsightsConnection._init_session")
@mock.patch("insights.client.connection.InsightsConnection.get_proxies")
def insights_connection(get_proxies, init_session):
    config = InsightsConfig(
        base_url="www.example.com",
        logging_file=LOGGING_FILE,
        upload_url=UPLOAD_URL,
    )

    connection = InsightsConnection(config)
    connection.proxies = None

    return connection


@parametrize_methods
@mock.patch("insights.client.connection.InsightsConnection._legacy_test_urls")
def test_test_urls_legacy_test_urls_call(
    legacy_test_urls, http_method, request_function, insights_connection
):
    """The non-legacy URL subtest hands over to its legacy counterpart if legacy_upload is enabled."""
    insights_connection.config.legacy_upload = True

    insights_connection._test_urls(UPLOAD_URL, http_method)

    legacy_test_urls.assert_called_once_with(UPLOAD_URL, http_method)


@parametrize_methods
@mock.patch("insights.client.connection.InsightsConnection._legacy_test_urls")
def test_test_urls_legacy_test_urls_result(
    legacy_test_urls, http_method, request_function, insights_connection
):
    """The non-legacy URL subtest returns from its legacy counterpart if legacy_upload is enabled."""
    insights_connection.config.legacy_upload = True

    result = insights_connection._test_urls(UPLOAD_URL, http_method)

    assert result == legacy_test_urls.return_value


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


@mock.patch("insights.client.connection.InsightsConnection.post")
@mock.patch("insights.client.connection.TemporaryFile")
@mock.patch("insights.client.connection.InsightsConnection.get")
def test_test_urls_get_success(get, temporary_file, post, insights_connection):
    """The non-legacy URL subtest issues one GET request if the API call succeeds."""
    insights_connection.config.legacy_upload = False

    insights_connection._test_urls(UPLOAD_URL, "GET")

    get.assert_called_once_with(UPLOAD_URL)
    post.assert_not_called()


@parametrize_exceptions(EXPECTED_EXCEPTIONS)
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


@mock.patch("insights.client.connection.InsightsConnection.post")
@mock.patch("insights.client.connection.TemporaryFile")
@mock.patch("insights.client.connection.InsightsConnection.get")
def test_test_urls_post_success(get, temporary_file, post, insights_connection):
    """The non-legacy URL subtest issues one POST request if the API call succeeds."""
    insights_connection.config.legacy_upload = False

    insights_connection._test_urls(UPLOAD_URL, "POST")
    post.assert_called_once_with(UPLOAD_URL, files=mock.ANY)
    get.assert_not_called()


@parametrize_exceptions(EXPECTED_EXCEPTIONS)
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


@parametrize_exceptions(EXPECTED_EXCEPTIONS)
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


@parametrize_methods
@mock.patch("insights.client.connection.logger")
def test_test_urls_error_log_no_catch(
    logger, http_method, request_function, insights_connection
):
    """The non-legacy URL subtest doesn't log any errors in case of an unknown exception."""
    insights_connection.config.legacy_upload = False

    with mock.patch(request_function) as request_function_mock:
        request_function_mock.side_effect = UnexpectedException
        try:
            insights_connection._test_urls(UPLOAD_URL, http_method)
        except UnexpectedException:
            pass

    logger.error.assert_not_called()


@parametrize_methods
@mock.patch("insights.client.connection.logger")
def test_test_urls_error_log_success(
    logger, http_method, request_function, insights_connection
):
    """The non-legacy URL subtest doesn't log any errors if all API calls succeed."""
    insights_connection.config.legacy_upload = False

    with mock.patch(request_function):
        insights_connection._test_urls(UPLOAD_URL, http_method)

    logger.error.assert_not_called()


@parametrize_exceptions(EXPECTED_EXCEPTIONS)
@parametrize_methods
@mock.patch("insights.client.connection.logger")
def test_test_urls_error_log_fail(
    logger, http_method, request_function, exception, insights_connection
):
    """The non-legacy URL subtest logs an ERROR if an API call fails."""
    insights_connection.config.legacy_upload = False

    try:
        with mock.patch(request_function) as request_function_mock:
            request_function_mock.side_effect = exception
            insights_connection._test_urls(UPLOAD_URL, http_method)
    except exception:
        pass

    logger.error.assert_called_once()


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


@parametrize_exceptions(EXPECTED_EXCEPTIONS)
@parametrize_methods
def test_test_urls_print_fail(
    http_method, request_function, exception, insights_connection, capsys
):
    """The non-legacy URL subtest prints the exception details if an API call fails."""
    insights_connection.config.legacy_upload = False

    with mock.patch(request_function) as request_function_mock:
        request_function_mock.side_effect = exception
        try:
            insights_connection._test_urls(UPLOAD_URL, http_method)
        except exception:
            pass

    out, err = capsys.readouterr()
    assert out
    assert not err


@mock.patch("insights.client.connection.InsightsConnection.post")
@mock.patch("insights.client.connection.InsightsConnection.get")
def test_legacy_urls_get_no_catch(get, post, insights_connection):
    """The legacy URL subtest issues one GET request in case of an unknown exception."""
    get.side_effect = UnexpectedException

    try:
        insights_connection._legacy_test_urls(UPLOAD_URL, "GET")
    except UnexpectedException:
        pass

    get.assert_called_once_with(LEGACY_URL + LEGACY_URL_SUFFIXES[0])
    post.assert_not_called()


@mock.patch("insights.client.connection.InsightsConnection.post")
@mock.patch("insights.client.connection.InsightsConnection.get")
def test_legacy_urls_get_success(get, post, insights_connection):
    """The non-legacy URL subtest issues one GET request if the API call succeeds."""
    insights_connection._legacy_test_urls(UPLOAD_URL, "GET")

    get.assert_called_once_with(LEGACY_URL + LEGACY_URL_SUFFIXES[0])
    post.assert_not_called()


@parametrize_exceptions(EXPECTED_EXCEPTIONS)
@mock.patch("insights.client.connection.InsightsConnection.post")
@mock.patch("insights.client.connection.InsightsConnection.get")
def test_legacy_urls_get_one_fail(get, post, exception, insights_connection):
    """The non-legacy URL subtest issues one GET request if one API call fails."""
    get.side_effect = [exception, mock.Mock()]

    insights_connection._legacy_test_urls(UPLOAD_URL, "GET")

    assert get.mock_calls == [
        mock.call(LEGACY_URL + LEGACY_URL_SUFFIXES[0]),
        mock.call(LEGACY_URL + LEGACY_URL_SUFFIXES[1]),
    ]
    post.assert_not_called()


@parametrize_exceptions(EXPECTED_EXCEPTIONS)
@mock.patch("insights.client.connection.InsightsConnection.post")
@mock.patch("insights.client.connection.InsightsConnection.get")
def test_legacy_urls_get_all_fails(get, post, exception, insights_connection):
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


@mock.patch("insights.client.connection.InsightsConnection.post")
@mock.patch("insights.client.connection.InsightsConnection.get")
def test_legacy_urls_post_no_catch(get, post, insights_connection):
    """The legacy URL subtest issues one POST request in case of an unknown exception."""
    post.side_effect = UnexpectedException

    try:
        insights_connection._legacy_test_urls(UPLOAD_URL, "POST")
    except UnexpectedException:
        pass

    post.assert_called_once_with(LEGACY_URL + LEGACY_URL_SUFFIXES[0], data=mock.ANY)
    get.assert_not_called()


@mock.patch("insights.client.connection.InsightsConnection.post")
@mock.patch("insights.client.connection.InsightsConnection.get")
def test_legacy_urls_post_success(get, post, insights_connection):
    """The non-legacy URL subtest issues one POST request if the API call succeeds."""
    insights_connection._legacy_test_urls(UPLOAD_URL, "POST")

    post.assert_called_once_with(LEGACY_URL + LEGACY_URL_SUFFIXES[0], data=mock.ANY)
    get.assert_not_called()


@parametrize_exceptions(EXPECTED_EXCEPTIONS)
@mock.patch("insights.client.connection.InsightsConnection.post")
@mock.patch("insights.client.connection.InsightsConnection.get")
def test_legacy_urls_post_one_fail(get, post, exception, insights_connection):
    """The non-legacy URL subtest issues one POST request if one API call fails."""
    post.side_effect = [exception, mock.Mock(status_code=200)]

    insights_connection._legacy_test_urls(UPLOAD_URL, "POST")

    assert post.mock_calls == [
        mock.call(LEGACY_URL + LEGACY_URL_SUFFIXES[0], data=mock.ANY),
        mock.call(LEGACY_URL + LEGACY_URL_SUFFIXES[1], data=mock.ANY),
    ]
    get.assert_not_called()


@parametrize_exceptions(EXPECTED_EXCEPTIONS)
@mock.patch("insights.client.connection.InsightsConnection.post")
@mock.patch("insights.client.connection.InsightsConnection.get")
def test_legacy_urls_post_all_fails(get, post, exception, insights_connection):
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


@parametrize_exceptions(EXPECTED_EXCEPTIONS)
@parametrize_methods
def test_legacy_urls_no_catch(
    http_method, request_function, exception, insights_connection
):
    """The legacy URL subtest doesn't catch unknown exceptions."""
    raised = exception()

    with pytest.raises(exception) as caught:
        with mock.patch(request_function) as request_function_mock:
            request_function_mock.side_effect = raised
            insights_connection._legacy_test_urls(UPLOAD_URL, http_method)

    assert caught.value is raised


@parametrize_exceptions(EXPECTED_EXCEPTIONS)
@parametrize_methods
def test_legacy_urls_raise(
    http_method, request_function, exception, insights_connection
):
    """The legacy URL subtest re-raises the last API call failure exception."""
    exceptions = [exception() for _ in LEGACY_URL_SUFFIXES]

    with pytest.raises(exception) as caught:
        with mock.patch(request_function) as request_function_mock:
            request_function_mock.side_effect = exceptions
            insights_connection._legacy_test_urls(UPLOAD_URL, http_method)

    assert caught.value is exceptions[-1]


@parametrize_methods
@mock.patch("insights.client.connection.logger")
def test_legacy_urls_error_log_no_catch(
    logger, http_method, request_function, insights_connection
):
    """The legacy URL subtest doesn't log any errors in case of an unknown exception."""
    with mock.patch(request_function) as request_function_mock:
        request_function_mock.side_effect = UnexpectedException
        try:
            insights_connection._legacy_test_urls(UPLOAD_URL, http_method)
        except UnexpectedException:
            pass

    logger.error.assert_not_called()


@parametrize_exceptions(EXPECTED_EXCEPTIONS)
@parametrize_methods
@mock.patch("insights.client.connection.logger")
def test_legacy_urls_error_log_success(
    logger, http_method, request_function, exception, insights_connection
):
    """The legacy URL subtest doesn't log any errors if the API call succeeds."""
    with mock.patch(request_function):
        insights_connection._legacy_test_urls(UPLOAD_URL, http_method)

    logger.error.assert_not_called()


@parametrize_exceptions(EXPECTED_EXCEPTIONS)
@parametrize_methods
@mock.patch("insights.client.connection.logger")
def test_legacy_urls_error_log_one_fail(
    logger, http_method, request_function, exception, insights_connection
):
    """The legacy URL subtest logs one ERROR if one API call fails."""
    try:
        with mock.patch(request_function) as request_function_mock:
            request_function_mock.side_effect = [exception(), mock.Mock()]
            insights_connection._legacy_test_urls(UPLOAD_URL, http_method)
    except exception:
        pass

    logger.error.assert_called_once()


@parametrize_exceptions(EXPECTED_EXCEPTIONS)
@parametrize_methods
@mock.patch("insights.client.connection.logger")
def test_legacy_urls_error_log_all_fails(
    logger, http_method, request_function, exception, insights_connection
):
    """The legacy URL subtest logs one ERROR for every failed API call."""
    try:
        with mock.patch(request_function) as request_function_mock:
            request_function_mock.side_effect = [
                exception() for _ in LEGACY_URL_SUFFIXES
            ]
            insights_connection._legacy_test_urls(UPLOAD_URL, http_method)
    except exception:
        pass

    assert len(logger.error.mock_calls) == len(LEGACY_URL_SUFFIXES)


@parametrize_methods
def test_legacy_urls_exception_print_no_catch(
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


@parametrize_exceptions(EXPECTED_EXCEPTIONS)
@parametrize_methods
def test_legacy_urls_exception_print_success(
    http_method, request_function, exception, insights_connection, capsys
):
    """The legacy URL subtest prints a message pointing to a log file if the API call succeeds."""
    with mock.patch(request_function):
        insights_connection._legacy_test_urls(UPLOAD_URL, http_method)

    out, err = capsys.readouterr()
    assert not out
    assert not err


@parametrize_exceptions(EXPECTED_EXCEPTIONS)
@parametrize_methods
def test_legacy_urls_exception_print_one_fail(
    http_method, request_function, exception, insights_connection, capsys
):
    """The legacy URL subtest prints the exception details if one API call fails."""
    try:
        with mock.patch(request_function) as request_function_mock:
            request_function_mock.side_effect = [
                exception,
                mock.Mock(),
            ]
            insights_connection._legacy_test_urls(UPLOAD_URL, http_method)
    except exception:
        pass

    out, err = capsys.readouterr()
    assert out
    assert not err


@parametrize_exceptions(EXPECTED_EXCEPTIONS)
@parametrize_methods
def test_legacy_urls_exception_print_all_fails(
    http_method, request_function, exception, insights_connection, capsys
):
    """The legacy connection test prints the details for every exception if all API calls fail."""
    exceptions = [exception] * len(LEGACY_URL_SUFFIXES)

    try:
        with mock.patch(request_function) as request_function_mock:
            request_function_mock.side_effect = exceptions
            insights_connection._legacy_test_urls(UPLOAD_URL, http_method)
    except exception:
        pass

    out, err = capsys.readouterr()
    assert out.count("\n") == len(LEGACY_URL_SUFFIXES)
    assert not err
