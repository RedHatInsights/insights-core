# -*- coding: UTF-8 -*-

import os
import json
import six
import mock
import pytest
from .helpers import insights_upload_conf
from mock.mock import patch
from insights.client.collection_rules import InsightsUploadConf
from insights.client.config import InsightsConfig


conf_remove_file = '/tmp/remove.conf'
removed_files = ["/etc/some_file", "/tmp/another_file"]


def teardown_function(func):
    if func is test_raw_config_parser:
        if os.path.isfile(conf_remove_file):
            os.remove(conf_remove_file)


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


def patch_open(filedata):
    if six.PY3:
        open_name = 'builtins.open'
    else:
        open_name = '__builtin__.open'

    return patch(open_name, mock.mock_open(read_data=filedata), create=True)


@patch_raw_config_parser([])
@patch_isfile(False)
def test_no_file(isfile, raw_config_parser):
    upload_conf = insights_upload_conf(remove_file=conf_remove_file)
    result = upload_conf.get_rm_conf()

    isfile.assert_called_once_with(conf_remove_file)

    # no file, no call to open
    with patch_open('') as mock_open:
        mock_open.assert_not_called()

    assert result is None


@patch('insights.client.collection_rules.InsightsUploadConf.get_rm_conf_old')
@patch_isfile(True)
def test_return(isfile, get_rm_conf_old):
    '''
    Test that loading YAML from a file will return a dict
    '''
    filedata = '---\ncommands:\n- /bin/ls\n- ethtool_i'
    with patch_open(filedata):
        upload_conf = insights_upload_conf(remove_file=conf_remove_file)
        result = upload_conf.get_rm_conf()
    assert result == {'commands': ['/bin/ls', 'ethtool_i']}
    get_rm_conf_old.assert_not_called()


@patch('insights.client.collection_rules.InsightsUploadConf.get_rm_conf_old')
@patch_isfile(True)
def test_fallback_to_old(isfile, get_rm_conf_old):
    '''
    Test that the YAML function falls back to classic INI
    if the file cannot be parsed as YAML
    '''
    filedata = 'ncommands\n /badwain/ls\n- ethtool_i'
    with patch_open(filedata):
        upload_conf = insights_upload_conf(remove_file=conf_remove_file)
        upload_conf.get_rm_conf()
    get_rm_conf_old.assert_called_once()


@pytest.mark.skipif(mock.version_info < (3, 0, 5), reason="Old mock_open has no iteration control")
@patch_isfile(True)
def test_fallback_ini_data(isfile):
    '''
    Test that the YAML function falls back to classic INI
    if the file cannot be parsed as YAML, and the data is
    parsed as INI
    '''
    filedata = '[remove]\ncommands=/bin/ls,ethtool_i'
    with patch_open(filedata):
        upload_conf = insights_upload_conf(remove_file=conf_remove_file)
        result = upload_conf.get_rm_conf()
    assert result == {'commands': ['/bin/ls', 'ethtool_i']}


@pytest.mark.skipif(mock.version_info < (3, 0, 5), reason="Old mock_open has no iteration control")
@patch_isfile(True)
def test_fallback_bad_data(isfile):
    '''
    Test that the YAML function falls back to classic INI
    if the file cannot be parsed as YAML, and the data isn't
    INI either so it's thrown out
    '''
    filedata = 'ncommands\n /badwain/ls\n- ethtool_i'
    with patch_open(filedata):
        upload_conf = insights_upload_conf(remove_file=conf_remove_file)
        with pytest.raises(RuntimeError) as e:
            upload_conf.get_rm_conf()
    assert 'YAML file nor as an INI file' in str(e.value)


@patch_isfile(True)
def test_load_string_patterns(isfile):
    '''
    Test that the patterns section is loaded as a list of strings.
    '''
    filedata = '---\npatterns:\n- abcd\n- bcdef'
    with patch_open(filedata):
        upload_conf = insights_upload_conf(remove_file=conf_remove_file)
        result = upload_conf.get_rm_conf()
    assert 'patterns' in result
    assert isinstance(result['patterns'], list)


@patch_isfile(True)
def test_load_string_regex(isfile):
    '''
    Test that the patterns section is loaded as a dict with
    key 'regex' and the value is a list of strings
    '''
    filedata = '---\npatterns:\n  regex:\n  - abcd\n  - bcdef'
    with patch_open(filedata):
        upload_conf = insights_upload_conf(remove_file=conf_remove_file)
        result = upload_conf.get_rm_conf()
    assert 'patterns' in result
    assert isinstance(result['patterns'], dict)
    assert 'regex' in result['patterns']
    assert isinstance(result['patterns']['regex'], list)


@patch_raw_config_parser([("files", ",".join(removed_files))])
@patch_isfile(True)
def test_return_old(isfile, raw_config_parser):
    upload_conf = insights_upload_conf(remove_file=conf_remove_file)
    result = upload_conf.get_rm_conf_old()

    raw_config_parser.assert_called_once_with()
    raw_config_parser.return_value.read.assert_called_with(conf_remove_file)
    raw_config_parser.return_value.items.assert_called_with('remove')

    assert result == {"files": removed_files}


