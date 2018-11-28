# -*- coding: UTF-8 -*-

from mock.mock import call, patch
from pytest import fixture, raises
from six.moves import range


@fixture()
def tested_url_count():
    """
    Count of the URLs tested by the _test_urls method.
    """
    # (url.path + '/', '', '/r', '/r/insights')
    return 4


@fixture
def test_urls(insights_connection):
    """
    Calls the _test_urls method expecting an exception to be raised.
    """
    def _fixture(http_method, expected_error):
        with raises(expected_error):
            insights_connection()._test_urls("https://www.example.com/",
                                             http_method)
    return _fixture


@fixture
def assert_session_request_method_calls(tested_url_count):
    """
    Asserts the get/post method has been called for every tested URL.
    """
    def _fixture(session_request_method):
        assert len(session_request_method.mock_calls) == tested_url_count
    return _fixture


@fixture
def assert_print_calls(tested_url_count, isinstance_matcher):
    """
    Asserts the exception has been printed for every tested URL.
    """
    def _fixture(print_mock, error):
        print_calls = []
        for i in range(tested_url_count):
            matcher = isinstance_matcher(error)
            print_calls.append(call(matcher))
        print_mock.assert_has_calls(print_calls)
    return _fixture


@fixture
def patch_print():
    """
    Patches the stdlib print method so we can assert its calls.
    """
    with patch("insights.client.connection.print") as print_mock:
        yield print_mock


def test_get_connection_timeout(patch_init_session,
                                patch_print,
                                session_get_fail,
                                test_urls,
                                assert_session_request_method_calls,
                                assert_print_calls,
                                timeout_error):
    """
    GET request time-outs get printed and caught, the last exception is
    re-raised.
    """
    get = session_get_fail(patch_init_session.return_value, timeout_error)

    test_urls("GET", timeout_error)
    assert_session_request_method_calls(get)

    assert_print_calls(patch_print, timeout_error)


def test_get_connection_error(patch_init_session,
                              patch_print,
                              session_get_fail,
                              test_urls,
                              assert_session_request_method_calls,
                              assert_print_calls,
                              connection_error):
    """
    GET request connection errors get printed and caught, the last exception is
    re-raised.
    """
    get = session_get_fail(patch_init_session.return_value, connection_error)

    test_urls("GET", connection_error)
    assert_session_request_method_calls(get)

    assert_print_calls(patch_print, connection_error)


def test_post_connection_timeout(patch_init_session,
                                 patch_print,
                                 session_post_fail,
                                 test_urls,
                                 assert_session_request_method_calls,
                                 assert_print_calls,
                                 timeout_error):
    """
    POST request time-outs get printed and caught, the last exception is
    re-raised.
    """
    post = session_post_fail(patch_init_session.return_value, timeout_error)

    test_urls("POST", timeout_error)

    assert_session_request_method_calls(post)
    assert_print_calls(patch_print, timeout_error)


def test_post_connection_error(patch_init_session,
                               patch_print,
                               session_post_fail,
                               test_urls,
                               assert_session_request_method_calls,
                               assert_print_calls,
                               connection_error):
    """
    POST request connection errors get printed and caught, the last exception
    is re-raised.
    """
    post = session_post_fail(patch_init_session.return_value, connection_error)

    test_urls("POST", connection_error)

    assert_session_request_method_calls(post)
    assert_print_calls(patch_print, connection_error)
