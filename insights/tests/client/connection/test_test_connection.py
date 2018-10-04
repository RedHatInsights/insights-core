# -*- coding: UTF-8 -*-

from mock.mock import call, patch
from pytest import fixture


@fixture()
def patch_test_openssl():
    with patch("insights.client.connection.InsightsConnection._test_openssl") as test_openssl:
        yield test_openssl


@fixture()
def patch_test_urls():
    with patch("insights.client.connection.InsightsConnection._test_urls") as test_urls:
        yield test_urls


@fixture()
def patch_print():
    with patch("insights.client.connection.print") as print_mock:
        yield print_mock


@fixture()
def test_urls_post_call():
    def fixture(insights_connection):
        return call(insights_connection.upload_url, "POST")
    return fixture


@fixture()
def test_urls_get_call():
    def fixture(insights_connection):
        return call(insights_connection.api_url, "GET")
    return fixture


@fixture()
def assert_test_connection_result():
    def assertion(result):
        assert result == 1
    return assertion


@fixture()
def assert_test_urls_calls():
    def assertion(test_urls_mock, calls):
        test_urls_mock.assert_has_calls(calls)
        assert len(test_urls_mock.mock_calls) == len(calls)
    return assertion


@fixture()
def assert_test_urls_post_calls(assert_test_urls_calls, test_urls_post_call):
    def assertion(test_urls_mock, insights_connection):
        calls = [test_urls_post_call(insights_connection)]
        return assert_test_urls_calls(test_urls_mock, calls)
    return assertion


@fixture()
def assert_test_urls_get_calls(assert_test_urls_calls, test_urls_post_call, test_urls_get_call):
    def assertion(test_urls_mock, insights_connection):
        calls = [test_urls_post_call(insights_connection),
                 test_urls_get_call(insights_connection)]
        return assert_test_urls_calls(test_urls_mock, calls)
    return assertion


@fixture()
def assert_print_call(isinstance_matcher):
    def assertion(print_mock, expected_error):
        matcher = isinstance_matcher(expected_error)
        print_mock.assert_called_once_with(matcher)
    return assertion


def test_post_connection_timeout(patch_test_openssl,
                                 patch_test_urls,
                                 patch_print,
                                 insights_connection,
                                 timeout_error,
                                 assert_test_connection_result,
                                 assert_test_urls_post_calls,
                                 assert_print_call):
    patch_test_urls.side_effect = [timeout_error, True]

    connection = insights_connection()
    result = connection.test_connection()

    assert_test_connection_result(result)

    assert_test_urls_post_calls(patch_test_urls, connection)
    assert_print_call(patch_print, timeout_error)


def test_post_connection_error(patch_test_openssl,
                               patch_test_urls,
                               patch_print,
                               insights_connection,
                               assert_test_connection_result,
                               connection_error,
                               assert_print_call):
    patch_test_urls.side_effect = [connection_error, True]

    connection = insights_connection()
    result = connection.test_connection()

    assert_test_connection_result(result)

    assert_test_urls_post_calls(patch_test_urls, connection)
    assert_print_call(patch_print, connection_error)


def test_get_connection_timeout(patch_test_openssl,
                                patch_test_urls,
                                patch_print,
                                insights_connection,
                                timeout_error,
                                assert_test_connection_result,
                                assert_test_urls_get_calls,
                                assert_print_call):
    patch_test_urls.side_effect = [True, timeout_error]

    connection = insights_connection()
    result = connection.test_connection()

    assert_test_connection_result(result)

    assert_test_urls_get_calls(patch_test_urls, connection)
    assert_print_call(patch_print, timeout_error)


def test_get_connection_error(patch_test_openssl,
                              patch_test_urls,
                              patch_print,
                              insights_connection,
                              connection_error,
                              assert_test_connection_result,
                              assert_test_urls_get_calls,
                              assert_print_call):
    patch_test_urls.side_effect = [True, connection_error]

    connection = insights_connection()
    result = connection.test_connection()

    assert_test_connection_result(result)

    assert_test_urls_get_calls(patch_test_urls, connection)
    assert_print_call(patch_print, connection_error)
