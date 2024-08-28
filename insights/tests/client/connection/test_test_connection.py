from logging import ERROR
from mock.mock import ANY
from mock.mock import call
from mock.mock import Mock
from mock.mock import patch

from pytest import fixture
from pytest import mark
from pytest import raises
from requests.exceptions import ConnectTimeout
from requests.exceptions import ReadTimeout
from requests.exceptions import SSLError

from insights.client.config import InsightsConfig
from insights.client.connection import InsightsConnection

EXCEPTION_MESSAGE = "request exception"
UPLOAD_URL = "https://www.example.com/insights"
LEGACY_URL = "https://www.example.com"
LEGACY_URL_SUFFIXES = ["/insights/", "", "/r", "/r/insights"]
EXPECTED_EXCEPTIONS = [SSLError, ConnectTimeout, ReadTimeout]

LOGGING_FILE = "logging-file.log"
parametrize_exceptions = mark.parametrize(
    ["exception"],
    [(exception,) for exception in EXPECTED_EXCEPTIONS],
)
parametrize_methods = mark.parametrize(
    ["http_method", "request_function"],
    [
        ("GET", "insights.client.connection.InsightsConnection.get"),
        ("POST", "insights.client.connection.InsightsConnection.post")
    ]
)


@fixture
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
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
@patch("insights.client.connection.InsightsConnection._legacy_test_urls")
def test_test_urls_legacy_test_urls(legacy_test_urls, http_method, request_function, insights_connection):
    """The non-legacy URL subtest hands over to its legacy counterpart if legacy_upload is enabled."""
    insights_connection.config.legacy_upload = True

    result = insights_connection._test_urls(UPLOAD_URL, http_method)

    legacy_test_urls.assert_called_once_with(UPLOAD_URL, http_method)
    assert result == legacy_test_urls.return_value


@parametrize_methods
@patch("insights.client.connection.TemporaryFile")
@patch("insights.client.connection.InsightsConnection._legacy_test_urls")
def test_test_urls_not_legacy_test_urls(legacy_test_urls, temporary_file, http_method, request_function, insights_connection):
    """The non-legacy URL subtest doesn’t hand over to its legacy counterpart if legacy_upload is disabled."""
    insights_connection.config.legacy_upload = False

    with patch(request_function):
        insights_connection._test_urls(UPLOAD_URL, http_method)
    legacy_test_urls.assert_not_called()


@patch("insights.client.connection.InsightsConnection.post")
@patch("insights.client.connection.TemporaryFile")
@patch("insights.client.connection.InsightsConnection.get")
def test_test_urls_get_no_catch(get, temporary_file, post, insights_connection):
    """The non-legacy URL subtest issues one GET request in case of an unknown exception."""
    get.side_effect = Exception
    insights_connection.config.legacy_upload = False

    try:
        insights_connection._test_urls(UPLOAD_URL, "GET")
    except Exception:
        pass

    get.assert_called_once_with(UPLOAD_URL)
    post.assert_not_called()


@patch("insights.client.connection.InsightsConnection.post")
@patch("insights.client.connection.TemporaryFile")
@patch("insights.client.connection.InsightsConnection.get")
def test_test_urls_get_success(get, temporary_file, post, insights_connection):
    """The non-legacy URL subtest issues one GET request if the API call succeeds."""
    insights_connection.config.legacy_upload = False

    insights_connection._test_urls(UPLOAD_URL, "GET")

    get.assert_called_once_with(UPLOAD_URL)
    post.assert_not_called()


@parametrize_exceptions
@patch("insights.client.connection.InsightsConnection.post")
@patch("insights.client.connection.TemporaryFile")
@patch("insights.client.connection.InsightsConnection.get")
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


@patch("insights.client.connection.InsightsConnection.post")
@patch("insights.client.connection.TemporaryFile")
@patch("insights.client.connection.InsightsConnection.get")
def test_test_urls_post_no_catch(get, temporary_file, post, insights_connection):
    """The non-legacy URL subtest issues one POST request in case of an unknown exception."""
    post.side_effect = Exception
    insights_connection.config.legacy_upload = False

    try:
        insights_connection._test_urls(UPLOAD_URL, "POST")
    except Exception:
        pass

    post.assert_called_once_with(UPLOAD_URL, files=ANY)
    get.assert_not_called()


