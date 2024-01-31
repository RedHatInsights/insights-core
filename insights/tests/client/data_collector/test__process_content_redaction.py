from insights.client.data_collector import _process_content_redaction
from mock.mock import patch, Mock, call
from tempfile import NamedTemporaryFile
from subprocess import PIPE


test_file_data = 'test\nabcd\n1234\npassword: pAsswOrd\n'
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
        call(['grep', '-v', '-E', '-f', tmpfile.return_value.name, test_file.name], stdout=PIPE)
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
        call(['grep', '-v', '-F', '-f', tmpfile.return_value.name, test_file.name], stdout=PIPE)
    ])


def test_returnvalue():
    '''
    Verify that the returned data is what we expect to see
    '''
    # exclude plainstrings
    retval = _process_content_redaction(test_file.name, ['test', 'abc'], False)
    assert retval == '1234\npassword: pAsswOrd\n'.encode('utf-8')

    # exclude regex
    retval = _process_content_redaction(test_file.name, ['[[:digit:]]+', 'a*(b|c)'], True)
    assert retval == 'test\npassword: pAsswOrd\n'.encode('utf-8')
