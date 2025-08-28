# -*- coding: UTF-8 -*-

import six
import mock
import pytest
from .helpers import insights_upload_conf
from mock.mock import patch, Mock, call
from insights.client.collection_rules import correct_format, load_yaml, verify_permissions


conf_remove_file = '/tmp/remove.conf'
conf_file_redaction_file = '/tmp/file-redaction.yaml'
conf_file_content_redaction_file = '/tmp/file-content-redaction.yaml'
removed_files = ["/etc/some_file", "/tmp/another_file"]


def patch_open(filedata):
    if six.PY3:
        open_name = 'builtins.open'
    else:
        open_name = '__builtin__.open'

    return patch(open_name, mock.mock_open(read_data=filedata), create=True)


# Tests for the correct_format function
def test_correct_format_ok_validtypes():
    '''
    Verify that valid config is allowed when
    proper keys and lists of strings are specified
    '''
    # files and commands (file-redaction.yaml)
    parsed_data = {
        'commands': ['/bin/test', '/bin/test2'],
        'files': ['/var/lib/aaa', '/var/lib/nnn'],
    }
    expected_keys = ('commands', 'files')
    err, msg = correct_format(parsed_data, expected_keys, conf_file_redaction_file)
    assert not err
    assert msg is None

    # patterns w. list of strings (file-content-redaction.yaml)
    parsed_data = {'patterns': ['abcd', 'bcdef'], 'keywords': ['example', 'example2']}
    expected_keys = ('patterns', 'keywords')
    err, msg = correct_format(parsed_data, expected_keys, conf_file_content_redaction_file)
    assert not err
    assert msg is None

    # patterns w. regex object (file-content-redaction.yaml)
    parsed_data = {'patterns': {'regex': ['abcd', 'bcdef']}, 'keywords': ['example', 'example2']}
    expected_keys = ('patterns', 'keywords')
    err, msg = correct_format(parsed_data, expected_keys, conf_file_content_redaction_file)
    assert not err
    assert msg is None


def test_config_verification_ok_emptyvalues():
    '''
    Verify that valid config is allowed when
    proper keys and empty (None) values are specified
    '''
    parsed_data = {'patterns': None, 'keywords': ['abc', 'def']}
    expected_keys = ('patterns', 'keywords')
    err, msg = correct_format(parsed_data, expected_keys, conf_file_content_redaction_file)
    assert not err
    assert msg is None


def test_config_verification_bad_invalidkeys():
    '''
    Verify that a config with invalid keys is not allowed
    '''
    parsed_data = {'commands': None, 'files': None, 'somekey': None}
    expected_keys = ('commands', 'files')
    err, msg = correct_format(parsed_data, expected_keys, conf_file_redaction_file)
    assert err
    assert 'Unknown section' in msg


def test_correct_format_bad_keys_in_wrong_file():
    '''
    Verify that an otherwise valid key is not
    specified in the wrong file (i.e. patterns
    in file-redaction.yaml)
    '''
    parsed_data = {'files': ['/etc/example'], 'patterns': ['abc', 'def']}
    expected_keys = ('files', 'commands')
    err, msg = correct_format(parsed_data, expected_keys, conf_file_redaction_file)
    assert err
    assert 'Unknown section(s) in ' + conf_file_redaction_file in msg


def test_correct_format_bad_invalidtypes():
    '''
    Verify that a config with valid keys,
    but invalid data types, is not allowed
    '''
    parsed_data = {'commands': 'somestring', 'files': ['/var/lib/aaa', '/var/lib/bbb']}
    expected_keys = ('commands', 'files')
    err, msg = correct_format(parsed_data, expected_keys, conf_file_redaction_file)
    assert err
    assert 'must be a list of strings' in msg


def test_correct_format_bad_patterns_keysnoregex():
    '''
    Verify that a config with patterns, if a dict
    with a single key, only contains the key
    "regex"
    '''
    parsed_data = {'patterns': {'wrongkey': ['a(bc)', 'nextregex']}}
    expected_keys = ('patterns', 'keywords')
    err, msg = correct_format(parsed_data, expected_keys, conf_file_content_redaction_file)
    assert err
    assert 'contains an object but the "regex" key was not specified' in msg