@patch("insights.client.connection.InsightsConnection.post")
@patch("insights.client.connection.TemporaryFile")
@patch("insights.client.connection.InsightsConnection.get")
def test_test_urls_post_success(get, temporary_file, post, insights_connection):
    """The non-legacy URL subtest issues one POST request if the API call succeeds."""
    insights_connection.config.legacy_upload = False

    insights_connection._test_urls(UPLOAD_URL, "POST")
    post.assert_called_once_with(UPLOAD_URL, files=ANY)
    get.assert_not_called()


@parametrize_exceptions
@patch("insights.client.connection.InsightsConnection.post")
@patch("insights.client.connection.TemporaryFile")
@patch("insights.client.connection.InsightsConnection.get")
def test_test_urls_post_fail(get, temporary_file, post, exception, insights_connection):
    """The non-legacy URL subtest issues one POST request if the API call fails."""
    post.side_effect = exception
    insights_connection.config.legacy_upload = False

    try:
        insights_connection._test_urls(UPLOAD_URL, "POST")
    except exception:
        pass

    post.assert_called_once_with(UPLOAD_URL, files=ANY)
    get.assert_not_called()


@parametrize_methods
@patch("insights.client.connection.TemporaryFile")
def test_test_urls_no_catch(temporary_file, http_method, request_function, insights_connection):
    """The non-legacy URL subtest doesn’t catch unknown exceptions."""
    insights_connection.config.legacy_upload = False

    raised = Exception()

    with raises(Exception) as caught:
        with patch(request_function) as request_function_mock:
            request_function_mock.side_effect = raised
            insights_connection._test_urls(UPLOAD_URL, http_method)

    assert caught.value is raised


@parametrize_exceptions
@parametrize_methods
@patch("insights.client.connection.TemporaryFile")
def test_test_urls_raise(temporary_file, http_method, request_function, exception, insights_connection):
    """The non-legacy URL subtest re-raises the API call failure exception."""
    insights_connection.config.legacy_upload = False

    raised = exception()

    with raises(exception) as caught:
        with patch(request_function) as request_function_mock:
            request_function_mock.side_effect = raised
            insights_connection._test_urls(UPLOAD_URL, http_method)

    assert caught.value is raised


@parametrize_methods
def test_test_urls_error_log_no_catch(http_method, request_function, insights_connection, caplog):
    """The non-legacy URL subtest doesn't log any errors in case of an unknown exception."""
    insights_connection.config.legacy_upload = False

    with caplog.at_level(ERROR, logger="insights.client.connection"):
        with patch(request_function) as request_function_mock:
            request_function_mock.side_effect = Exception
            try:
                insights_connection._test_urls(UPLOAD_URL, http_method)
            except Exception:
                pass

    assert not caplog.record_tuples


@parametrize_methods
def test_test_urls_error_log_success(http_method, request_function, insights_connection, caplog):
    """The non-legacy URL subtest doesn't log any errors if all API calls succeed."""
    insights_connection.config.legacy_upload = False

    with caplog.at_level(ERROR, logger="insights.client.connection"):
        with patch(request_function):
            insights_connection._test_urls(UPLOAD_URL, http_method)

    assert not caplog.record_tuples


@parametrize_exceptions
@parametrize_methods
def test_test_urls_error_log_fail(http_method, request_function, exception, insights_connection, caplog):
    """The non-legacy URL subtest logs an ERROR if an API call fails."""
    insights_connection.config.legacy_upload = False

    with caplog.at_level(ERROR, logger="insights.client.connection"):
        try:
            with patch(request_function) as request_function_mock:
                request_function_mock.side_effect = exception
                insights_connection._test_urls(UPLOAD_URL, http_method)
        except exception:
            pass

    assert caplog.record_tuples == [(
        "insights.client.connection",
        ERROR,
        "Could not successfully connect to: %s" % (UPLOAD_URL,)
    )]


