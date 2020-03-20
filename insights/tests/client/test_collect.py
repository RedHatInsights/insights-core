# -*- coding: UTF-8 -*-

from contextlib import contextmanager
from insights.client.client import collect
from insights.client.config import InsightsConfig
from insights.client.data_collector import DataCollector
from json import dump as json_dump, dumps as json_dumps
from mock.mock import Mock, patch
from pytest import mark, raises
from tempfile import NamedTemporaryFile
import six
import mock

stdin_uploader_json = {"some key": "some value"}
stdin_sig = "some signature"
stdin_payload = {"uploader.json": json_dumps(stdin_uploader_json), "sig": stdin_sig}
conf_remove_file = "/tmp/remove.conf"
removed_files = ["/etc/some_file", "/tmp/another_file"]


def collect_args(*insights_config_args, **insights_config_custom_kwargs):
    """
    Instantiates InsightsConfig with a default logging_file argument.
    """
    all_insights_config_kwargs = {"logging_file": "/tmp/insights.log", "remove_file": conf_remove_file}
    all_insights_config_kwargs.update(insights_config_custom_kwargs)
    return InsightsConfig(*insights_config_args, **all_insights_config_kwargs), Mock()


@contextmanager
def patch_temp_conf_file():
    """
    Creates a valid temporary config file.
    """
    collection_rules_file = NamedTemporaryFile("w+t")
    json_dump({"version": "1.2.3"}, collection_rules_file)
    collection_rules_file.seek(0)
    with patch("insights.client.collection_rules.constants.collection_rules_file", collection_rules_file.name):
        yield collection_rules_file
    collection_rules_file.close()


def temp_conf_file():
    """
    Creates a valid temporary config file.
    """
    collection_rules_file = NamedTemporaryFile()
    json_dump({"version": "1.2.3"}, collection_rules_file)
    collection_rules_file.seek(0)
    return collection_rules_file


def patch_get_branch_info():
    """
    Sets a static response to get_branch_info method.
    """
    def decorator(old_function):
        patcher = patch("insights.client.client.get_branch_info")
        return patcher(old_function)
    return decorator


def patch_get_conf_file():
    """
    Mocks InsightsUploadConf.get_conf_file so it returns a fixed configuration.
    """
    def decorator(old_function):
        patcher = patch("insights.client.client.InsightsUploadConf.get_conf_file")
        return patcher(old_function)
    return decorator


def patch_get_rm_conf():
    """
    Mocks InsightsUploadConf.get_rm_conf so it returns a fixed configuration.
    """
    def decorator(old_function):
        patcher = patch("insights.client.client.InsightsUploadConf.get_rm_conf")
        return patcher(old_function)
    return decorator


def patch_data_collector():
    """
    Replaces DataCollector with a dummy mock.
    """
    def decorator(old_function):
        patcher = patch("insights.client.client.DataCollector")
        return patcher(old_function)
    return decorator


def patch_isfile(remove_file_exists):
    """
    Mocks os.path.isfile so it always claims that a file exists. If it‘s a remove conf file, the result depends on the
    given value.
    """
    def decorator(old_function):
        def decider(*args, **kwargs):
            """
            Returns given value for remove_file and True for any other file.
            """
            if args[0] == conf_remove_file:
                return remove_file_exists
            else:
                return True

        patcher = patch("insights.client.collection_rules.os.path.isfile", decider)
        return patcher(old_function)

    return decorator


def patch_raw_config_parser():
    """
    Mocks RawConfigParser, so it returns a fixed configuration of removed files.
    """
    def decorator(old_function):
        files = ",".join(removed_files)
        patcher = patch("insights.client.collection_rules.ConfigParser.RawConfigParser",
                        **{"return_value.items.return_value": [("files", files)]})
        return patcher(old_function)
    return decorator


def patch_validate_gpg_sig(return_value):
    """
    Mocks the InsightsUploadConf.validate_gpg_sig method so it returns the given validation result.
    """
    def decorator(old_function):
        patcher = patch("insights.client.collection_rules.InsightsUploadConf.validate_gpg_sig",
                        return_value=return_value)
        return patcher(old_function)
    return decorator


def patch_try_disk(return_value):
    """
    Mocks the InsightsUploadConf.try_disk method so it returns the given parsed file contents.
    """
    def decorator(old_function):
        patcher = patch("insights.client.collection_rules.InsightsUploadConf.try_disk", return_value=return_value)
        return patcher(old_function)
    return decorator


@patch_data_collector()
@patch_get_conf_file()
# @patch_get_conf_stdin()
@patch_get_branch_info()
def test_get_conf_file(get_branch_info, get_conf_file, data_collector):
    """
    If there is no config passed via stdin, it is loaded from a file instead.
    """
    config, pconn = collect_args()
    collect(config, pconn)

    get_conf_file.assert_called_once_with()


