# -*- coding: UTF-8 -*-

from insights.client.client import collect
from insights.client.config import InsightsConfig
from json import dump as json_dump, dumps as json_dumps
from mock.mock import call, Mock, patch, PropertyMock
from pytest import raises
from tempfile import TemporaryFile


branch_info = Mock()
stdin_payload_uploader_json = json_dumps({"key": "value"})
stdin_payload = {"uploader.json": stdin_payload_uploader_json, "sig": "signature"}
remove_file = "/tmp/remove.conf"
collection_rules_file = "/tmp/collection_rules"
collection_fallback_file = "/tmp/collection_rules"


def collect_args(*insights_config_args, **insights_config_custom_kwargs):
    """
    Instantiates InsightsConfig with a default logging_file argument.
    """
    insights_config_all_kwargs = {"logging_file": "/tmp/insights.log"}
    insights_config_all_kwargs.update(insights_config_custom_kwargs)
    return InsightsConfig(*insights_config_args, **insights_config_all_kwargs), Mock()


def patch_get_branch_info():
    """
    Sets a static response to get_branch_info method.
    """
    def decorator(old_function):
        patcher = patch("insights.client.client.get_branch_info", return_value=branch_info)
        return patcher(old_function)
    return decorator


def patch_stdin():
    """
    Sets a static JSON data to stdin.
    """
    def decorator(old_function):
        stdin = TemporaryFile("w+t")
        json_dump(stdin_payload, stdin)
        stdin.seek(0)

        patcher = patch("insights.client.client.sys.stdin", new_callable=PropertyMock(return_value=stdin))
        return patcher(old_function)
    return decorator


def patch_isfile(isfile):
    """
    Makes isfile return the passed result.
    """
    def decorator(old_function):
        patcher = patch("insights.client.client.os.path.isfile", return_value=isfile)
        return patcher(old_function)
    return decorator


def patch_collection_remove_file():
    """
    Makes collection_remove_file contain a fixed path.
    """
    def decorator(old_function):
        patcher = patch("insights.client.client.constants.collection_remove_file", remove_file)
        return patcher(old_function)
    return decorator


def patch_raw_config_parser(items=[]):
    """
    Mocks RawConfigParser so it returns the passed items.
    """
    def decorator(old_function):
        patcher = patch("insights.client.collection_rules.ConfigParser.RawConfigParser",
                          **{"return_value.items.return_value": items})
        return patcher(old_function)
    return decorator


def patch_validate_gpg_sig(valid):
    """
    Makes validate_gpg_sig return the passed result.
    """
    def decorator(old_function):
        patcher = patch("insights.client.collection_rules.InsightsUploadConf.validate_gpg_sig", return_value=valid)
        return patcher(old_function)
    return decorator


def patch_collection_rules_file():
    """
    Makes collection_rules_file contain a fixed path.
    """
    def decorator(old_function):
        patcher = patch("insights.client.collection_rules.constants.collection_rules_file", "/tmp/collection_rules")
        return patcher(old_function)
    return decorator


def patch_collection_fallback_file():
    """
    Makes collection_fallback_file contain a fixed path.
    """
    def decorator(old_function):
        patcher = patch("insights.client.collection_rules.constants.collection_fallback_file", collection_fallback_file)
        return patcher(old_function)
    return decorator


def patch_try_disk(return_values):
    """
    Makes try_disk sequentially return the passed contents.
    """
    def decorator(old_function):
        patcher = patch("insights.client.collection_rules.InsightsUploadConf.try_disk", side_effect=return_values)
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


def patch_named_temporary_file():
    """
    Mocks NamedTemporaryFile so it sequentially builds rules objects. Adds these object to test function arguments.
    """
    def decorator(old_function):
        rules_fp = Mock()
        rules_fp.name = "rules name"
        sig_fp = Mock()
        sig_fp.name = "sig name"

        patcher = patch("insights.client.collection_rules.NamedTemporaryFile",
                        side_effect=[rules_fp, sig_fp],
                        rules_fp=rules_fp,
                        sig_fp=sig_fp)
        return patcher(old_function)
    return decorator


@patch_data_collector()
@patch_raw_config_parser()
@patch_collection_remove_file()
@patch_isfile(False)
@patch_stdin()
@patch_get_branch_info()
def test_remove_file_not_exists(get_branch_info, stdin, isfile, raw_config_parser, data_collector):
    config, pconn = collect_args(from_stdin=True, gpg=False)
    collect(config, pconn)

    isfile.assert_called_once_with(remove_file)
    raw_config_parser.assert_not_called()


@patch_data_collector()
@patch_raw_config_parser([])
@patch_collection_remove_file()
@patch_isfile(True)
@patch_stdin()
@patch_get_branch_info()
def test_remove_file_exists(get_branch_info, stdin, isfile, raw_config_parser, data_collector):
    config, pconn = collect_args(from_stdin=True, gpg=False)
    collect(config, pconn)

    isfile.assert_called_once_with(remove_file)
    raw_config_parser.assert_called_once_with()
    raw_config_parser.return_value.read.assert_called_once_with(remove_file)
    raw_config_parser.return_value.items.assert_called_once_with("remove")


