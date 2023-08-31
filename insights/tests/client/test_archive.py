import time
from insights.client.archive import InsightsArchive
from mock.mock import patch, Mock, call
from unittest import TestCase
from pytest import raises
from insights.client.constants import InsightsConstants as constants

test_timestamp = '000000'
test_hostname = 'testhostname'
test_archive_name = 'insights-testhostname-000000'
test_archive_dir = '/var/tmp/insights-client-000000/insights-testhostname-000000'
test_obfuscated_archive_dir = '/var/tmp/insights-client-000000/insights-localhost-000000'
test_cmd_dir = '/var/tmp/insights-client-000000/insights-testhostname-000000/insights_commands'
test_tmp_dir_path = '/var/tmp/insights-client-000000'
test_tmp_dir = 'insights-client-000000'


@patch('insights.client.archive.time.strftime', Mock(return_value=test_timestamp))
@patch('insights.client.archive.determine_hostname', Mock(return_value=test_hostname))
@patch('insights.client.archive.tempfile.mkdtemp')
@patch('insights.client.archive.atexit.register')
class TestInsightsArchive(TestCase):
    @patch('insights.client.archive.InsightsArchive.cleanup_previous_archive')
    def test_init_archive(self, cleanup, register, mkdtemp):
        '''
        Verify archive is created with default parameters
        '''
        config = Mock()
        config.obfuscate_hostname = False
        archive = InsightsArchive(config)

        assert archive.config == config
        assert archive.tmp_dir
        assert archive.archive_dir is None
        assert archive.cmd_dir is None
        assert archive.compressor == config.compressor
        assert archive.archive_name == test_archive_name

        cleanup.assert_called_once()
        mkdtemp.assert_has_calls([call(dir=constants.insights_tmp_path, prefix=constants.insights_tmp_prefix + '-')])
        register.assert_called_once()

    @patch('insights.client.archive.os.path.exists', return_value=False)
    @patch('insights.client.archive.os.makedirs')
    @patch('insights.client.archive.InsightsArchive.cleanup_previous_archive')
    def test_create_archive_dir_default(self, _cleanup, mkdir, _exists, _, __):
        '''
        Verify archive_dir is created when it does not already exist
        '''
        config = Mock()
        config.obfuscate_hostname = False
        archive = InsightsArchive(config)
        archive.tmp_dir = test_tmp_dir_path
        result = archive.create_archive_dir()

        mkdir.assert_called_once_with(test_archive_dir, 0o700)
        # ensure the archive_dir is returned from the function
        assert result == test_archive_dir
        # ensure the class attr is set
        assert archive.archive_dir == test_archive_dir
        # ensure the retval and attr are the same
        assert result == archive.archive_dir

    @patch('insights.client.archive.os.listdir', return_value=[])
    @patch('insights.client.archive.shutil.rmtree')
    def test_tmp_dir_no_cleanup(self, rmtree, listdir, _, __):
        '''
        Verify cleanup doesn't act with no previous directories
        '''
        InsightsArchive(Mock())
        listdir.assert_called_once_with(constants.insights_tmp_path)
        rmtree.assert_not_called()

    @patch('insights.client.archive.os.listdir', return_value=[test_tmp_dir])
    @patch('insights.client.archive.shutil.rmtree')
    @patch('insights.client.archive.os.path.isdir', return_value=[True])
    @patch('insights.client.archive.time.time')
    def test_tmp_dir_no_cleanup_time(self, _timestamp, _isdir, rmtree, listdir, _, __):
        '''
        Verify cleanup doesn't act with previous directories that are not
        older that 1 day
        '''
        _timestamp.return_value = time.time()
        InsightsArchive(Mock())
        listdir.assert_called_once_with(constants.insights_tmp_path)
        rmtree.assert_not_called()

    @patch('insights.client.archive.os.listdir', return_value=[test_tmp_dir])
    @patch('insights.client.archive.shutil.rmtree')
    @patch('insights.client.archive.os.path.isdir', return_value=[True])
    @patch('insights.client.archive.os.path.getmtime')
    def test_tmp_dir_cleanup(self, _timestamp, _isdir, rmtree, listdir, _, __):
        # set the timestamp of the directory as it was create 2 days ago
        _timestamp.return_value = time.time() - 2 * 24 * 60 * 60
        InsightsArchive(Mock())
        listdir.assert_called_once_with(constants.insights_tmp_path)
        rmtree.assert_called_with(test_tmp_dir_path, True)

    @patch('insights.client.archive.os.makedirs')
    def test_create_archive_dir_obfuscated(self, makedirs, _, __):
        '''
        Verify archive_dir is created when it does not already exist
        '''
        config = Mock()
        config.obfuscate_hostname = True
        with patch('insights.client.archive.os.path.exists', return_value=True):
            archive = InsightsArchive(config)
        # give this a discrete value so we can check the results
        archive.tmp_dir = test_tmp_dir_path

        with patch('insights.client.archive.os.path.exists', return_value=False):
            result = archive.create_archive_dir()
        makedirs.assert_called_once_with(test_obfuscated_archive_dir, 0o700)
        # ensure the archive_dir is returned from the function
        assert result == test_obfuscated_archive_dir
        # ensure the class attr is set
        assert archive.archive_dir == test_obfuscated_archive_dir
        # ensure the retval and attr are the same
        assert result == archive.archive_dir

    @patch('insights.client.archive.os.makedirs')
    @patch('insights.client.archive.os.path.exists', side_effect=[False, False])
    def test_create_archive_dir_defined_path_DNE(self, exists, makedirs, _, __):
        '''
        Verify archive_dir is created when the attr is defined but
        the path does not exist
        '''
        config = Mock()
        config.obfuscate_hostname = False
        archive = InsightsArchive(config)
        # give this a discrete value so we can check the results
        archive.tmp_dir = test_tmp_dir_path
        archive.archive_dir = test_archive_dir
        result = archive.create_archive_dir()
        exists.assert_has_calls([call(archive.archive_dir),
                                 call(test_archive_dir)])
        makedirs.assert_called_once_with(test_archive_dir, 0o700)
        # ensure the archive_dir is returned from the function
        assert result == test_archive_dir
        # ensure the class attr is set
        assert archive.archive_dir == test_archive_dir
        # ensure the retval and attr are the same
        assert result == archive.archive_dir

    @patch('insights.client.archive.os.makedirs')
    def test_create_archive_dir_undef_path_exists(self, makedirs, _, __):
        '''
        Verify archive_dir is not re-created when the attr is undefined but
        the path exists
        '''
        config = Mock()
        config.obfuscate_hostname = False
        with patch('insights.client.archive.os.path.exists', return_value=True):
            archive = InsightsArchive(config)
        # give this a discrete value so we can check the results
        archive.tmp_dir = test_tmp_dir_path
        with patch('insights.client.archive.os.path.exists', return_value=True) as exists:
            result = archive.create_archive_dir()
        makedirs.assert_not_called()
        exists.assert_called_once_with(test_archive_dir)
        # ensure the archive_dir is returned from the function
        assert result == test_archive_dir
        # ensure the class attr is set
        assert archive.archive_dir == test_archive_dir
        # ensure the retval and attr are the same
        assert result == archive.archive_dir

    @patch('insights.client.archive.os.makedirs')
    def test_create_archive_dir_defined_path_exists(self, makedirs, _, __):
        '''
        When archive_dir is defined and exists, simply return the
        class attr and do not attempt to create it
        '''
        with patch('insights.client.archive.os.path.exists', return_value=True):
            archive = InsightsArchive(Mock())
        # give this a discrete value so we can check the results
        archive.tmp_dir = '/var/tmp/test'
        archive.archive_dir = test_archive_dir
        with patch('insights.client.archive.os.path.exists', return_value=True) as exists:
            result = archive.create_archive_dir()
        makedirs.assert_not_called()
        exists.assert_called_once_with(archive.archive_dir)
        # ensure the archive_dir is returned from the function
        assert result == test_archive_dir
        # ensure the class attr is set
        assert archive.archive_dir == test_archive_dir
        # ensure the retval and attr are the same
        assert result == archive.archive_dir

    @patch('insights.client.archive.InsightsArchive.create_archive_dir', return_value=test_archive_dir)
    @patch('insights.client.archive.os.makedirs')
    @patch('insights.client.archive.os.path.exists', side_effect=[False])
    def test_create_command_dir(self, exists, makedirs, create_archive_dir, _, __):
        '''
        Verify insights_commands dir is created
        '''
        archive = InsightsArchive(Mock())
        archive.archive_dir = test_archive_dir
        result = archive.create_command_dir()
        create_archive_dir.assert_called_once()
        makedirs.assert_called_once_with(test_cmd_dir, 0o700)
        # ensure the cmd_dir is returned from the function
        assert result == test_cmd_dir
        # ensure the class attr is set
        assert archive.cmd_dir == test_cmd_dir
        # ensure the retval and attr are the same
        assert result == archive.cmd_dir

    @patch('insights.client.archive.InsightsArchive.create_archive_dir', return_value=test_archive_dir)
    @patch('insights.client.archive.os.path.join', Mock())
    @patch('insights.client.archive.InsightsArchive.cleanup_previous_archive')
    def test_get_full_archive_path(self, create_archive_dir, cleanup, _, __):
        '''
        Verify create_archive_dir is called when calling get_full_archive_path
        '''
        archive = InsightsArchive(Mock())
        archive.get_full_archive_path('test')
        create_archive_dir.assert_called_once()

    @patch('insights.client.archive.InsightsArchive.create_archive_dir', return_value=test_archive_dir)
    @patch('insights.client.archive.os.path.join', Mock())
    @patch('insights.client.archive.os.path.isdir', Mock())
    @patch('insights.client.archive.shutil.copytree', Mock())
    @patch('insights.client.archive.InsightsArchive.cleanup_previous_archive', Mock())
    def test_copy_dir(self, create_archive_dir, _, __):
        '''
        Verify create_archive_dir is called when calling copy_dir
        '''
        archive = InsightsArchive(Mock())
        archive.copy_dir('test')
        create_archive_dir.assert_called_once()

    @patch('insights.client.archive.shutil.copyfile')
    @patch('insights.client.archive.os.path.isdir', Mock())
    @patch('insights.client.archive.os.path.exists', return_value=True)
    def test_keep_archive(self, path_exists, copyfile, _, __):
        archive = InsightsArchive(Mock())
        archive.tar_file = '/var/tmp/insights-archive-test.tar.gz'
        archive.keep_archive_dir = '/var/tmp/test-archive'
        archive.storing_archive()
        copyfile.assert_called_once_with(archive.tar_file, '/var/tmp/test-archive/insights-archive-test.tar.gz')

    @patch('insights.client.archive.shutil.copyfile', side_effect=OSError)
    @patch('insights.client.archive.os.path.join', Mock())
    @patch('insights.client.archive.os.path.isdir', Mock())
    @patch('insights.client.archive.os.path.basename', Mock())
    @patch('insights.client.archive.logger')
    @patch('insights.client.archive.os.path.exists', return_value=True)
    @patch('insights.client.archive.InsightsArchive.cleanup_previous_archive', Mock())
    def test_keep_archive_err_during_copy(self, path_exists, logger, copyfile, _, __):
        archive = InsightsArchive(Mock())
        archive.archive_stored = '/var/tmp/test-archive/test-store-archive'
        archive.keep_archive_dir = '/var/tmp/test-archive'
        with raises(Exception):
            archive.storing_archive()
        logger.error.assert_called_once_with('ERROR: Could not stored archive to %s', archive.archive_stored)

    @patch('insights.client.archive.os.makedirs', side_effect=OSError)
    @patch('insights.client.archive.os.path.exists', side_effect=[False])
    @patch('insights.client.archive.os.path.join', Mock())
    @patch('insights.client.archive.os.path.isdir', Mock())
    @patch('insights.client.archive.os.path.basename', Mock())
    @patch('insights.client.archive.logger')
    @patch('insights.client.archive.InsightsArchive.cleanup_previous_archive', Mock())
    def test_keep_arhive_err_creating_directory(self, logger, path_exists, mkdir, _, __):
        archive = InsightsArchive(Mock())
        archive.keep_archive_dir = '/var/tmp/test-archive'
        with raises(Exception):
            archive.storing_archive()
        logger.error.assert_called_with('ERROR: Could not create %s', archive.keep_archive_dir)