def test_correct_format_bad_patterns_invalidkey():
    '''
    Verify that a config with patterns, if a dict
    containing the key "regex", only contains the key "regex"
    '''
    parsed_data = {'patterns': {'regex': [], 'wrongkey': ['a(bc)', 'nextregex']}}
    expected_keys = ('patterns', 'keywords')
    err, msg = correct_format(parsed_data, expected_keys, conf_file_content_redaction_file)
    assert err
    assert 'Only "regex" is valid' in msg


def test_correct_format_bad_patterns_regexinvalidtype():
    '''
    Verify that if a regex key exists in the
    patterns section, that the value is a list
    of strings
    '''
    parsed_data = {'patterns': {'regex': 'a(b)'}}
    expected_keys = ('patterns', 'keywords')
    err, msg = correct_format(parsed_data, expected_keys, conf_file_content_redaction_file)
    assert err
    assert 'regex section under patterns must be a list of strings' in msg


def test_load_yaml_ok():
    '''
    Verify that proper YAML is parsed correctly
    '''
    yaml_data = '---\ncommands:\n- /bin/abc/def\n- /bin/ghi/jkl\nfiles:\n- /etc/abc/def.conf\n'
    with patch_open(yaml_data):
        result = load_yaml('test')
    assert result


def test_load_yaml_error():
    '''
    Verify that improper YAML raises an error
    '''
    yaml_data = '---\ncommands: files:\n- /etc/abc/def.conf\n'
    with patch_open(yaml_data):
        with pytest.raises(RuntimeError) as e:
            result = load_yaml('test')
            assert not result
    assert 'Cannot parse' in str(e.value)


def test_load_yaml_inline_tokens_in_regex_quotes():
    '''
    Verify that, if specifying a regex containing tokens parseable
    by YAML (such as []), when wrapped in quotation marks,
    the regex is parsed properly.
    '''
    yaml_data = '---\npatterns:\n  regex:\n  - \"[[:digit:]]*\"\n'
    with patch_open(yaml_data):
        result = load_yaml('test')
    assert result


def test_load_yaml_inline_tokens_in_regex_noquotes():
    '''
    Verify that, if specifying a regex containing tokens parseable
    by YAML (such as []), when not wrapped in quotation marks,
    an error is raised.
    '''
    yaml_data = '---\npatterns:\n  regex:\n  - [[:digit:]]*\n'
    with patch_open(yaml_data):
        with pytest.raises(RuntimeError) as e:
            result = load_yaml('test')
            assert not result
    assert 'Cannot parse' in str(e.value)


@patch('insights.client.collection_rules.stat.S_IMODE', return_value=0o600)
@patch('insights.client.collection_rules.os.stat', return_value=Mock(st_mode=1))
def test_verify_permissions_ok(os_stat, s_imode):
    '''
    Verify that file permissions 600 does not raise an error
    '''
    verify_permissions('test')


@patch('insights.client.collection_rules.stat.S_IMODE', return_value=0o644)
@patch('insights.client.collection_rules.os.stat', return_value=Mock(st_mode=1))
def test_verify_permissions_bad(os_stat, s_imode):
    '''
    Verify that file permissions 600 does not raise an error
    '''
    with pytest.raises(RuntimeError) as e:
        verify_permissions('test')
    assert 'Invalid permissions' in str(e.value)


# @patch_isfile(True)
# def test_config_filtering(isfile):
#     '''
#     Verify that keys with None values
#     do not appear in the final conf
#     '''
#     filedata = '---\npatterns:\nfiles:\n- /var/lib/aaa'
#     with patch_open(filedata):
#         upload_conf = insights_upload_conf(remove_file=conf_remove_file)
#         result = upload_conf.get_rm_conf()
#     assert 'patterns' not in result and 'files' in result


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
        patcher = patch(
            "insights.client.collection_rules.ConfigParser.RawConfigParser",
            **{"return_value.items.return_value": items}
        )
        return patcher(old_function)

    return decorator


