# -*- coding: UTF-8 -*-

from insights.client.client import update_rules
from mock.mock import Mock, patch
from pytest import raises


def patch_insights_upload_conf():
    """
    Mocks InsightsUploadConf.
    """
    def decorator(old_function):
        patcher = patch("insights.client.client.InsightsUploadConf")
        return patcher(old_function)
    return decorator


@patch_insights_upload_conf()
def test_no_connection_error(insights_upload_conf):
    """
    Error is raised when connection couldn't be established.
    """
    config = Mock()
    with raises(ValueError):
        update_rules(config, None)

    insights_upload_conf.return_value.get_conf_update.assert_not_called()


@patch_insights_upload_conf()
def test_configuration(insights_upload_conf):
    """
    Configuration is created with given options and retrieved connection.
    """
    config = Mock()
    pconn = Mock()
    update_rules(config, pconn)

    insights_upload_conf.assert_called_once_with(config, conn=pconn)


@patch_insights_upload_conf()
def test_return_get_conf_update(insights_upload_conf):
    """
    Updated configuration is loaded and returned.
    """
    config = Mock()
    pconn = Mock()
    result = update_rules(config, pconn)

    get_conf_update = insights_upload_conf.return_value.get_conf_update
    get_conf_update.assert_called_once_with()
    assert result == get_conf_update.return_value