@parametrize_methods
def test_test_urls_print_no_catch(http_method, request_function, insights_connection, capsys):
    """The non-legacy URL subtest doesn't print anything in case of an unknown exception."""
    insights_connection.config.legacy_upload = False

    with patch(request_function) as request_function_mock:
        request_function_mock.side_effect = Exception
        try:
            insights_connection._test_urls(UPLOAD_URL, http_method)
        except Exception:
            pass

    out, err = capsys.readouterr()
    assert not out
    assert not err


@parametrize_methods
def test_test_urls_print_success(http_method, request_function, insights_connection, capsys):
    """The non-legacy URL subtest doesn’t print anything if all API calls succeed."""
    insights_connection.config.legacy_upload = False

    with patch(request_function):
        insights_connection._test_urls(UPLOAD_URL, http_method)

    out, err = capsys.readouterr()
    assert not out
    assert not err


@parametrize_exceptions
@parametrize_methods
def test_test_urls_print_fail(http_method, request_function, exception, insights_connection, capsys):
    """The non-legacy URL subtest prints the exception details if an API call fails."""
    insights_connection.config.legacy_upload = False

    with patch(request_function) as request_function_mock:
        request_function_mock.side_effect = exception(EXCEPTION_MESSAGE)
        try:
            insights_connection._test_urls(UPLOAD_URL, http_method)
        except exception:
            pass

    out, err = capsys.readouterr()
    assert out == EXCEPTION_MESSAGE + "\n"
    assert not err


@patch("insights.client.connection.InsightsConnection.post")
@patch("insights.client.connection.InsightsConnection.get")
def test_legacy_urls_get_no_catch(get, post, insights_connection):
    """The legacy URL subtest issues one GET request in case of an unknown exception."""
    get.side_effect = Exception

    try:
        insights_connection._legacy_test_urls(UPLOAD_URL, "GET")
    except Exception:
        pass

    get.assert_called_once_with(LEGACY_URL + LEGACY_URL_SUFFIXES[0])
    post.assert_not_called()


@patch("insights.client.connection.InsightsConnection.post")
@patch("insights.client.connection.InsightsConnection.get")
def test_legacy_urls_get_success(get, post, insights_connection):
    """The non-legacy URL subtest issues one GET request if the API call succeeds."""
    insights_connection._legacy_test_urls(UPLOAD_URL, "GET")

    get.assert_called_once_with(LEGACY_URL + LEGACY_URL_SUFFIXES[0])
    post.assert_not_called()


@parametrize_exceptions
@patch("insights.client.connection.InsightsConnection.post")
@patch("insights.client.connection.InsightsConnection.get")
def test_legacy_urls_get_one_fail(get, post, exception, insights_connection):
    """The non-legacy URL subtest issues one GET request if one API call fails."""
    get.side_effect = [exception, Mock()]

    insights_connection._legacy_test_urls(UPLOAD_URL, "GET")

    assert get.mock_calls == [
        call(LEGACY_URL + LEGACY_URL_SUFFIXES[0]),
        call(LEGACY_URL + LEGACY_URL_SUFFIXES[1]),
    ]
    post.assert_not_called()



@parametrize_exceptions
@patch("insights.client.connection.InsightsConnection.post")
@patch("insights.client.connection.InsightsConnection.get")
def test_legacy_urls_get_all_fails(get, post, exception, insights_connection):
    """The non-legacy URL subtest issues one GET request for every API call if the previous one fails."""
    get.side_effect = [exception] * len(LEGACY_URL_SUFFIXES)

    try:
        insights_connection._legacy_test_urls(UPLOAD_URL, "GET")
    except exception:
        pass

    assert get.mock_calls == [call(LEGACY_URL + suffix) for suffix in LEGACY_URL_SUFFIXES]
    post.assert_not_called()