@patch_isfile(False)
def test_rm_conf_old_nofile(isfile):
    '''
    Ensure an empty blacklist is generated when the file
    remove.conf does not exist.
    '''
    upload_conf = insights_upload_conf(remove_file=conf_remove_file)
    result = upload_conf.get_rm_conf_old()

    isfile.assert_called_once_with(conf_remove_file)

    # no file, no call to open
    with patch_open('') as mock_open:
        mock_open.assert_not_called()

    assert result is None


@pytest.mark.skipif(mock.version_info < (3, 0, 5), reason="Old mock_open has no iteration control")
@patch('insights.client.collection_rules.verify_permissions', return_value=True)
@patch_isfile(True)
def test_rm_conf_old_emptyfile(isfile, verify):
    '''
    Ensure an empty blacklist is generated when the old
    remove.conf exists, but is empty.
    '''
    filedata = ''
    with patch_open(filedata):
        upload_conf = insights_upload_conf(remove_file=conf_remove_file)
        result = upload_conf.get_rm_conf_old()
    assert result is None


@pytest.mark.skipif(mock.version_info < (3, 0, 5), reason="Old mock_open has no iteration control")
@patch('insights.client.collection_rules.verify_permissions', return_value=True)
@patch_isfile(True)
def test_rm_conf_old_load_bad_invalidsection(isfile, verify):
    '''
    Ensure an error is raised when an invalid
    section is defined in the old remove.conf
    '''
    filedata = '[wrong]\ncommands=/bin/abc'
    with patch_open(filedata):
        upload_conf = insights_upload_conf(remove_file=conf_remove_file)
        with pytest.raises(RuntimeError) as e:
            upload_conf.get_rm_conf_old()
    assert 'ERROR: invalid section(s)' in str(e.value)


@pytest.mark.skipif(mock.version_info < (3, 0, 5), reason="Old mock_open has no iteration control")
@patch('insights.client.collection_rules.verify_permissions', return_value=True)
@patch_isfile(True)
def test_rm_conf_old_load_bad_keysnosection(isfile, verify):
    '''
    Ensure an error is raised when keys are defined without
    a section in the old remove.conf
    '''
    filedata = 'commands=/bin/abc\nfiles=/etc/def'
    with patch_open(filedata):
        upload_conf = insights_upload_conf(remove_file=conf_remove_file)
        with pytest.raises(RuntimeError) as e:
            upload_conf.get_rm_conf_old()
    assert 'ERROR: Cannot parse' in str(e.value)


@pytest.mark.skipif(mock.version_info < (3, 0, 5), reason="Old mock_open has no iteration control")
@patch('insights.client.collection_rules.verify_permissions', return_value=True)
@patch_isfile(True)
def test_rm_conf_old_load_bad_invalidkey(isfile, verify):
    '''
    Ensure an error is raised when an invalid key is defined
    '''
    filedata = '[remove]\ncommands=/bin/abc\nbooradley=/etc/def'
    with patch_open(filedata):
        upload_conf = insights_upload_conf(remove_file=conf_remove_file)
        with pytest.raises(RuntimeError) as e:
            upload_conf.get_rm_conf_old()
    assert 'ERROR: Unknown key' in str(e.value)


@pytest.mark.skipif(mock.version_info < (3, 0, 5), reason="Old mock_open has no iteration control")
@patch('insights.client.collection_rules.verify_permissions', return_value=True)
@patch_isfile(True)
def test_rm_conf_old_load_ok(isfile, verify):
    '''
    Ensure that the old rm_conf load works
    with valid data.
    '''
    filedata = '[remove]\ncommands=/bin/ls,ethtool_i\nfiles=/etc/test\npatterns=abc123,def456\nkeywords=key1,key2,key3'
    with patch_open(filedata):
        upload_conf = insights_upload_conf(remove_file=conf_remove_file)
        result = upload_conf.get_rm_conf_old()
    assert result["commands"] == ["/bin/ls", "ethtool_i"]
    assert result["files"] == ["/etc/test"]
    assert result["patterns"] == ["abc123", "def456"]
    assert result["keywords"] == ["key1", "key2", "key3"]


