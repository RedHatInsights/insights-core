# -*- coding: UTF-8 -*-

from .helpers import insights_upload_conf
from mock.mock import patch


remove_file = '/etc/insights-client/remove.conf'
remove_files = ["/etc/remove.conf", "/tmp/remove.conf"]


def patch_isfile(isfile):
    """
    Makes isfile return the passed result.
    """
    def decorator(old_function):
        patcher = patch("insights.client.collection_rules.os.path.isfile", return_value=isfile)
        return patcher(old_function)
    return decorator


def patch_raw_config_parser(items):
    """
    Mocks RawConfigParser so it returns the passed items.
    """
    def decorator(old_function):
        patcher = patch("insights.client.collection_rules.ConfigParser.RawConfigParser",
                          **{"return_value.items.return_value": items})
        return patcher(old_function)
    return decorator


def patch_collection_remove_file():
    """
    Mocks InsightsConstants collection_remove_file so it contains a fixed value.
    """
    def decorator(old_function):
        patcher = patch("insights.client.collection_rules.constants.collection_remove_file", remove_file)
        return patcher(old_function)
    return decorator


@patch_isfile(False)
@patch_raw_config_parser([])
def test_no_file(raw_config_parser, isfile):
    upload_conf = insights_upload_conf()
    result = upload_conf.get_rm_conf()

    isfile.assert_called_once_with(remove_file)
    raw_config_parser.assert_not_called()

    assert result is None


@patch_collection_remove_file()
@patch_raw_config_parser([("files", ",".join(remove_files))])
@patch_isfile(True)
def test_return(isfile, raw_config_parser):
    upload_conf = insights_upload_conf()
    result = upload_conf.get_rm_conf()

    isfile.assert_called_once_with(remove_file)

    raw_config_parser.assert_called_once_with()
    raw_config_parser.return_value.read.assert_called_with(remove_file)
    raw_config_parser.return_value.items.assert_called_with('remove')

    assert result == {"files": remove_files}
