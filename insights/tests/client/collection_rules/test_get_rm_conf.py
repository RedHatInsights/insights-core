# -*- coding: UTF-8 -*-

from .helpers import insights_upload_conf
from mock.mock import patch


conf_remove_file = '/tmp/remove.conf'
removed_files = ["/etc/some_file", "/tmp/another_file"]


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


@patch_raw_config_parser([])
@patch_isfile(False)
def test_no_file(isfile, raw_config_parser):
    upload_conf = insights_upload_conf(remove_file=conf_remove_file)
    result = upload_conf.get_rm_conf()

    isfile.assert_called_once_with(conf_remove_file)
    raw_config_parser.assert_not_called()

    assert result is None


@patch_raw_config_parser([("files", ",".join(removed_files))])
@patch_isfile(True)
def test_return(isfile, raw_config_parser):
    upload_conf = insights_upload_conf(remove_file=conf_remove_file)
    result = upload_conf.get_rm_conf()

    isfile.assert_called_once_with(conf_remove_file)

    raw_config_parser.assert_called_once_with()
    raw_config_parser.return_value.read.assert_called_with(conf_remove_file)
    raw_config_parser.return_value.items.assert_called_with('remove')

    assert result == {"files": removed_files}