@patch("insights.client.connection.InsightsConnection.post")
@patch("insights.client.connection.InsightsConnection.get")
def test_legacy_urls_post_no_catch(get, post, insights_connection):
    """The legacy URL subtest issues one POST request in case of an unknown exception."""
    post.side_effect = Exception

    try:
        insights_connection._legacy_test_urls(UPLOAD_URL, "POST")
    except Exception:
        pass

    post.assert_called_once_with(LEGACY_URL + LEGACY_URL_SUFFIXES[0], data=ANY)
    get.assert_not_called()


@patch("insights.client.connection.InsightsConnection.post")
@patch("insights.client.connection.InsightsConnection.get")
def test_legacy_urls_post_success(get, post, insights_connection):
    """The non-legacy URL subtest issues one POST request if the API call succeeds."""
    insights_connection._legacy_test_urls(UPLOAD_URL, "POST")

    post.assert_called_once_with(LEGACY_URL + LEGACY_URL_SUFFIXES[0], data=ANY)
    get.assert_not_called()


@parametrize_exceptions
@patch("insights.client.connection.InsightsConnection.post")
@patch("insights.client.connection.InsightsConnection.get")
def test_legacy_urls_post_one_fail(get, post, exception, insights_connection):
    """The non-legacy URL subtest issues one POST request if one API call fails."""
    post.side_effect = [exception, Mock(status_code=200)]

    insights_connection._legacy_test_urls(UPLOAD_URL, "POST")

    assert post.mock_calls == [
        call(LEGACY_URL + LEGACY_URL_SUFFIXES[0], data=ANY),
        call(LEGACY_URL + LEGACY_URL_SUFFIXES[1], data=ANY),
    ]
    get.assert_not_called()


@parametrize_exceptions
@patch("insights.client.connection.InsightsConnection.post")
@patch("insights.client.connection.InsightsConnection.get")
def test_legacy_urls_post_all_fails(get, post, exception, insights_connection):
    """The non-legacy URL subtest issues one POST request for every API call if the previous one fails."""
    post.side_effect = [exception] * len(LEGACY_URL_SUFFIXES)

    try:
        insights_connection._legacy_test_urls(UPLOAD_URL, "POST")
    except exception:
        pass

    assert post.mock_calls == [call(LEGACY_URL + suffix, data=ANY) for suffix in LEGACY_URL_SUFFIXES]
    get.assert_not_called()


@parametrize_methods
def test_legacy_urls_no_catch(http_method, request_function, insights_connection):
    """The legacy URL subtest doesn’t catch unknown exceptions."""
    exception = Exception()

    with raises(Exception) as caught:
        with patch(request_function) as request_function_mock:
            request_function_mock.side_effect = [exception]
            insights_connection._legacy_test_urls(UPLOAD_URL, http_method)

    assert caught.value is exception


@parametrize_exceptions
@parametrize_methods
def test_legacy_urls_raise(http_method, request_function, exception, insights_connection):
    """The legacy URL subtest re-raises the last API call failure exception."""
    exceptions = [exception() for _ in LEGACY_URL_SUFFIXES]

    with raises(exception) as caught:
        with patch(request_function) as request_function_mock:
            request_function_mock.side_effect = exceptions
            insights_connection._legacy_test_urls(UPLOAD_URL, http_method)

    assert caught.value is exceptions[-1]


@parametrize_methods
def test_legacy_urls_error_log_no_catch(http_method, request_function, insights_connection, caplog):
    """The legacy URL subtest doesn't log any errors in case of an unknown exception."""
    with caplog.at_level(ERROR, logger="insights.client.connection"):
        with patch(request_function) as request_function_mock:
            request_function_mock.side_effect = Exception
            try:
                insights_connection._legacy_test_urls(UPLOAD_URL, http_method)
            except Exception:
                pass

    assert not caplog.record_tuples


@parametrize_exceptions
@parametrize_methods
def test_legacy_urls_error_log_success(http_method, request_function, exception, insights_connection, caplog):
    """The legacy URL subtest doesn't log any errors if the API call succeeds."""
    with caplog.at_level(ERROR, logger="insights.client.connection"):
        with patch(request_function):
            insights_connection._legacy_test_urls(UPLOAD_URL, http_method)

    assert not caplog.record_tuples


