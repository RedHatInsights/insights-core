# -*- coding: UTF-8 -*-

from insights.client.client import update_rules
from mock.mock import Mock, patch
from pytest import mark, raises

collection_rules_file = "/tmp/collection_rules"


def update_rules_args():
    """
    Mocks InsightsConfig with some values that allow instantiating InsightsUploadConf without errors.
    """
    return Mock(base_url=""), Mock


def coerce_result(result):
    """
    Coerces return value to a tuple if it returned only a single value.
    """
    if isinstance(result, tuple):
        return result
    else:
        return (result,)


def try_disk_call_file(mock):
    """
    Finds a filename what the try_disk method was called with.
    """
    name, args, kwargs = mock.mock_calls[0]
    return args[0]


def patch_insights_upload_conf():
    """
    Mocks InsightsUploadConf class.
    """
    def decorator(old_function):
        patcher = patch("insights.client.client.InsightsUploadConf")
        return patcher(old_function)
    return decorator


def patch_get_collection_rules(return_value):
    """
    Mocks InsightsUploadConf.get_collection_rules method so it returns a given value.
    """
    def decorator(old_function):
        patcher = patch("insights.client.client.InsightsUploadConf.get_collection_rules", return_value=return_value)
        return patcher(old_function)
    return decorator


def patch_try_disk(return_value):
    """
    Mocks InsightsUploadConf.try_disk method so it returns a given value.
    """
    def decorator(old_function):
        patcher = patch("insights.client.client.InsightsUploadConf.try_disk", return_value=return_value)
        return patcher(old_function)
    return decorator


def patch_collection_rules_file():
    """
    Mocks the collection_rules_file contant so it contains a fixed value.
    """
    def decorator(old_function):
        patcher = patch("insights.client.collection_rules.constants.collection_rules_file", collection_rules_file)
        return patcher(old_function)
    return decorator


@mark.regression
def test_no_connection_error():
    """
    Error is raised when connection couldn't be established.
    """
    config, pconn = update_rules_args()
    with raises(ValueError):
        update_rules(config, None)


@patch_insights_upload_conf()
def test_no_connection_no_configuration(insights_upload_conf):
    """
    Configuration is not loaded when connection couldn't be established.
    """
    config, pconn = update_rules_args()
    try:
        update_rules(config, None)
    except ValueError:
        pass

    insights_upload_conf.assert_not_called()


@patch_insights_upload_conf()
def test_configuration(insights_upload_conf):
    """
    Configuration is created with given options and retrieved connection.
    """
    config, pconn = update_rules_args()
    update_rules(config, pconn)

    insights_upload_conf.assert_called_once_with(config, conn=pconn)


@patch_insights_upload_conf()
def test_return_get_conf_update(insights_upload_conf):
    """
    Updated configuration is loaded and returned.
    """
    config, pconn = update_rules_args()
    result = update_rules(config, pconn)

    get_conf_update = insights_upload_conf.return_value.get_conf_update
    get_conf_update.assert_called_once_with()
    assert result == get_conf_update.return_value


@mark.regression
@patch_try_disk(None)
@patch_get_collection_rules({"version": "1.2.3"})
def test_get_collection_rules_calls(get_collection_rules, try_disk):
    """
    Collection rules are retrieved from online source, skipping loading from file.
    """
    config, pconn = update_rules_args()
    update_rules(config, pconn)

    get_collection_rules.assert_called_once_with()
    try_disk.assert_not_called()


@mark.regression
@patch_get_collection_rules({"value": "abc"})
def test_get_collection_rules_no_version_error(get_collection_rules):
    """
    An error is raised if collection rules retrieved from online source don’t contain a version.
    """
    config, pconn = update_rules_args()
    with raises(ValueError):
        update_rules(config, pconn)


@mark.regression
@patch_collection_rules_file()
@patch_get_collection_rules({"version": "1.2.3"})
def test_get_collection_rules_result(get_collection_rules):
    """
    Collection rules file name is added to the retrieved result.
    """
    config, pconn = update_rules_args()
    raw_result = update_rules(config, pconn)
    coerced_result = coerce_result(raw_result)

    expected = get_collection_rules.return_value.copy()
    expected.update({"file": collection_rules_file})
    assert coerced_result[0] == expected


@mark.regression
@patch_try_disk({"version": "1.2.3"})
@patch_get_collection_rules(None)
def test_try_disk_calls(get_collection_rules, try_disk):
    """
    Collection rules are not retrieved from online source, loading from file.
    """
    config, pconn = update_rules_args()
    update_rules(config, pconn)

    get_collection_rules.assert_called_once_with()
    try_disk.assert_called()


@mark.regression
@patch_try_disk({"value": "abc"})
@patch_get_collection_rules(None)
def test_try_disk_no_version_error(get_collection_rules, try_disk):
    """
    An error is raised if collection rules retrieved from file don’t contain a version.
    """
    config, pconn = update_rules_args()
    with raises(ValueError):
        update_rules(config, pconn)


@mark.regression
@patch_try_disk({"version": "1.2.3"})
@patch_get_collection_rules(None)
def test_try_disk_result(get_collection_rules, try_disk):
    """
    Local file name is added to the stored result.
    """
    config, pconn = update_rules_args()
    raw_result = update_rules(config, pconn)
    coerced_result = coerce_result(raw_result)

    name, args, kwargs = try_disk.mock_calls[0]
    expected = try_disk.return_value
    expected.update({"file": args[0]})
    assert coerced_result[0] == expected
