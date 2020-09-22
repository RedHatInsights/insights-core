from insights.client.config import InsightsConfig
from insights.contrib.soscleaner import SOSCleaner
from insights.client.data_collector import DataCollector, CleanOptions
from mock.mock import patch, Mock


@patch('insights.client.data_collector.InsightsArchive')
def test_archive_returned(_):
    c = InsightsConfig()
    r = {}   # rm_conf
    d = DataCollector(c)
    ret = d.done(c, r)
    d.archive.create_tar_file.assert_called_once()
    assert ret == d.archive.create_tar_file.return_value


@patch('insights.client.data_collector.InsightsArchive')
def test_dir_returned(_):
    c = InsightsConfig(output_dir='test')
    r = {}   # rm_conf
    d = DataCollector(c)
    ret = d.done(c, r)
    d.archive.create_tar_file.assert_not_called()
    assert ret == d.archive.archive_dir


@patch('insights.client.data_collector.SOSCleaner')
@patch('insights.client.data_collector.InsightsArchive')
def test_soscleaner_archive_returned(_, soscleaner):
    '''
    Test that SOSCleaner is enabled when obfuscate=True,
    and returns an archive by default
    '''
    c = InsightsConfig(obfuscate=True)
    r = {'keywords': ['test']}
    d = DataCollector(c)
    ret = d.done(c, r)
    soscleaner.assert_called_once()
    soscleaner.return_value.clean_report.assert_called_once()
    assert ret == soscleaner.return_value.archive_path


@patch('insights.client.data_collector.SOSCleaner')
@patch('insights.client.data_collector.InsightsArchive')
def test_soscleaner_dir_returned(_, soscleaner):
    '''
    Test that SOSCleaner returns a directory when
    output_dir is specified.
    '''
    c = InsightsConfig(obfuscate=True, output_dir='test')
    r = {'keywords': ['test']}
    d = DataCollector(c)
    ret = d.done(c, r)
    soscleaner.assert_called_once()
    soscleaner.return_value.clean_report.assert_called_once()
    assert ret == soscleaner.return_value.dir_path


@patch('insights.client.data_collector.NamedTemporaryFile')
def test_cleanoptions_outputfile(_):
    '''
    Test that CleanOptions no_tar_file option
    is set when output_dir is specified
    '''
    c = InsightsConfig(obfuscate=True, output_dir='test')
    r = {'keywords': ['test']}
    o = CleanOptions(c, '/var/tmp/test', r, 'test')
    assert o.no_tar_file is not None


@patch('insights.client.data_collector.CleanOptions')
@patch('insights.contrib.soscleaner.os.path.isdir')
def test_soscleaner_additions(isdir_, clean_opts):
    '''
    Test the added if-block in soscleaner.py
    for returning before creating the archive
    '''
    clean_opts.hostname_path = 'test'

    # test that soscleaner returns as normal by default,
    #   then that it returns None when no_tar_file is not None
    for cond in (None, 'test'):
        clean_opts.no_tar_file = cond

        s = SOSCleaner()
        s.logger = Mock()
        s.file_count = Mock()
        s._prep_environment = Mock(return_value=(None, '/var/tmp/test/socleaner-test', None, None, None))
        s._start_logging = Mock()
        s._get_disclaimer = Mock()
        s._keywords2db = Mock()
        s._clean_files_only = Mock()
        s._extract_sosreport = Mock()
        s._make_dest_env = Mock()
        s._get_hostname = Mock(return_value=(None, None))
        s._add_extra_files = Mock()
        s._process_hosts_file = Mock()
        s._domains2db = Mock()
        s._file_list = Mock(return_value=[])
        s._clean_file = Mock()
        s._create_reports = Mock(side_effect=setattr(s, 'logfile', 'test'))
        s._create_reports = Mock(side_effect=setattr(s, 'ip_report', 'test'))
        s._create_archive = Mock(side_effect=setattr(s, 'archive_path', 'test'))

        ret = s.clean_report(clean_opts, '/var/tmp/test')
        if cond:
            # output_dir specified, tar file not created
            s._create_archive.assert_not_called()
            assert ret is None
        else:
            # default, tar file created
            s._create_archive.assert_called_once()
            assert ret == [s.archive_path, s.logfile, s.ip_report]