@parametrize_exceptions
@parametrize_methods
def test_legacy_urls_error_log_one_fail(http_method, request_function, exception, insights_connection, caplog):
    """The legacy URL subtest logs one ERROR if one API call fails."""
    with caplog.at_level(ERROR, logger="insights.client.connection"):
        try:
            with patch(request_function) as request_function_mock:
                request_function_mock.side_effect = [exception(), Mock()]
                insights_connection._legacy_test_urls(UPLOAD_URL, http_method)
        except exception:
            pass

    assert caplog.record_tuples == [(
        "insights.client.connection",
        ERROR,
        "Could not successfully connect to: %s" % (LEGACY_URL + LEGACY_URL_SUFFIXES[0],)
    )]


@parametrize_exceptions
@parametrize_methods
def test_legacy_urls_error_log_all_fails(http_method, request_function, exception, insights_connection, caplog):
    """The legacy URL subtest logs one ERROR for every failed API call."""
    with caplog.at_level(ERROR, logger="insights.client.connection"):
        try:
            with patch(request_function) as request_function_mock:
                request_function_mock.side_effect = [exception() for _ in LEGACY_URL_SUFFIXES]
                insights_connection._legacy_test_urls(UPLOAD_URL, http_method)
        except exception:
            pass

    assert caplog.record_tuples == [
        (
            "insights.client.connection",
            ERROR,
            "Could not successfully connect to: %s" % (LEGACY_URL + suffix,)
        ) for suffix in LEGACY_URL_SUFFIXES
    ]


@parametrize_methods
def test_legacy_urls_exception_print_no_catch(http_method, request_function, insights_connection, capsys):
    """The legacy URL subtest doesn't print anything in case of an unknown exception."""
    with patch(request_function) as request_function_mock:
        request_function_mock.side_effect = Exception
        try:
            insights_connection._legacy_test_urls(UPLOAD_URL, http_method)
        except Exception:
            pass

    out, err = capsys.readouterr()
    assert not out
    assert not err


@parametrize_exceptions
@parametrize_methods
def test_legacy_urls_exception_print_success(http_method, request_function, exception, insights_connection, capsys):
    """The legacy URL subtest prints a message pointing to a log file if the API call succeeds."""
    with patch(request_function):
        insights_connection._legacy_test_urls(UPLOAD_URL, http_method)

    out, err = capsys.readouterr()
    assert not out
    assert not err


@parametrize_exceptions
@parametrize_methods
def test_legacy_urls_exception_print_one_fail(http_method, request_function, exception, insights_connection, capsys):
    """The legacy URL subtest prints the exception details if one API call fails."""
    try:
        with patch(request_function) as request_function_mock:
            request_function_mock.side_effect = [exception(EXCEPTION_MESSAGE), Mock()]
            insights_connection._legacy_test_urls(UPLOAD_URL, http_method)
    except exception:
        pass

    out, err = capsys.readouterr()
    assert out == EXCEPTION_MESSAGE + "\n"
    assert not err


@parametrize_exceptions
@parametrize_methods
def test_legacy_urls_exception_print_all_fails(http_method, request_function, exception, insights_connection, capsys):
    """The legacy connection test prints the details for every exception if all API calls fail."""
    exceptions = [exception("%s %s" % (EXCEPTION_MESSAGE, suffix,)) for suffix in LEGACY_URL_SUFFIXES]

    try:
        with patch(request_function) as request_function_mock:
            request_function_mock.side_effect = exceptions
            insights_connection._legacy_test_urls(UPLOAD_URL, http_method)
    except exception:
        pass

    out, err = capsys.readouterr()
    assert out == "".join(str(exc) + "\n" for exc in exceptions)
    assert not err


@patch("insights.client.connection.InsightsConnection._test_urls")
def test_test_connection_test_urls_no_catch(test_urls, insights_connection):
    """The connection test doesn’t catch unknown exceptions."""
    test_urls.side_effect = Exception

    try:
        insights_connection.test_connection()
    except Exception:
        pass
    test_urls.assert_called_once_with(insights_connection.upload_url, "POST")