@patch(
    'insights.client.collection_rules.InsightsUploadConf.load_redaction_file',
    return_value={"files": "/etc/insights-client/machine-id"},
)
@patch("insights.client.collection_rules.logger.warning")
def test_rm_conf_skipped_machine_id_files(warning, config):
    '''
    Verify that '/etc/insights-client/machine-id' is set in file-redaction.yaml[files]
    '''
    upload_conf = insights_upload_conf()
    upload_conf.get_rm_conf()
    warning.assert_called_once_with(
        "WARNING: Spec %s will be skipped for redaction; as it would cause issues, please remove it from %s.",
        "machine_id",
        "/etc/insights-client/file-redaction.yaml",
    )


@patch(
    'insights.client.collection_rules.InsightsUploadConf.load_redaction_file',
    return_value={"files": "machine_id"},
)
@patch("insights.client.collection_rules.logger.warning")
def test_rm_conf_skipped_machine_id_files_symname(warning, config):
    '''
    Verify that 'machine_id' is set in file-redaction.yaml[files]
    '''
    upload_conf = insights_upload_conf()
    upload_conf.get_rm_conf()
    warning.assert_called_once_with(
        "WARNING: Spec %s will be skipped for redaction; as it would cause issues, please remove it from %s.",
        "machine_id",
        "/etc/insights-client/file-redaction.yaml",
    )


@patch(
    'insights.client.collection_rules.InsightsUploadConf.load_redaction_file',
    return_value={"components": "insights.specs.default.DefaultSpecs.machine_id"},
)
@patch("insights.client.collection_rules.logger.warning")
def test_rm_conf_skipped_machine_id_components(warning, config):
    '''
    Verify that 'insights.specs.default.DefaultSpecs.machine_id' is set in file-redaction.yaml[components]
    '''
    upload_conf = insights_upload_conf()
    upload_conf.get_rm_conf()
    warning.assert_called_once_with(
        "WARNING: Spec %s will be skipped for redaction; as it would cause issues, please remove it from %s.",
        "machine_id",
        "/etc/insights-client/file-redaction.yaml",
    )


@patch(
    'insights.client.collection_rules.InsightsUploadConf.load_redaction_file',
    return_value={"commands": "/usr/sbin/subscription-manager identity"},
)
@patch("insights.client.collection_rules.logger.warning")
def test_rm_conf_skipped_subman_id_commands(warning, config):
    '''
    Verify that '/usr/sbin/subscription-manager identity' is set in file-redaction.yaml[commands]
    '''
    upload_conf = insights_upload_conf()
    upload_conf.get_rm_conf()
    warning.assert_called_once_with(
        "WARNING: Spec %s will be skipped for redaction; as it would cause issues, please remove it from %s.",
        "subscription_manager_id",
        "/etc/insights-client/file-redaction.yaml",
    )


@patch(
    'insights.client.collection_rules.InsightsUploadConf.load_redaction_file',
    return_value={"commands": "subscription_manager_id"},
)
@patch("insights.client.collection_rules.logger.warning")
def test_rm_conf_skipped_subman_id_commands_symname(warning, config):
    '''
    Verify that 'subscription_manager_id' is set in file-redaction.yaml[commands]
    '''
    upload_conf = insights_upload_conf()
    upload_conf.get_rm_conf()
    warning.assert_called_once_with(
        "WARNING: Spec %s will be skipped for redaction; as it would cause issues, please remove it from %s.",
        "subscription_manager_id",
        "/etc/insights-client/file-redaction.yaml",
    )


