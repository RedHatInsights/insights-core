from insights.client.data_collector import _process_content_redaction
from insights.client.constants import InsightsConstants as constants
from mock.mock import patch, Mock, call
from tempfile import NamedTemporaryFile
from subprocess import PIPE


test_file_data = 'test\nabcd\n1234\npassword: p4ssw0rd\n'
test_file = NamedTemporaryFile()
test_file.write(test_file_data.encode('utf-8'))
test_file.flush()


@patch('insights.client.data_collector.Popen')
@patch('insights.client.data_collector.NamedTemporaryFile')
def test_subproc_calls_egrep(tmpfile, Popen):
    '''
    Verify that the sed command to remove passwords is called

    Verify that egrep is called when patterns to exclude are
    present and regex == True
    '''
    Popen.return_value.communicate = Mock(return_value=('test', None))
    _process_content_redaction(test_file.name, ['test1', 'test2'], True)
    tmpfile.assert_called_once()
    tmpfile.return_value.write.assert_called_once_with('\n'.join(['test1', 'test2']).encode('utf-8'))
    tmpfile.return_value.flush.assert_called_once()
    Popen.assert_has_calls([
        call(['sed', '-rf', constants.default_sed_file, test_file.name], stdout=PIPE),
        call(['grep', '-v', '-E', '-f', tmpfile.return_value.name], stdin=Popen.return_value.stdout, stdout=PIPE)
    ])


@patch('insights.client.data_collector.Popen')
@patch('insights.client.data_collector.NamedTemporaryFile')
def test_subproc_calls_fgrep(tmpfile, Popen):
    '''
    Verify that the sed command to remove passwords is called

    Verify that fgrep is called when patterns to exclude are
    present and regex == False
    '''
    Popen.return_value.communicate = Mock(return_value=('test', None))
    _process_content_redaction(test_file.name, ['test1', 'test2'], False)
    tmpfile.assert_called_once()
    tmpfile.return_value.write.assert_called_once_with('\n'.join(['test1', 'test2']).encode('utf-8'))
    tmpfile.return_value.flush.assert_called_once()
    Popen.assert_has_calls([
        call(['sed', '-rf', constants.default_sed_file, test_file.name], stdout=PIPE),
        call(['grep', '-v', '-F', '-f', tmpfile.return_value.name], stdin=Popen.return_value.stdout, stdout=PIPE)
    ])


@patch('insights.client.data_collector.Popen')
@patch('insights.client.data_collector.NamedTemporaryFile')
def test_nogrep(tmpfile, Popen):
    '''
    Verify that grep is not called when no patterns to exclude
    are present
    '''
    Popen.return_value.communicate = Mock(return_value=('test', None))
    _process_content_redaction(test_file.name, None, False)
    tmpfile.assert_not_called()
    Popen.assert_called_once_with(['sed', '-rf', constants.default_sed_file, test_file.name], stdout=PIPE)


# mock the .exp.sed file for QE pipeline
mock_sed_file = NamedTemporaryFile()
mock_sed_file.write("s/(password[a-zA-Z0-9_]*)(\\s*\\:\\s*\\\"*\\s*|\\s*\\\"*\\s*=\\s*\\\"\\s*|\\s*=+\\s*|\\s*--md5+\\s*|\\s*)([a-zA-Z0-9_!@#$%^&*()+=/-]*)/\\1\\2********/\ns/(password[a-zA-Z0-9_]*)(\\s*\\*+\\s+)(.+)/\\1\\2********/".encode('utf-8'))
mock_sed_file.flush()


@patch('insights.client.data_collector.constants.default_sed_file', mock_sed_file.name)
def test_returnvalue():
    '''
    Verify that the returned data is what we expect to see
    '''
    # no exclude
    retval = _process_content_redaction(test_file.name, [], False)
    assert retval == 'test\nabcd\n1234\npassword: ********\n'.encode('utf-8')

    # no exclude also works with None
    retval = _process_content_redaction(test_file.name, None, False)
    assert retval == 'test\nabcd\n1234\npassword: ********\n'.encode('utf-8')

    # exclude plainstrings
    retval = _process_content_redaction(test_file.name, ['test', 'abc'], False)
    assert retval == '1234\npassword: ********\n'.encode('utf-8')

    # exclude regex
    retval = _process_content_redaction(test_file.name, ['[[:digit:]]+', 'a*(b|c)'], True)
    assert retval == 'test\npassword: ********\n'.encode('utf-8')