@patch("insights.client.connection.InsightsConnection._test_urls")
def test_test_connection_test_urls_success(test_urls, insights_connection):
    """The connection test consists of several API calls."""
    insights_connection.test_connection()
    assert len(test_urls.mock_calls) > 1


@parametrize_exceptions
@patch("insights.client.connection.InsightsConnection._test_urls")
def test_test_connection_test_urls_fail(test_urls, exception, insights_connection):
    """The connection test is stopped after the first API call failure."""
    test_urls.side_effect = exception

    insights_connection.test_connection()
    test_urls.assert_called_once()


@patch("insights.client.connection.InsightsConnection._test_urls")
def test_test_connection_error_log_no_catch(test_urls, insights_connection, caplog):
    """The connection test doesn't log any errors in case of an unknown exception."""
    test_urls.side_effect = Exception

    with caplog.at_level(ERROR, logger="insights.client.connection"):
        try:
            insights_connection.test_connection()
        except Exception:
            pass

    assert not caplog.record_tuples


@patch("insights.client.connection.InsightsConnection._test_urls")
def test_test_connection_error_log_success(test_urls, insights_connection, caplog):
    """The connection test doesn't log any errors if all API calls succeed."""
    with caplog.at_level(ERROR, logger="insights.client.connection"):
        insights_connection.test_connection()

    assert not caplog.record_tuples


@parametrize_exceptions
@patch("insights.client.connection.InsightsConnection._test_urls")
def test_test_connection_error_log_fail(test_urls, exception, insights_connection, caplog):
    """The connection test logs an ERROR if an API call fails."""
    test_urls.side_effect = exception

    with caplog.at_level(ERROR, logger="insights.client.connection"):
        insights_connection.test_connection()

    assert caplog.record_tuples == [
        ("insights.client.connection", ERROR, "Connectivity test failed! Please check your network configuration")
    ]


@patch("insights.client.connection.InsightsConnection._test_urls")
def test_test_connection_print_no_catch(test_urls, insights_connection, capsys):
    """The connection test doesn't print anything in case of an unknown exception."""
    test_urls.side_effect = Exception

    try:
        insights_connection.test_connection()
    except Exception:
        pass

    out, err = capsys.readouterr()
    assert not out
    assert not err


@patch("insights.client.connection.InsightsConnection._test_urls")
def test_test_connection_print_success(test_urls, insights_connection, capsys):
    """The connection test prints a message pointing to a log file if all API calls succeed."""
    insights_connection.test_connection()

    out, err = capsys.readouterr()
    assert out == "See %s for more details.\n" % (LOGGING_FILE,)
    assert not err


@parametrize_exceptions
@patch("insights.client.connection.InsightsConnection._test_urls")
def test_test_connection_print_fail(test_urls, exception, insights_connection, capsys):
    """The connection test prints a message pointing to a log file if an API call fails."""
    test_urls.side_effect = exception

    insights_connection.test_connection()
    out, err = capsys.readouterr()
    assert out == "Additional information may be in %s\n" % (LOGGING_FILE,)
    assert not err


@patch("insights.client.connection.InsightsConnection._test_urls")
def test_test_connection_no_catch(test_urls, insights_connection):
    """The connection test doesn’t catch and recreate an unknown exception."""
    expected = Exception()
    test_urls.side_effect = expected

    with raises(Exception) as caught:
        insights_connection.test_connection()

    assert caught.value is expected


@patch("insights.client.connection.InsightsConnection._test_urls")
def test_test_connection_return_code_success(test_urls, insights_connection):
    """The connection test returns a zero code if all API calls succeed."""
    result = insights_connection.test_connection()
    assert result == 0


@parametrize_exceptions
@patch("insights.client.connection.InsightsConnection._test_urls")
def test_test_connection_return_code_fail(test_urls, exception, insights_connection):
    """The connection test returns a non-zero code if an API call fails."""
    test_urls.side_effect = exception

    result = insights_connection.test_connection()
    assert result > 0


