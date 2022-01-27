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
@patch('insights.client.data_collector.get_pkg_data')
@patch('insights.client.data_collector.NamedTemporaryFile')
def test_subproc_calls_egrep(tmpfile, get_pkg_data, Popen):
    '''
    Verify that the sed command to remove passwords is called

    Verify that egrep is called when patterns to exclude are
    present and regex == True
    '''
    tmpfiles = [Mock(), Mock()]
    tmpfile.configure_mock(side_effect=tmpfiles)

    Popen.return_value.communicate = Mock(return_value=('test', None))
    _process_content_redaction(test_file.name, ['test1', 'test2'], True)

    assert tmpfile.call_count == 2
    tmpfile.assert_has_calls([call(), call()])

    tmpfiles[0].write.assert_called_once_with(get_pkg_data.return_value)
    tmpfiles[0].flush.assert_called_once_with()

    tmpfiles[1].write.assert_called_once_with('\n'.join(['test1', 'test2']).encode('utf-8'))
    tmpfiles[1].flush.assert_called_once_with()

    Popen.assert_has_calls([
        call(['sed', '-rf', tmpfiles[0].name, test_file.name], stdout=PIPE),
        call(['grep', '-v', '-E', '-f', tmpfiles[1].name], stdin=Popen.return_value.stdout, stdout=PIPE)
    ])


@patch('insights.client.data_collector.Popen')
@patch('insights.client.data_collector.get_pkg_data')
@patch('insights.client.data_collector.NamedTemporaryFile')
def test_subproc_calls_fgrep(tmpfile, get_pkg_data, Popen):
    '''
    Verify that the sed command to remove passwords is called

    Verify that fgrep is called when patterns to exclude are
    present and regex == False
    '''
    tmpfiles = [Mock(), Mock()]
    tmpfile.configure_mock(side_effect=tmpfiles)

    Popen.return_value.communicate = Mock(return_value=('test', None))
    _process_content_redaction(test_file.name, ['test1', 'test2'], False)

    assert tmpfile.call_count == 2
    tmpfile.assert_has_calls([call(), call()])

    tmpfiles[0].write.assert_called_once_with(get_pkg_data.return_value)
    tmpfiles[0].flush.assert_called_once_with()

    tmpfiles[1].write.assert_called_once_with('\n'.join(['test1', 'test2']).encode('utf-8'))
    tmpfiles[1].flush.assert_called_once_with()

    Popen.assert_has_calls([
        call(['sed', '-rf', tmpfiles[0].name, test_file.name], stdout=PIPE),
        call(['grep', '-v', '-F', '-f', tmpfiles[1].name], stdin=Popen.return_value.stdout, stdout=PIPE)
    ])


@patch('insights.client.data_collector.Popen')
@patch('insights.client.data_collector.get_pkg_data')
@patch('insights.client.data_collector.NamedTemporaryFile')
def test_nogrep(tmpfile, get_pkg_data, Popen):
    '''
    Verify that grep is not called when no patterns to exclude
    are present
    '''
    Popen.return_value.communicate = Mock(return_value=('test', None))
    _process_content_redaction(test_file.name, None, False)

    tmpfile.assert_called_once_with()
    tmpfile.return_value.write.assert_called_once_with(get_pkg_data.return_value)
    tmpfile.return_value.flush.assert_called_once_with()

    Popen.assert_called_once_with(['sed', '-rf', tmpfile.return_value.name, test_file.name], stdout=PIPE)


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
