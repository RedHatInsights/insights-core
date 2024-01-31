from insights.client.config import InsightsConfig
from insights.client.archive import InsightsArchive
from insights.client.data_collector import DataCollector
from insights.client.core_collector import CoreCollector
from mock.mock import patch, Mock
import pytest
import os
import six

test_file_data = 'test\nabcd\n1234\npassword: p4ssw0rd\n'


@patch('insights.client.archive.InsightsArchive', Mock())
@patch('insights.client.insights_spec.InsightsCommand', Mock())
@patch('insights.client.insights_spec.InsightsFile', Mock())
@patch('insights.client.data_collector.DataCollector._parse_command_spec', Mock())
@patch('insights.client.data_collector.DataCollector._parse_file_spec', Mock())
@patch('insights.client.data_collector.DataCollector._parse_glob_spec', Mock())
@patch('insights.client.data_collector.DataCollector.redact')
def test_redact_called_classic(redact):
    '''
    Verify that redact is always called during classic collection
    '''
    conf = InsightsConfig()
    upload_conf = {'commands': [], 'files': [], 'globs': []}
    rm_conf = {'test': 'test'}
    branch_info = {'test1': 'test2'}
    blacklist_report = {'test3': 'test4'}
    dc = DataCollector(conf)
    dc.run_collection(upload_conf, rm_conf, branch_info, blacklist_report)
    redact.assert_called_once_with(rm_conf)


@patch('insights.client.archive.InsightsArchive', Mock())
@patch('insights.client.core_collector.CoreCollector._write_branch_info', Mock())
@patch('insights.client.core_collector.CoreCollector._write_display_name', Mock())
@patch('insights.client.core_collector.CoreCollector._write_version_info', Mock())
@patch('insights.client.core_collector.CoreCollector._write_tags', Mock())
@patch('insights.client.core_collector.CoreCollector._write_blacklist_report', Mock())
@patch('insights.client.core_collector.collect.collect', Mock(return_value=('/var/tmp/testarchive/insights-test', {})))
@patch('insights.client.core_collector.CoreCollector.redact')
def test_redact_called_core(redact):
    '''
    Verify that redact is always called during core collection
    '''
    conf = InsightsConfig(core_collect=True)
    upload_conf = None
    rm_conf = {'test': 'test'}
    branch_info = {'test1': 'test2'}
    blacklist_report = {'test3': 'test4'}
    dc = CoreCollector(conf)
    dc.run_collection(upload_conf, rm_conf, branch_info, blacklist_report)
    redact.assert_called_once_with(rm_conf)


@patch('insights.client.data_collector.os.walk')
def test_redact_call_walk(walk):
    '''
    Verify that redact() calls os.walk and when an
    an archive structure is present in /var/tmp/**/insights-*
    '''
    conf = InsightsConfig(core_collect=False)
    arch = InsightsArchive(conf)
    arch.create_archive_dir()

    dc = DataCollector(conf, arch)
    rm_conf = {'patterns': ['test']}

    dc.redact(rm_conf)
    walk.assert_called_once_with(arch.archive_dir)


@patch('insights.client.data_collector.os.walk')
@patch('insights.client.data_collector.os.path.isdir', Mock(return_value=True))
def test_redact_call_walk_core(walk):
    '''
    Verify that redact() calls os.walk and when an
    an archive structure is present in /var/tmp/**/insights-*
    With core collection, /data is added to the path
    '''
    conf = InsightsConfig(core_collect=True)
    arch = InsightsArchive(conf)
    arch.create_archive_dir()

    dc = DataCollector(conf, arch)
    rm_conf = {'patterns': ['test']}

    dc.redact(rm_conf)
    walk.assert_called_once_with(os.path.join(arch.archive_dir, 'data'))


@patch('insights.client.data_collector._process_content_redaction')
def test_redact_call_process_redaction(_process_content_redaction):
    '''
    Verify that redact() calls _process_content_redaction
    then writes the returned data back to the same file
    '''
    conf = InsightsConfig(core_collect=False)
    arch = InsightsArchive(conf)
    arch.create_archive_dir()

    # put something in the archive to redact
    test_file = os.path.join(arch.archive_dir, 'test.file')
    with open(test_file, 'w') as t:
        t.write(test_file_data)

    dc = DataCollector(conf, arch)
    rm_conf = {'patterns': ['test']}

    if six.PY3:
        open_name = 'builtins.open'
    else:
        open_name = '__builtin__.open'

    with patch(open_name, create=True) as mock_open:
        dc.redact(rm_conf)
        _process_content_redaction.assert_called_once_with(test_file, ['test'], False)
        mock_open.assert_called_once_with(test_file, 'wb')
        mock_open.return_value.__enter__.return_value.write.assert_called_once_with(_process_content_redaction.return_value)