@patch_data_collector()
@patch_stdin()
@patch_named_temporary_file()
@patch_get_branch_info()
def test_stdin_write_rules(get_branch_info, named_temporary_file, stdin, data_collector):
    config, pconn = collect_args(from_stdin=True, gpg=False)
    collect(config, pconn)

    calls = [call(delete=False),
             call.rules_fp.write(stdin_payload_uploader_json.encode("utf-8")),
             call.rules_fp.flush(),
             call(delete=False),
             call.sig_fp.write("signature".encode("utf-8")),
             call.sig_fp.flush()]
    named_temporary_file.assert_has_calls(calls)


@patch_data_collector()
@patch_validate_gpg_sig(True)
@patch_stdin()
@patch_named_temporary_file()
@patch_get_branch_info()
def test_validate_gpg_sig(get_branch_info, named_temporary_file, stdin, validate_gpg_sig, data_collector):
    config, pconn = collect_args(from_stdin=True, gpg=True)
    collect(config, pconn)

    validate_gpg_sig.assert_called_with(named_temporary_file.rules_fp.name, named_temporary_file.sig_fp.name)


@patch_try_disk([{}])
@patch_validate_gpg_sig(False)
@patch_stdin()
@patch_named_temporary_file()
@patch_get_branch_info()
def test_invalid_gpg(get_branch_info, named_temporary_file, stdin, validate_gpg_sig, try_disk):
    config, pconn = collect_args(from_stdin=True, gpg=True)

    with raises(Exception):
        collect(config, pconn)
    try_disk.assert_not_called()  # Ensure it’s not ValueError


@patch_data_collector()
@patch_try_disk([{"version": "1.2.3"}])
@patch_collection_rules_file()
@patch_stdin()
@patch_get_branch_info()
def test_collection_rules_file_conf_try_disk(get_branch_info, stdin, try_disk, data_collector):
    config, pconn = collect_args(gpg="perhaps")
    collect(config, pconn)
    try_disk.assert_called_once_with(collection_rules_file, "perhaps")


@patch_try_disk([{"version": None}])
@patch_stdin()
@patch_get_branch_info()
def test_collection_rules_file_conf_no_version_error(get_branch_info, stdin, try_disk):
    config, pconn = collect_args()
    with raises(ValueError):
        collect(config, pconn)


@patch_data_collector()
@patch_try_disk([None, {"version": "1.2.3"}])
@patch_collection_fallback_file()
@patch_collection_rules_file()
@patch_stdin()
@patch_get_branch_info()
def test_fallback_file_conf_try_disk(get_branch_info, stdin, try_disk, data_collector):
    config, pconn = collect_args(gpg="perhaps")
    collect(config, pconn)
    calls = [call(collection_rules_file, "perhaps"), call(collection_fallback_file, "perhaps")]
    try_disk.assert_has_calls(calls)
    assert try_disk.call_count == len(calls)


@patch_try_disk([None, {"version": None}])
@patch_stdin()
@patch_get_branch_info()
def test_fallback_file_conf_no_version_error(get_branch_info, stdin, try_disk):
    config, pconn = collect_args()
    with raises(ValueError):
        collect(config, pconn)


@patch_try_disk([None, None])
@patch_stdin()
@patch_get_branch_info()
def test_no_file_conf_error(get_branch_info, stdin, try_disk):
    config, pconn = collect_args()
    with raises(ValueError):
        collect(config, pconn)


@patch_data_collector()
@patch_try_disk([{"version": "1.2.3"}])
@patch_collection_rules_file()
@patch_isfile(False)
@patch_stdin()
@patch_get_branch_info()
def test_return_without_rm_conf(get_branch_info, stdin, isfile, try_disk, data_collector):
    config, pconn = collect_args()
    collect(config, pconn)

    collection_rules = {"version": "1.2.3", "file": collection_rules_file}
    rm_conf = None
    data_collector.return_value.run_collection.assert_called_once_with(collection_rules, rm_conf, branch_info)


@patch_data_collector()
@patch_try_disk([{"version": "1.2.3"}])
@patch_collection_rules_file()
@patch_raw_config_parser([("files", "/etc/remove.conf,/tmp/remove.conf")])
@patch_isfile(True)
@patch_stdin()
@patch_get_branch_info()
def test_return_with_rm_conf(get_branch_info, stdin, isfile, raw_config_parser, try_disk, data_collector):
    config, pconn = collect_args()
    collect(config, pconn)

    collection_rules = {"version": "1.2.3", "file": collection_rules_file}
    rm_conf = {"files": ["/etc/remove.conf", "/tmp/remove.conf"]}
    data_collector.return_value.run_collection.assert_called_once_with(collection_rules, rm_conf, branch_info)
