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
import pytest

stdin_uploader_json = {"some key": "some value"}
stdin_sig = "some signature"
stdin_payload = {"uploader.json": json_dumps(stdin_uploader_json), "sig": stdin_sig}
conf_remove_file = "/tmp/remove.conf"
conf_file_redaction_file = "/tmp/file-redaction.yaml"
conf_file_content_redaction_file = "/tmp/file-content-redaction.yaml"
removed_files = ["/etc/some_file", "/tmp/another_file"]


def collect_args(*insights_config_args, **insights_config_custom_kwargs):
    """
    Instantiates InsightsConfig with a default logging_file argument.
    """
    all_insights_config_kwargs = {"logging_file": "/tmp/insights.log",
                                  "remove_file": conf_remove_file,
                                  "redaction_file": conf_file_redaction_file,
                                  "content_redaction_file": conf_file_content_redaction_file,
                                  "core_collect": False}
    all_insights_config_kwargs.update(insights_config_custom_kwargs)
    return InsightsConfig(*insights_config_args, **all_insights_config_kwargs)


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
            if args[0] in (conf_remove_file, conf_file_redaction_file, conf_file_content_redaction_file):
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
@patch_get_branch_info()
def test_get_conf_file(get_branch_info, get_conf_file, data_collector):
    """
    If there is no config passed via stdin, it is loaded from a file instead.
    """
    config = collect_args()
    collect(config)

    get_conf_file.assert_called_once_with()


@patch("insights.client.client.CoreCollector")
@patch_get_conf_file()
@patch_get_branch_info()
def test_get_conf_called_core_collection(get_branch_info, get_conf_file, core_collector):
    """
    Verify that uploader.json is NOT loaded when using core collection (from get_rm_conf function)
    """
    config = collect_args(core_collect=True)
    collect(config)
    get_conf_file.assert_not_called()


@patch_data_collector()
@patch_get_rm_conf()
@patch_get_conf_file()
@patch_get_branch_info()
def test_get_rm_conf_file(get_branch_info, get_conf_file, get_rm_conf, data_collector):
    """
    Load configuration of files removed from collection when collection rules are loaded from a file.
    """
    config = collect_args()
    collect(config)

    get_rm_conf.assert_called_once_with()


@patch("insights.client.client.InsightsUploadConf.create_report")
@patch_data_collector()
@patch_get_rm_conf()
@patch_get_conf_file()
@patch_get_branch_info()
def test_data_collector_file(get_branch_info, get_conf_file, get_rm_conf, data_collector, create_report):
    """
    Configuration from a file is passed to the DataCollector along with removed files configuration.
    """
    config = collect_args()
    collect(config)

    collection_rules = get_conf_file.return_value
    rm_conf = get_rm_conf.return_value
    branch_info = get_branch_info.return_value
    blacklist_report = create_report.return_value
    data_collector.return_value.run_collection.assert_called_once_with(collection_rules, rm_conf, branch_info, blacklist_report)
    data_collector.return_value.done.assert_called_once_with(collection_rules, rm_conf)


@patch("insights.client.client.InsightsUploadConf.create_report")
@patch("insights.client.client.CoreCollector")
@patch_get_rm_conf()
@patch_get_conf_file()
@patch_get_branch_info()
def test_core_collector_file(get_branch_info, get_conf_file, get_rm_conf, core_collector, create_report):
    """
    CoreCollector is loaded with rm_conf and a None value for collection_rules
    """
    config = collect_args(core_collect=True)
    collect(config)

    collection_rules = None
    rm_conf = get_rm_conf.return_value
    branch_info = get_branch_info.return_value
    blacklist_report = create_report.return_value
    core_collector.return_value.run_collection.assert_called_once_with(collection_rules, rm_conf, branch_info, blacklist_report)
    core_collector.return_value.done.assert_called_once_with(collection_rules, rm_conf)


@patch("insights.client.client.CoreCollector")
@patch("insights.client.client.DataCollector")
@patch("insights.client.client.InsightsUploadConf.create_report")
@patch_get_rm_conf()
@patch_get_conf_file()
@patch_get_branch_info()
def test_correct_collector_loaded(get_branch_info, get_conf_file, get_rm_conf, create_report, data_collector, core_collector):
    '''
    Verify that core collection is loaded for core_collect=True, and that
    classic collection is loaded for core_collect=False
    '''
    config = collect_args(core_collect=False)
    collect(config)

    data_collector.return_value.run_collection.assert_called()
    core_collector.return_value.run_collection.assert_not_called()

    # clear calls to test opposite condition
    data_collector.return_value.run_collection.reset_mock()
    core_collector.return_value.run_collection.reset_mock()

    config.core_collect = True
    collect(config)

    data_collector.return_value.run_collection.assert_not_called()
    core_collector.return_value.run_collection.assert_called()


@patch_data_collector()
@patch_validate_gpg_sig(False)
@patch_isfile(False)
@patch_get_branch_info()
def test_file_signature_ignored(get_branch_info, validate_gpg_sig, data_collector):
    """
    Signature of configuration from a file is not validated if validation is disabled.
    """

    config = collect_args(gpg=False)
    with patch_temp_conf_file():
        collect(config)

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
    config = collect_args()
    with patch_temp_conf_file():
        collect(config)

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
    config = collect_args()
    with patch_temp_conf_file():
        with raises(RuntimeError):
            collect(config)

    validate_gpg_sig.assert_called()


@pytest.mark.skip(reason="This test became too convoluted and will be useless when core collection launches.")
@mark.regression
@patch('insights.client.collection_rules.verify_permissions')
@patch_data_collector()
@patch_raw_config_parser()
@patch_isfile(True)
@patch_try_disk({"version": "1.2.3"})
@patch_get_branch_info()
def test_file_result(get_branch_info, try_disk, raw_config_parser, data_collector, verify_permissions):
    """
    Configuration from file is loaded from the "uploader.json" key.
    """
    if six.PY3:
        open_name = 'builtins.open'
    else:
        open_name = '__builtin__.open'

    with patch(open_name, create=True) as mock_open:
        mock_open.side_effect = [mock.mock_open(read_data='').return_value,
                                 mock.mock_open(read_data='').return_value,
                                 mock.mock_open(read_data='[remove]\nfiles=/etc/some_file,/tmp/another_file').return_value]
        raw_config_parser.side_effect = [Mock(sections=Mock(return_value=['remove']), items=Mock(return_value=[('files', '/etc/some_file,/tmp/another_file')]))]
        config = collect_args()
        collect(config)

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
    config = collect_args()
    with raises(ValueError):
        collect(config)

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
    config = collect_args()
    with raises(RuntimeError):
        collect(config)

    data_collector.return_value.run_collection.assert_not_called()
    data_collector.return_value.done.assert_not_called()


def test_cmd_blacklist():
    config = collect_args()
    dc = DataCollector(config)
    assert dc._blacklist_check('rm')
    assert dc._blacklist_check('reboot')
    assert dc._blacklist_check('kill')
    assert dc._blacklist_check('shutdown')
    assert dc._blacklist_check('echo ""; shutdown')
    assert dc._blacklist_check('/bin/bash -c "rm -rf /"')
    assert dc._blacklist_check('echo ""; /bin/bash -c "rm -rf /"; reboot')