@patch(
    'insights.client.collection_rules.InsightsUploadConf.load_redaction_file',
    return_value={"components": "insights.specs.default.DefaultSpecs.subscription_manager_id"},
)
@patch("insights.client.collection_rules.logger.warning")
def test_rm_conf_skipped_subman_id_components(warning, config):
    '''
    Verify that 'insights.specs.default.DefaultSpecs.subscription_manager_id' is set in file-redaction.yaml[components]
    '''
    upload_conf = insights_upload_conf()
    upload_conf.get_rm_conf()
    warning.assert_called_once_with(
        "WARNING: Spec %s will be skipped for redaction; as it would cause issues, please remove it from %s.",
        "subscription_manager_id",
        "/etc/insights-client/file-redaction.yaml",
    )


@patch(
    'insights.client.collection_rules.InsightsUploadConf.load_redaction_file',
    return_value={"commands": "/usr/sbin/subscription-manager identity", "files": "machine_id"},
)
@patch("insights.client.collection_rules.logger.warning")
def test_rm_conf_skipped_both_id(warning, config):
    '''
    Verify that 'insights.specs.default.DefaultSpecs.subscription_manager_id' is set in file-redaction.yaml[components]
    and 'machine_id' is set in file-redaction.yaml[files]
    '''
    upload_conf = insights_upload_conf()
    upload_conf.get_rm_conf()
    calls = [
        call(
            "WARNING: Spec %s will be skipped for redaction; as it would cause issues, please remove it from %s.",
            "machine_id",
            "/etc/insights-client/file-redaction.yaml",
        ),
        call(
            "WARNING: Spec %s will be skipped for redaction; as it would cause issues, please remove it from %s.",
            "subscription_manager_id",
            "/etc/insights-client/file-redaction.yaml",
        ),
    ]
    warning.assert_has_calls(calls, any_order=True)


# @patch('insights.client.collection_rules.verify_permissions', return_value=True)
# @patch_isfile(True)
# def test_rm_conf_old_load_bad(isfile, verify):
#     '''
#     Ensure that the old rm_conf load rejects
#     invalid data.
#     '''
#     filedata = '[remove]\ncommands=/bin/ls,ethtool_i\nfiles=/etc/test\npatterns=abc123,def456\nkeywords=key1,key2,key3'
#     with patch_open(filedata):
#         upload_conf = insights_upload_conf(remove_file=conf_remove_file)
#         result = upload_conf.get_rm_conf_old()
#     assert result == {'commands': ['/bin/ls', 'ethtool_i'], 'files': ['/etc/test'], 'patterns': ['abc123', 'def456'], 'keywords': ['key1', 'key2', 'key3']}


# @patch('insights.client.collection_rules.InsightsUploadConf.get_rm_conf_old')
# @patch_isfile(True)
# def test_return(isfile, get_rm_conf_old):
#     '''
#     Test that loading YAML from a file will return a dict
#     '''
#     filedata = '---\ncommands:\n- /bin/ls\n- ethtool_i'
#     with patch_open(filedata):
#         upload_conf = insights_upload_conf(remove_file=conf_remove_file)
#         result = upload_conf.get_rm_conf()
#     assert result == {'commands': ['/bin/ls', 'ethtool_i']}
#     get_rm_conf_old.assert_not_called()


# @patch('insights.client.collection_rules.InsightsUploadConf.get_rm_conf_old')
# @patch_isfile(True)
# def test_fallback_to_old(isfile, get_rm_conf_old):
#     '''
#     Test that the YAML function falls back to classic INI
#     if the file cannot be parsed as YAML
#     '''
#     filedata = 'ncommands\n /badwain/ls\n- ethtool_i'
#     with patch_open(filedata):
#         upload_conf = insights_upload_conf(remove_file=conf_remove_file)
#         upload_conf.get_rm_conf()
#     get_rm_conf_old.assert_called_once()


