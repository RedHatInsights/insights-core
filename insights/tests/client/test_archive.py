from insights.client.archive import InsightsArchive
from mock.mock import patch, Mock, call
from unittest import TestCase

test_timestamp = '000000'
test_hostname = 'testhostname'
test_archive_name = 'insights-testhostname-000000'
test_archive_dir = '/var/tmp/test/insights-testhostname-000000'
test_cmd_dir = '/var/tmp/test/insights-testhostname-000000/insights_commands'


@patch('insights.client.archive.time.strftime', Mock(return_value=test_timestamp))
@patch('insights.client.archive.determine_hostname', Mock(return_value=test_hostname))
@patch('insights.client.archive.tempfile.mkdtemp')
@patch('insights.client.archive.atexit.register')
class TestInsightsArchive(TestCase):

    def test_init_archive(self, register, mkdtemp):
        '''
        Verify archive is created with default parameters
        '''
        config = Mock()
        archive = InsightsArchive(config)

        assert archive.config == config
        assert archive.tmp_dir
        assert archive.archive_tmp_dir
        assert archive.archive_dir is None
        assert archive.cmd_dir is None
        assert archive.compressor == config.compressor
        assert archive.archive_name == test_archive_name

        mkdtemp.assert_has_calls([call(prefix='/var/tmp/'),
                                  call(prefix='/var/tmp/')])
        register.assert_called_once()

    @patch('insights.client.archive.os.makedirs')
    @patch('insights.client.archive.os.path.exists', Mock(return_value=False))
    def test_create_archive_dir_default(self, makedirs, _, __):
        '''
        Verify archive_dir is created when it does not already exist
        '''
        archive = InsightsArchive(Mock())
        # give this a discrete value so we can check the results
        archive.tmp_dir = '/var/tmp/test'
        result = archive.create_archive_dir()
        makedirs.assert_called_once_with(test_archive_dir, 0o700)
        # ensure the archive_dir is returned from the function
        assert result == test_archive_dir
        # ensure the class attr is set
        assert archive.archive_dir == test_archive_dir
        # ensure the retval and attr are the same
        assert result == archive.archive_dir

    @patch('insights.client.archive.os.makedirs')
    @patch('insights.client.archive.os.path.exists', return_value=False)
    def test_create_archive_dir_defined_path_DNE(self, exists, makedirs, _, __):
        '''
        Verify archive_dir is created when the attr is defined but
        the path does not exist
        '''
        archive = InsightsArchive(Mock())
        # give this a discrete value so we can check the results
        archive.tmp_dir = '/var/tmp/test'
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
    @patch('insights.client.archive.os.path.exists', return_value=True)
    def test_create_archive_dir_undef_path_exists(self, exists, makedirs, _, __):
        '''
        Verify archive_dir is not re-created when the attr is undefined but
        the path exists
        '''
        archive = InsightsArchive(Mock())
        # give this a discrete value so we can check the results
        archive.tmp_dir = '/var/tmp/test'
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
    @patch('insights.client.archive.os.path.exists', return_value=True)
    def test_create_archive_dir_defined_path_exists(self, exists, makedirs, _, __):
        '''
        When archive_dir is defined and exists, simply return the
        class attr and do not attempt to create it
        '''
        archive = InsightsArchive(Mock())
        # give this a discrete value so we can check the results
        archive.tmp_dir = '/var/tmp/test'
        archive.archive_dir = test_archive_dir
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
    @patch('insights.client.archive.os.path.exists', return_value=False)
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
    def test_get_full_archive_path(self, create_archive_dir, _, __):
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
    def test_copy_dir(self, create_archive_dir, _, __):
        '''
        Verify create_archive_dir is called when calling copy_dir
        '''
        archive = InsightsArchive(Mock())
        archive.copy_dir('test')
        create_archive_dir.assert_called_once()