@patch("insights.client.connection.InsightsConnection.post")
@patch("insights.client.connection.TemporaryFile")
def test_test_connection_non_legacy_error_log_no_catch(temporary_file, post, insights_connection, caplog):
    """The non-legacy connection test doesn't log any errors in case of an unknown exception."""
    post.side_effect = Exception
    insights_connection.config.legacy_upload = False

    with caplog.at_level(ERROR, logger="insights.client.connection"):
        try:
            insights_connection.test_connection()
        except Exception:
            pass

    assert not caplog.record_tuples


@patch("insights.client.connection.InsightsConnection.get")
@patch("insights.client.connection.InsightsConnection.post")
@patch("insights.client.connection.TemporaryFile")
def test_test_connection_non_legacy_error_log_success(temporary_file, post, get, insights_connection, caplog):
    """The non-legacy connection test doesn't log any errors if all API calls succeed."""
    insights_connection.config.legacy_upload = False

    with caplog.at_level(ERROR, logger="insights.client.connection"):
        insights_connection.test_connection()

    assert not caplog.record_tuples


@parametrize_exceptions
@patch("insights.client.connection.InsightsConnection.post")
@patch("insights.client.connection.TemporaryFile")
def test_test_connection_non_legacy_error_log_fail(temporary_file, post, exception, insights_connection, caplog):
    """The connection test logs an ERROR if an API call fails."""
    post.side_effect = exception
    insights_connection.config.legacy_upload = False

    with caplog.at_level(ERROR, logger="insights.client.connection"):
        insights_connection.test_connection()

    assert caplog.record_tuples == [
        ("insights.client.connection", ERROR, message)
        for message in [
            "Could not successfully connect to: %s" % (UPLOAD_URL,),
            "Connectivity test failed! Please check your network configuration",
        ]
    ]


@patch("insights.client.connection.InsightsConnection.post")
@patch("insights.client.connection.TemporaryFile")
def test_test_connection_non_legacy_print_no_catch(temporary_file, post, insights_connection, capsys):
    """The non-legacy connection test doesn't print anything in case of an unknown exception."""
    post.side_effect = Exception
    insights_connection.config.legacy_upload = False

    try:
        insights_connection.test_connection()
    except Exception:
        pass

    out, err = capsys.readouterr()
    assert not out
    assert not err


@patch("insights.client.connection.InsightsConnection.get")
@patch("insights.client.connection.InsightsConnection.post")
@patch("insights.client.connection.TemporaryFile")
def test_test_connection_non_legacy_print_success(temporary_file, post, get, insights_connection, capsys):
    """The non-legacy connection test prints a message pointing to a log file if all API calls succeed."""
    insights_connection.config.legacy_upload = False

    insights_connection.test_connection()

    out, err = capsys.readouterr()
    assert out == "See %s for more details.\n" % (LOGGING_FILE,)
    assert not err


@parametrize_exceptions
@patch("insights.client.connection.InsightsConnection.post")
@patch("insights.client.connection.TemporaryFile")
def test_test_connection_non_legacy_print_fail(temporary_file, post, exception, insights_connection, capsys):
    """The non-legacy connection test prints the exception details and a message pointing to a log file if an API call fails."""
    post.side_effect = exception(EXCEPTION_MESSAGE)
    insights_connection.config.legacy_upload = False

    insights_connection.test_connection()

    out, err = capsys.readouterr()
    assert out == "%s\nAdditional information may be in %s\n" % (EXCEPTION_MESSAGE, LOGGING_FILE,)
    assert not err


@patch("insights.client.connection.InsightsConnection.post")
def test_test_connection_legacy_error_log_no_catch(post, insights_connection, caplog):
    """The legacy connection test doesn't log any errors in case of an unknown exception."""
    post.side_effect = Exception
    insights_connection.config.legacy_upload = True

    with caplog.at_level(ERROR, logger="insights.client.connection"):
        try:
            insights_connection.test_connection()
        except Exception:
            pass

    assert not caplog.record_tuples