# @pytest.mark.skipif(mock.version_info < (3, 0, 5), reason="Old mock_open has no iteration control")
# @patch_isfile(True)
# def test_fallback_ini_data(isfile):
#     '''
#     Test that the YAML function falls back to classic INI
#     if the file cannot be parsed as YAML, and the data is
#     parsed as INI
#     '''
#     filedata = '[remove]\ncommands=/bin/ls,ethtool_i'
#     with patch_open(filedata):
#         upload_conf = insights_upload_conf(remove_file=conf_remove_file)
#         result = upload_conf.get_rm_conf()
#     assert result == {'commands': ['/bin/ls', 'ethtool_i']}


# @pytest.mark.skipif(mock.version_info < (3, 0, 5), reason="Old mock_open has no iteration control")
# @patch_isfile(True)
# def test_fallback_bad_data(isfile):
#     '''
#     Test that the YAML function falls back to classic INI
#     if the file cannot be parsed as YAML, and the data isn't
#     INI either so it's thrown out
#     '''
#     filedata = 'ncommands\n /badwain/ls\n- ethtool_i'
#     with patch_open(filedata):
#         upload_conf = insights_upload_conf(remove_file=conf_remove_file)
#         with pytest.raises(RuntimeError) as e:
#             upload_conf.get_rm_conf()
#     assert 'YAML file nor as an INI file' in str(e.value)


# @patch_isfile(True)
# def test_load_string_patterns(isfile):
#     '''
#     Test that the patterns section is loaded as a list of strings.
#     '''
#     filedata = '---\npatterns:\n- abcd\n- bcdef'
#     with patch_open(filedata):
#         upload_conf = insights_upload_conf(remove_file=conf_remove_file)
#         result = upload_conf.get_rm_conf()
#     assert 'patterns' in result
#     assert isinstance(result['patterns'], list)


# @patch_isfile(True)
# def test_load_string_regex(isfile):
#     '''
#     Test that the patterns section is loaded as a dict with
#     key 'regex' and the value is a list of strings
#     '''
#     filedata = '---\npatterns:\n  regex:\n  - abcd\n  - bcdef'
#     with patch_open(filedata):
#         upload_conf = insights_upload_conf(remove_file=conf_remove_file)
#         result = upload_conf.get_rm_conf()
#     assert 'patterns' in result
#     assert isinstance(result['patterns'], dict)
#     assert 'regex' in result['patterns']
#     assert isinstance(result['patterns']['regex'], list)


# @patch_raw_config_parser([("files", ",".join(removed_files))])
# @patch_isfile(True)
# def test_return_old(isfile, raw_config_parser):
#     upload_conf = insights_upload_conf(remove_file=conf_remove_file)
#     result = upload_conf.get_rm_conf_old()

#     raw_config_parser.assert_called_once_with()
#     raw_config_parser.return_value.read.assert_called_with(conf_remove_file)
#     raw_config_parser.return_value.items.assert_called_with('remove')

#     assert result == {"files": removed_files}


# def test_raw_config_parser():
#     '''
#         Ensure that get_rm_conf and json.loads (used to load uploader.json) return the same filename
#     '''
#     raw_filename = '/etc/yum/pluginconf.d/()*\\\\w+\\\\.conf'
#     uploader_snip = json.loads('{"pattern": [], "symbolic_name": "pluginconf_d", "file": "' + raw_filename + '"}')
#     with open(conf_remove_file, 'w') as rm_conf:
#         rm_conf.write('[remove]\nfiles=' + raw_filename)
#     coll = InsightsUploadConf(InsightsConfig(remove_file=conf_remove_file))
#     items = coll.get_rm_conf()
#     assert items['files'][0] == uploader_snip['file']


# @patch_isfile(True)
# def test_config_filtering(isfile):
#     '''
#     Verify that keys with None values
#     do not appear in the final conf
#     '''
#     filedata = '---\npatterns:\nfiles:\n- /var/lib/aaa'
#     with patch_open(filedata):
#         upload_conf = insights_upload_conf(remove_file=conf_remove_file)
#         result = upload_conf.get_rm_conf()
#     assert 'patterns' not in result and 'files' in result
