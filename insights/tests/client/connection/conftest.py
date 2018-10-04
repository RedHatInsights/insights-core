# -*- coding: UTF-8 -*-

from insights.client.connection import InsightsConnection
from mock.mock import Mock, patch
from pytest import fixture
from requests.exceptions import ConnectionError, ConnectTimeout, ReadTimeout


@fixture()
def patch_init_session():
    """
    Patches the _init_session method so the InsightsConnection is initialized
    with a mocked session.
    """
    with patch("insights.client.connection.InsightsConnection._init_session") as init_session:
        yield init_session


@fixture(params=[ConnectTimeout, ReadTimeout])
def timeout_error(request):
    """
    Parametrizes a test with the two possible time-out errors.
    """
    yield request.param


@fixture(params=[ConnectionError])
def connection_error(request):
    """
    Parametrizes a test with the connection error.
    """
    yield request.param


@fixture()
def insights_connection():
    """
    InsightsConnection factory with a mocked configuration.
    """
    def factory():
        config = Mock(api_url="www.example.com",
                      base_url="www.example.com",
                      proxy=None)
        return InsightsConnection(config)
    return factory


@fixture()
def session_get_fail():
    """
    Configures the session mock so it’s get method raises the given error.
    Returns the get method mock.
    """
    def patcher(session_mock, side_effect_error):
        get = session_mock.get
        get.side_effect = side_effect_error
        return get
    return patcher


@fixture()
def session_post_fail():
    """
    Configures the session mock so it’s post method raises the given error.
    Returns the get method mock.
    """
    def patcher(session_mock, side_effect_error):
        post = session_mock.post
        post.side_effect = side_effect_error
        return post
    return patcher
