from insights.client.config import InsightsConfig
from insights.client.archive import InsightsArchive
from insights.client.data_collector import DataCollector
from mock.mock import patch
import pytest
import os
import six

test_file_data = 'test\nabcd\n1234\npassword: p4ssw0rd\n'


@patch('insights.client.data_collector.os.walk')
# @patch('insights.client.data_collector._process_content_redaction')
def test_redact_call_walk(walk):
    '''
    Verify that redact() calls os.walk and when an
    an archive structure is present in /var/tmp/**/insights-*
    '''
    conf = InsightsConfig()
    arch = InsightsArchive(conf)
    # TODO: uncomment this once dual collector logic is merged.
    #   archive dir must be created explicitly
    # arch.create_archive_dir()

    dc = DataCollector(conf, arch)
    rm_conf = {}

    dc.redact(rm_conf)
    walk.assert_called_once_with(arch.archive_dir)


@patch('insights.client.data_collector._process_content_redaction')
def test_redact_call_process_redaction(_process_content_redaction):
    '''
    Verify that redact() calls _process_content_redaction
    then writes the returned data back to the same file

    Also verifies that the "exclude" parameter is None and the
    "regex" parameter is False in the _process_content_redaction
    call when rm_conf is empty
    '''
    conf = InsightsConfig()
    arch = InsightsArchive(conf)
    # TODO: uncomment this once dual collector logic is merged.
    #   archive dir must be created explicitly
    # arch.create_archive_dir()

    # put something in the archive to redact
    test_file = os.path.join(arch.archive_dir, 'test.file')
    with open(test_file, 'w') as t:
        t.write(test_file_data)

    dc = DataCollector(conf, arch)
    rm_conf = {}

    if six.PY3:
        open_name = 'builtins.open'
    else:
        open_name = '__builtin__.open'

    with patch(open_name, create=True) as mock_open:
        dc.redact(rm_conf)
        _process_content_redaction.assert_called_once_with(test_file, None, False)
        mock_open.assert_called_once_with(test_file, 'w')
        mock_open.return_value.__enter__.return_value.write.assert_called_once_with(_process_content_redaction.return_value)


@patch('insights.client.data_collector._process_content_redaction')
def test_redact_exclude_regex(_process_content_redaction):
    '''
    Verify that the _process_content_redaction call is made with
    exclude == list of strings and regex == True when a list of
    regex strings is defined in rm_conf
    '''
    conf = InsightsConfig()
    arch = InsightsArchive(conf)
    # TODO: uncomment this once dual collector logic is merged.
    #   archive dir must be created explicitly
    # arch.create_archive_dir()

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
    conf = InsightsConfig()
    arch = InsightsArchive(conf)
    # TODO: uncomment this once dual collector logic is merged.
    #   archive dir must be created explicitly
    # arch.create_archive_dir()

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
    Verify that the _process_content_redaction call is made with
    exclude == [] and regex == False when the patterns key is
    defined but value is an empty list
    '''
    conf = InsightsConfig()
    arch = InsightsArchive(conf)
    # TODO: uncomment this once dual collector logic is merged.
    #   archive dir must be created explicitly
    # arch.create_archive_dir()

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
        _process_content_redaction.assert_called_once_with(test_file, [], False)


@patch('insights.client.data_collector._process_content_redaction')
def test_redact_exclude_none(_process_content_redaction):
    '''
    Verify that the _process_content_redaction call is made with
    exclude == None and regex == False when the patterns key is
    defined but value is an empty dict
    '''
    conf = InsightsConfig()
    arch = InsightsArchive(conf)
    # TODO: uncomment this once dual collector logic is merged.
    #   archive dir must be created explicitly
    # arch.create_archive_dir()

    # put something in the archive to redact
    test_file = os.path.join(arch.archive_dir, 'test.file')
    with open(test_file, 'w') as t:
        t.write(test_file_data)

    dc = DataCollector(conf, arch)
    rm_conf = {'patterns': {}}

    if six.PY3:
        open_name = 'builtins.open'
    else:
        open_name = '__builtin__.open'

    with patch(open_name, create=True):
        dc.redact(rm_conf)
        _process_content_redaction.assert_called_once_with(test_file, None, False)


@patch('insights.client.data_collector.os.walk')
@patch('insights.client.data_collector._process_content_redaction')
def test_redact_bad_location(_process_content_redaction, walk):
    '''
    Verify that redact() raises a RuntimeError
    if the directory present in InsightsArchive is
    in a location other than /var/tmp/**/insights-*
    '''
    conf = InsightsConfig()
    arch = InsightsArchive(conf)

    for bad_path in ['/', '/home', '/etc', '/var/log/', '/home/test', '/var/tmp/f22D1d/ins2ghts']:
        arch.archive_dir = bad_path
        dc = DataCollector(conf, arch)
        rm_conf = {}
        with pytest.raises(RuntimeError):
            dc.redact(rm_conf)
        walk.assert_not_called()
        _process_content_redaction.assert_not_called()