@patch_data_collector()
@patch_get_rm_conf()
@patch_get_conf_file()
@patch_get_branch_info()
def test_get_rm_conf_file(get_branch_info, get_conf_file, get_rm_conf, data_collector):
    """
    Load configuration of files removed from collection when collection rules are loaded from a file.
    """
    config, pconn = collect_args()
    collect(config, pconn)

    get_rm_conf.assert_called_once_with()


@patch_data_collector()
@patch_get_rm_conf()
@patch_get_conf_file()
@patch_get_branch_info()
def test_data_collector_file(get_branch_info, get_conf_file, get_rm_conf, data_collector):
    """
    Configuration from a file is passed to the DataCollector along with removed files configuration.
    """
    config, pconn = collect_args()
    collect(config, pconn)

    collection_rules = get_conf_file.return_value
    rm_conf = get_rm_conf.return_value
    branch_info = get_branch_info.return_value
    data_collector.return_value.run_collection.assert_called_once_with(collection_rules, rm_conf, branch_info)
    data_collector.return_value.done.assert_called_once_with(collection_rules, rm_conf)


@patch_data_collector()
@patch_validate_gpg_sig(False)
@patch_isfile(False)
@patch_get_branch_info()
def test_file_signature_ignored(get_branch_info, validate_gpg_sig, data_collector):
    """
    Signature of configuration from a file is not validated if validation is disabled.
    """

    config, pconn = collect_args(gpg=False)
    with patch_temp_conf_file():
        collect(config, pconn)

    validate_gpg_sig.assert_not_called()


@mark.regression
@patch_data_collector()
@patch_validate_gpg_sig(True)
@patch_isfile(False)
# @patch_stdin()
@patch_get_branch_info()
def test_file_signature_valid(get_branch_info, validate_gpg_sig, data_collector):
    """
    Correct signature of configuration from a file is recognized.
    """
    config, pconn = collect_args()
    with patch_temp_conf_file():
        collect(config, pconn)

    validate_gpg_sig.assert_called_once()


@mark.regression
@patch_data_collector()
@patch_validate_gpg_sig(False)
@patch_isfile(False)
@patch_get_branch_info()
def test_file_signature_invalid(get_branch_info, validate_gpg_sig, data_collector):
    """
    Incorrect signature of configuration from a file skips that file.
    """
    config, pconn = collect_args()
    with patch_temp_conf_file():
        with raises(ValueError):
            collect(config, pconn)

    validate_gpg_sig.assert_called()


@mark.regression
@patch_data_collector()
@patch_raw_config_parser()
@patch_isfile(True)
@patch_try_disk({"version": "1.2.3"})
@patch_get_branch_info()
def test_file_result(get_branch_info, try_disk, raw_config_parser, data_collector):
    """
    Configuration from file is loaded from the "uploader.json" key.
    """
    if six.PY3:
        open_name = 'builtins.open'
    else:
        open_name = '__builtin__.open'

    with patch(open_name, create=True) as mock_open:
        mock_open.side_effect = [mock.mock_open(read_data='[remove]\nfiles=/etc/some_file,/tmp/another_file').return_value]

        config, pconn = collect_args()
        collect(config, pconn)

        name, args, kwargs = try_disk.mock_calls[0]
        collection_rules = try_disk.return_value.copy()
        collection_rules.update({"file": args[0]})

        rm_conf = {"files": removed_files}
        branch_info = get_branch_info.return_value

        data_collector.return_value.run_collection.assert_called_once_with(collection_rules, rm_conf, branch_info)
        data_collector.return_value.done.assert_called_once_with(collection_rules, rm_conf)


@mark.regression
@patch_data_collector()
@patch_try_disk({"value": "abc"})
@patch_get_branch_info()
def test_file_no_version(get_branch_info, try_disk, data_collector):
    """
    Configuration from file is loaded from the "uploader.json" key.
    """
    config, pconn = collect_args()
    with raises(ValueError):
        collect(config, pconn)

    data_collector.return_value.run_collection.assert_not_called()
    data_collector.return_value.done.assert_not_called()


@mark.regression
@patch_data_collector()
@patch_try_disk(None)
@patch_get_branch_info()
def test_file_no_data(get_branch_info, try_disk, data_collector):
    """
    Configuration from file is loaded from the "uploader.json" key.
    """
    config, pconn = collect_args()
    with raises(ValueError):
        collect(config, pconn)

    data_collector.return_value.run_collection.assert_not_called()
    data_collector.return_value.done.assert_not_called()


def test_cmd_blacklist():
    config, pconn = collect_args()
    dc = DataCollector(config)
    assert dc._blacklist_check('rm')
    assert dc._blacklist_check('reboot')
    assert dc._blacklist_check('kill')
    assert dc._blacklist_check('shutdown')
    assert dc._blacklist_check('echo ""; shutdown')
    assert dc._blacklist_check('/bin/bash -c "rm -rf /"')
    assert dc._blacklist_check('echo ""; /bin/bash -c "rm -rf /"; reboot')