def test_raw_config_parser():
    '''
        Ensure that get_rm_conf and json.loads (used to load uploader.json) return the same filename
    '''
    raw_filename = '/etc/yum/pluginconf.d/()*\\\\w+\\\\.conf'
    uploader_snip = json.loads('{"pattern": [], "symbolic_name": "pluginconf_d", "file": "' + raw_filename + '"}')
    with open(conf_remove_file, 'w') as rm_conf:
        rm_conf.write('[remove]\nfiles=' + raw_filename)
    coll = InsightsUploadConf(InsightsConfig(remove_file=conf_remove_file))
    items = coll.get_rm_conf()
    assert items['files'][0] == uploader_snip['file']


@patch_isfile(True)
def test_config_verification_ok_validtypes(isfile):
    '''
    Verify that valid config is allowed when
    proper keys and lists of strings are specified
    '''
    # patterns w. list of strings
    filedata = '---\ncommands:\n- /bin/test\n- /bin/test2\nfiles:\n- /var/lib/aaa\n- /var/lib/nnn\npatterns:\n- abcd\n- bcdef\nkeywords:\n- example\n- example2'
    with patch_open(filedata):
        upload_conf = insights_upload_conf(remove_file=conf_remove_file)
        result = upload_conf.get_rm_conf()
    assert result

    # patterns w. regex object
    filedata = '---\ncommands:\n- /bin/test\n- /bin/test2\nfiles:\n- /var/lib/aaa\n- /var/lib/nnn\npatterns:\n  regex:\n  - abcd\n  - bcdef\nkeywords:\n- example\n- example2'
    with patch_open(filedata):
        upload_conf = insights_upload_conf(remove_file=conf_remove_file)
        result = upload_conf.get_rm_conf()
    assert result


@patch_isfile(True)
def test_config_verification_ok_emptyvalues(isfile):
    '''
    Verify that valid config is allowed when
    proper keys and empty (None) values are specified
    '''
    filedata = '---\ncommands:\n- some_symbolic_name\nfiles:\npatterns:\nkeywords:\n'
    with patch_open(filedata):
        upload_conf = insights_upload_conf(remove_file=conf_remove_file)
        result = upload_conf.get_rm_conf()
    assert result


@patch_isfile(True)
def test_config_verification_bad_invalidkeys(isfile):
    '''
    Verify that a config with invalid keys is not allowed
    '''
    filedata = '---\ncommands:\nfiles:\nsomekey:\n'
    with patch_open(filedata):
        upload_conf = insights_upload_conf(remove_file=conf_remove_file)
        with pytest.raises(RuntimeError) as e:
            upload_conf.get_rm_conf()
    assert 'Unknown section' in str(e.value)


@patch_isfile(True)
def test_config_verification_bad_invalidtypes(isfile):
    '''
    Verify that a config with valid keys,
    but invalid data types, is not allowed
    '''
    filedata = '---\ncommands: somestring\nfiles:\n- /var/lib/aaa\n- /var/lib/bbb\n'
    with patch_open(filedata):
        upload_conf = insights_upload_conf(remove_file=conf_remove_file)
        with pytest.raises(RuntimeError) as e:
            upload_conf.get_rm_conf()
    assert 'must be a list of strings' in str(e.value)


@patch_isfile(True)
def test_config_verification_bad_patterns_keysnoregex(isfile):
    '''
    Verify that a config with patterns, if a dict
    with a single key, only contains the key
    "regex"
    '''
    filedata = '---\npatterns:\n  wrongkey:\n  - a(bc)\n  - nextregex'
    with patch_open(filedata):
        upload_conf = insights_upload_conf(remove_file=conf_remove_file)
        with pytest.raises(RuntimeError) as e:
            upload_conf.get_rm_conf()
    assert 'contains an object but the "regex" key was not specified' in str(e.value)


@patch_isfile(True)
def test_config_verification_bad_patterns_invalidkey(isfile):
    '''
    Verify that a config with patterns, if a dict
    containing the key "regex", only contains the key "regex"
    '''
    filedata = '---\npatterns:\n  regex:\n  wrongkey:\n  - a(bc)\n  - nextregex'
    with patch_open(filedata):
        upload_conf = insights_upload_conf(remove_file=conf_remove_file)
        with pytest.raises(RuntimeError) as e:
            upload_conf.get_rm_conf()
    assert 'Only "regex" is valid' in str(e.value)


@patch_isfile(True)
def test_config_verification_bad_patterns_regexinvalidtype(isfile):
    '''
    Verify that if a regex key exists in the
    patterns section, that the value is a list
    of strings
    '''
    filedata = '---\npatterns:\n  regex: a(b)'
    with patch_open(filedata):
        upload_conf = insights_upload_conf(remove_file=conf_remove_file)
        with pytest.raises(RuntimeError) as e:
            upload_conf.get_rm_conf()
    assert 'regex section under patterns must be a list of strings' in str(e.value)


@patch_isfile(True)
def test_config_filtering(isfile):
    '''
    Verify that keys with None values
    do not appear in the final conf
    '''
    filedata = '---\npatterns:\nfiles:\n- /var/lib/aaa'
    with patch_open(filedata):
        upload_conf = insights_upload_conf(remove_file=conf_remove_file)
        result = upload_conf.get_rm_conf()
    assert 'patterns' not in result and 'files' in result