@patch('insights.client.data_collector._process_content_redaction')
def test_redact_exclude_regex(_process_content_redaction):
    '''
    Verify that the _process_content_redaction call is made with
    exclude == list of strings and regex == True when a list of
    regex strings is defined in rm_conf
    '''
    conf = InsightsConfig(core_collect=False)
    arch = InsightsArchive(conf)
    arch.create_archive_dir()

    # put something in the archive to redact
    test_file = os.path.join(arch.archive_dir, 'test.file')
    with open(test_file, 'w') as t:
        t.write(test_file_data)

    dc = DataCollector(conf, arch)
    rm_conf = {'patterns': {'regex': ['12.*4', '^abcd']}}

    if six.PY3:
        open_name = 'builtins.open'
    else:
        open_name = '__builtin__.open'

    with patch(open_name, create=True):
        dc.redact(rm_conf)
        _process_content_redaction.assert_called_once_with(test_file, ['12.*4', '^abcd'], True)


@patch('insights.client.data_collector._process_content_redaction')
def test_redact_exclude_no_regex(_process_content_redaction):
    '''
    Verify that the _process_content_redaction call is made with
    exclude == list of strings and regex == False when a list
    of pattern strings is defined in rm_conf
    '''
    conf = InsightsConfig(core_collect=False)
    arch = InsightsArchive(conf)
    arch.create_archive_dir()

    # put something in the archive to redact
    test_file = os.path.join(arch.archive_dir, 'test.file')
    with open(test_file, 'w') as t:
        t.write(test_file_data)

    dc = DataCollector(conf, arch)
    rm_conf = {'patterns': ['1234', 'abcd']}

    if six.PY3:
        open_name = 'builtins.open'
    else:
        open_name = '__builtin__.open'

    with patch(open_name, create=True):
        dc.redact(rm_conf)
        _process_content_redaction.assert_called_once_with(test_file, ['1234', 'abcd'], False)


@patch('insights.client.data_collector._process_content_redaction')
def test_redact_exclude_empty(_process_content_redaction):
    '''
    Verify that the _process_content_redaction is NOT called when the
    patterns key is defined but value is an empty list
    '''
    conf = InsightsConfig(core_collect=False)
    arch = InsightsArchive(conf)
    arch.create_archive_dir()

    # put something in the archive to redact
    test_file = os.path.join(arch.archive_dir, 'test.file')
    with open(test_file, 'w') as t:
        t.write(test_file_data)

    dc = DataCollector(conf, arch)
    rm_conf = {'patterns': []}

    if six.PY3:
        open_name = 'builtins.open'
    else:
        open_name = '__builtin__.open'

    with patch(open_name, create=True):
        dc.redact(rm_conf)
        _process_content_redaction.assert_not_called()


@patch('insights.client.data_collector._process_content_redaction')
def test_redact_exclude_none(_process_content_redaction):
    '''
    Verify that the _process_content_redaction is NOT called when the
    patterns key is defined but value is None
    '''
    conf = InsightsConfig(core_collect=False)
    arch = InsightsArchive(conf)
    arch.create_archive_dir()

    # put something in the archive to redact
    test_file = os.path.join(arch.archive_dir, 'test.file')
    with open(test_file, 'w') as t:
        t.write(test_file_data)

    dc = DataCollector(conf, arch)
    rm_conf = {'patterns': None}

    if six.PY3:
        open_name = 'builtins.open'
    else:
        open_name = '__builtin__.open'

    with patch(open_name, create=True):
        dc.redact(rm_conf)
        _process_content_redaction.assert_not_called()


@patch('insights.client.data_collector.os.walk')
@patch('insights.client.data_collector._process_content_redaction')
def test_redact_bad_location(_process_content_redaction, walk):
    '''
    Verify that redact() raises a RuntimeError
    if the directory present in InsightsArchive is
    in a location other than /var/tmp/**/insights-*
    '''
    conf = InsightsConfig(core_collect=False)
    arch = InsightsArchive(conf)

    for bad_path in ['/', '/home', '/etc', '/var/log/', '/home/test', '/var/tmp/f22D1d/ins2ghts']:
        arch.archive_dir = bad_path
        dc = DataCollector(conf, arch)
        rm_conf = {}
        with pytest.raises(RuntimeError):
            dc.redact(rm_conf)
        walk.assert_not_called()
        _process_content_redaction.assert_not_called()
