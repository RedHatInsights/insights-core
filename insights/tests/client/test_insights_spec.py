# from insights.client.insights_spec import InsightsFile
# from insights.client.insights_spec import InsightsSpec
# from mock.mock import patch, MagicMock, ANY
# import mock


# def test_string_pattern_init():
#     '''
#     Assert spec is loaded in string mode when a list of strings is present
#     in the "patterns" section
#     (legacy remove conf + new style w/ list only)
#     '''
#     spec = InsightsSpec(MagicMock(), {'command': '', 'pattern': [], 'symbolic_name': ''}, ['test'])
#     assert not spec.regex


# def test_regex_pattern_init():
#     '''
#     Assert spec is loaded in regex mode when a dict is present with the "wegex"
#     key with a list of strings as its value in the "patterns" section
#     '''
#     spec = InsightsSpec(MagicMock(), {'command': '', 'pattern': [], 'symbolic_name': ''}, {'regex': ['test']})
#     assert spec.regex


# @patch('insights.client.insights_spec.Popen')
# @patch('insights.client.insights_spec.os.path.isfile', return_value=True)
# def test_string_pattern_called(isfile, Popen):
#     '''
#     '''
#     process_mock = mock.Mock()
#     attrs = {'communicate.return_value': (b'output', b'error')}
#     process_mock.configure_mock(**attrs)
#     Popen.return_value = process_mock
#     fs = InsightsFile({'file': '', 'pattern': [], 'symbolic_name': ''}, ['test'], '/')
#     fs.get_output()
#     Popen.assert_any_call(['grep', '-F', '-v', '-f', ANY], stdin=ANY, stdout=ANY)


# @patch('insights.client.insights_spec.Popen')
# @patch('insights.client.insights_spec.os.path.isfile', return_value=True)
# def test_regex_pattern_called(isfile, Popen):
#     '''
#     '''
#     process_mock = mock.Mock()
#     attrs = {'communicate.return_value': (b'output', b'error')}
#     process_mock.configure_mock(**attrs)
#     Popen.return_value = process_mock
#     fs = InsightsFile({'file': '', 'pattern': [], 'symbolic_name': ''}, {'regex': ['test']}, '/')
#     fs.get_output()
#     Popen.assert_any_call(['grep', '-E', '-v', '-f', ANY], stdin=ANY, stdout=ANY)
