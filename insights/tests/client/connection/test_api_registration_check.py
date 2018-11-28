# -*- coding: UTF-8 -*-

from mock.mock import patch
from pytest import fixture


@fixture()
def patch_test_connection():
    """
    Patches the test_connection method so its call can be asserted.
    """
    with patch("insights.client.connection.InsightsConnection.test_connection") as test_connection:
        yield test_connection


def test_connection_timeout(patch_init_session,
                            patch_test_connection,
                            insights_connection,
                            session_get_fail,
                            timeout_error):
    """
    Request time-out is caught.
    """
    get = session_get_fail(patch_init_session.return_value, timeout_error)

    result = insights_connection().api_registration_check()
    assert result is False

    get.assert_called_once()
    patch_test_connection.assert_called_once()


def test_connection_error(patch_init_session,
                          patch_test_connection,
                          insights_connection,
                          session_get_fail,
                          connection_error):
    """
    Request connection error is caught.
    """
    get = session_get_fail(patch_init_session.return_value, connection_error)

    result = insights_connection().api_registration_check()
    assert result is False

    get.assert_called_once()
    patch_test_connection.assert_called_once()