@parametrize_exceptions
@patch("insights.client.connection.InsightsConnection.post")
def test_test_connection_legacy_error_log_success(post, exception, insights_connection, caplog):
    """The legacy connection test doesn't log any errors if all API calls succeed."""
    insights_connection.config.legacy_upload = True

    with caplog.at_level(ERROR, logger="insights.client.connection"):
        insights_connection.test_connection()

    assert not caplog.record_tuples


@parametrize_exceptions
@patch("insights.client.connection.InsightsConnection.post")
def test_test_connection_legacy_error_log_one_fail(post, exception, insights_connection, caplog):
    """The connection test logs one ERROR if one API call fails."""
    post.side_effect = [exception, Mock()]
    insights_connection.config.legacy_upload = True

    with caplog.at_level(ERROR, logger="insights.client.connection"):
        insights_connection.test_connection()

    assert caplog.record_tuples == [(
        "insights.client.connection",
        ERROR,
        "Could not successfully connect to: %s" % (LEGACY_URL + LEGACY_URL_SUFFIXES[0],),
    )]


@parametrize_exceptions
@patch("insights.client.connection.InsightsConnection.post")
def test_test_connection_legacy_error_log_all_fails(post, exception, insights_connection, caplog):
    """The connection test logs one ERROR for every failed API call."""
    post.side_effect = exception
    insights_connection.config.legacy_upload = True

    with caplog.at_level(ERROR, logger="insights.client.connection"):
        insights_connection.test_connection()

    legacy_test_url_errors = [
        "Could not successfully connect to: %s" % (LEGACY_URL + suffix,)
        for suffix in LEGACY_URL_SUFFIXES
    ]
    test_connection_errors = [
        "Connectivity test failed! Please check your network configuration",
    ]
    assert caplog.record_tuples == [
        ("insights.client.connection", ERROR, message)
        for message in legacy_test_url_errors + test_connection_errors
    ]


@patch("insights.client.connection.InsightsConnection.post")
@patch("insights.client.connection.TemporaryFile")
def test_test_connection_legacy_print_no_catch(temporary_file, post, insights_connection, capsys):
    """The legacy connection test doesn't print anything in case of an unknown exception."""
    post.side_effect = Exception
    insights_connection.config.legacy_upload = False

    try:
        insights_connection.test_connection()
    except Exception:
        pass

    out, err = capsys.readouterr()
    assert not out
    assert not err


@patch("insights.client.connection.InsightsConnection.post")
@patch("insights.client.connection.TemporaryFile")
def test_test_connection_legacy_print_success(temporary_file, post, insights_connection, capsys):
    """The legacy connection test prints a message pointing to a log file if all API calls succeed."""
    insights_connection.config.legacy_upload = False

    insights_connection.test_connection()

    out, err = capsys.readouterr()
    assert out == "See %s for more details.\n" % (LOGGING_FILE,)
    assert not err


@parametrize_exceptions
@patch("insights.client.connection.InsightsConnection.post")
def test_test_connection_legacy_print_one_fail(post, exception, insights_connection, capsys):
    """The legacy connection test prints the exception details and a message pointing to a log file if one API call fails."""
    post.side_effect = [exception(EXCEPTION_MESSAGE), Mock()]
    insights_connection.config.legacy_upload = True

    insights_connection.test_connection()

    out, err = capsys.readouterr()
    assert out == "%s\nSee %s for more details.\n" % (EXCEPTION_MESSAGE, LOGGING_FILE,)
    assert not err


@parametrize_exceptions
@patch("insights.client.connection.InsightsConnection.post")
def test_test_connection_legacy_print_all_fails(post, exception, insights_connection, capsys):
    """The legacy connection test prints the details for every exception and a message pointing to a log file if all API calls fail."""
    post.side_effect = exception(EXCEPTION_MESSAGE)
    insights_connection.config.legacy_upload = True

    insights_connection.test_connection()

    out, err = capsys.readouterr()

    exception_messages = "%s\n" % (EXCEPTION_MESSAGE,) * len(LEGACY_URL_SUFFIXES)
    test_connection_message = "Additional information may be in %s\n" % (LOGGING_FILE,)

    assert out == exception_messages + test_connection_message
    assert not err
