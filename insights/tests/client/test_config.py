import pytest
import sys
import os
from io import TextIOWrapper, BytesIO
from insights.client.config import InsightsConfig, DEFAULT_OPTS, _core_collect_default
from mock.mock import patch
from pytest import mark


@patch('insights.client.config.ConfigParser.open')
def test_config_load(open_):
    open_.return_value = TextIOWrapper(
        BytesIO(b'[insights-client]\nusername=AMURO'))
    c = InsightsConfig()
    c._load_config_file()
    assert c.username == 'AMURO'


@patch('insights.client.config.ConfigParser.open')
def test_config_load_legacy(open_):
    open_.return_value = TextIOWrapper(
        BytesIO(b'[redhat-access-insights]\nusername=BRIGHT'))
    c = InsightsConfig()
    c._load_config_file()
    assert c.username == 'BRIGHT'


@patch('insights.client.config.ConfigParser.open')
def test_config_load_legacy_ignored(open_):
    open_.return_value = TextIOWrapper(
        BytesIO(b'[insights-client]\nusername=CASVAL\n'
                b'[redhat-access-insights]\nusername=SAYLA'))
    c = InsightsConfig()
    c._load_config_file()
    assert c.username == 'CASVAL'


@patch('insights.client.config.ConfigParser.open')
def test_config_load_section_error(open_):
    # defaults on incorrect conf
    open_.return_value = TextIOWrapper(
        BytesIO(b'aFUHAEFJhFhlAFJKhnfjeaf\nusername=RAMBA'))
    c = InsightsConfig()
    c._load_config_file()
    assert c.username == DEFAULT_OPTS['username']['default']


@patch('insights.client.config.ConfigParser.open')
def test_config_load_value_error(open_):
    # defaults on incorrect conf
    open_.return_value = TextIOWrapper(
        BytesIO(b'[insights-client]\nhttp_timeout=ZGOK'))
    c = InsightsConfig()
    c._load_config_file()
    assert c.http_timeout == DEFAULT_OPTS['http_timeout']['default']


def test_defaults():
    c = InsightsConfig()
    assert isinstance(c.cmd_timeout, int)
    assert isinstance(c.retries, int)
    assert isinstance(c.http_timeout, float)


@patch('insights.client.config.os.environ', {
        'INSIGHTS_HTTP_TIMEOUT': '1234',
        'INSIGHTS_RETRIES': '1234',
        'INSIGHTS_CMD_TIMEOUT': '1234'
       })
def test_env_number_parsing():
    c = InsightsConfig()
    c._load_env()
    assert isinstance(c.cmd_timeout, int)
    assert isinstance(c.retries, int)
    assert isinstance(c.http_timeout, float)


@patch('insights.client.config.os.environ', {
        'INSIGHTS_HTTP_TIMEOUT': 'STAY AWAY',
        'INSIGHTS_RETRIES': 'FROM ME',
        'INSIGHTS_CMD_TIMEOUT': 'BICK HAZARD'
     })
def test_env_number_bad_values():
    c = InsightsConfig()
    with pytest.raises(ValueError):
        c._load_env()


@patch('insights.client.config.os.environ', {})
def test_env_no_proxy_no_warning():
    with patch('insights.client.config.sys.stdout.write') as write:
        c = InsightsConfig(_print_errors=True)
        c._load_env()
        write.assert_not_called()


@patch('insights.client.config.os.environ', {'HTTP_PROXY': '127.0.0.1'})
def test_env_http_proxy_warning():
    with patch('insights.client.config.sys.stdout.write') as write:
        c = InsightsConfig(_print_errors=True)
        c._load_env()
        write.assert_called_once()


@patch('insights.client.config.os.environ', {'HTTP_PROXY': '127.0.0.1'})
@pytest.mark.parametrize(("kwargs",), (({},), ({"_print_errors": False},)))
def test_env_http_proxy_no_warning(kwargs):
    with patch('insights.client.config.sys.stdout.write') as write:
        c = InsightsConfig(**kwargs)
        c._load_env()
        write.assert_not_called()


@patch('insights.client.config.os.environ', {'HTTP_PROXY': '127.0.0.1', 'HTTPS_PROXY': '127.0.0.1'})
def test_env_http_and_https_proxy_no_warning():
    with patch('insights.client.config.sys.stdout.write') as write:
        c = InsightsConfig(_print_errors=True)
        c._load_env()
        write.assert_not_called()


@patch('insights.client.config.os.environ', {'HTTPS_PROXY': '127.0.0.1'})
def test_env_https_proxy_no_warning():
    with patch('insights.client.config.sys.stdout.write') as write:
        c = InsightsConfig(_print_errors=True)
        c._load_env()
        write.assert_not_called()


# empty argv so parse_args isn't polluted with pytest arguments
@mark.parametrize(("config",), (
    ({"payload": "./payload.tar.gz", "content_type": "application/gzip"},),
    ({"diagnosis": True},),
    ({"compliance": True},),
    ({"check_results": True},),
    ({"checkin": True},),
))
@patch('insights.client.config.sys.argv', [sys.argv[0]])
def test_implied_non_legacy_upload(config):
    '''
    Some arguments should always imply legacy_upload=False.
    '''
    c = InsightsConfig(**config)
    c.load_all()
    assert c.legacy_upload is False


# empty argv so parse_args isn't polluted with pytest arguments
@patch('insights.client.config.sys.argv', [sys.argv[0]])
def test_to_json_quiet_implies_diagnosis():
    '''
    --diagnosis should always imply legacy_upload=False
    '''
    c = InsightsConfig(to_json=True, quiet=True)
    c.load_all()
    assert c.diagnosis is True
    assert c.legacy_upload is False


def test_offline_disables_options():
    '''
    Can't use certain options in conjunction with --offline
    '''
    with pytest.raises(ValueError):
        InsightsConfig(to_json=True, offline=True)

    with pytest.raises(ValueError):
        InsightsConfig(test_connection=True, offline=True)

    with pytest.raises(ValueError):
        InsightsConfig(status=True, offline=True)

    with pytest.raises(ValueError):
        InsightsConfig(checkin=True, offline=True)

    with pytest.raises(ValueError):
        InsightsConfig(unregister=True, offline=True)


# empty argv so parse_args isn't polluted with pytest arguments
@patch('insights.client.config.sys.argv', [sys.argv[0]])
def test_output_dir_file_cant_use_both():
    '''
    Cannot supply both --output-file and --output-dir
    '''
    with pytest.raises(ValueError):
        c = InsightsConfig(output_dir='test', output_file='test')
        c.load_all()


# empty argv so parse_args isn't polluted with pytest arguments
@patch('insights.client.config.sys.argv', [sys.argv[0]])
def test_output_dir_file_validate():
    '''
    Must supply non-empty strings for --output-dir or --output-file
    '''
    with pytest.raises(ValueError):
        c = InsightsConfig(output_dir='')
        c.load_all()
    with pytest.raises(ValueError):
        c = InsightsConfig(output_file='')
        c.load_all()


# empty argv so parse_args isn't polluted with pytest arguments
@patch('insights.client.config.sys.argv', [sys.argv[0]])
def test_output_dir_file_implies_no_upload_true_keep_archive_false():
    '''
    Using --output-dir or --tar-file should imply:
        no-upload    == True,  because we don't want to upload
        keep-archive == False, because we don't want to keep the files in temp
    '''
    c = InsightsConfig(output_dir='test')
    c.load_all()
    assert c.no_upload
    assert not c.keep_archive
    c = InsightsConfig(output_file='test')
    c.load_all()
    assert c.no_upload
    assert not c.keep_archive


# empty argv so parse_args isn't polluted with pytest arguments
@patch('insights.client.config.sys.argv', [sys.argv[0]])
def test_compressor_option_validate():
    '''
    Compressor options are validated in config.py
    (used to be in archive.py)
    If an unsupported option is given, select 'gz'
    '''
    for comp in ('gz', 'bz2', 'xz', 'none'):
        c = InsightsConfig(compressor=comp)
        c.load_all()
        assert c.compressor == comp

    c = InsightsConfig(compressor='hullabaloo')
    c.load_all()
    assert c.compressor == 'gz'


# empty argv so parse_args isn't polluted with pytest arguments
@patch('insights.client.config.sys.argv', [sys.argv[0]])
def test_output_file_guess_file_ext():
    '''
    If --output-file is selected, automatically guess
    the compressor option based on the file extension.

    If the compressor cannot be guessed from the filename,
    the filename will be given an extension based on the
    compressor option (default .tar.gz).

    If the proper extension is already part of the
    output file, the output file is unchanged.
    '''
    c = InsightsConfig(output_file='test-abc')
    c.load_all()
    assert c.output_file == os.path.abspath('test-abc.tar.gz')
    assert c.compressor == 'gz'

    c = InsightsConfig(output_file='test-def.tar.gz')
    c.load_all()
    assert c.output_file == os.path.abspath('test-def.tar.gz')
    assert c.compressor == 'gz'

    c = InsightsConfig(output_file='test-ghi.tar.bz2', compressor='bz2')
    c.load_all()
    assert c.output_file == os.path.abspath('test-ghi.tar.bz2')
    assert c.compressor == 'bz2'

    c = InsightsConfig(output_file='test-jkl', compressor='valkyrie')
    c.load_all()
    assert c.output_file == os.path.abspath('test-jkl.tar.gz')
    assert c.compressor == 'gz'

    c = InsightsConfig(output_file='test-mno.tar')
    c.load_all()
    assert c.output_file == os.path.abspath('test-mno.tar')
    assert c.compressor == 'none'


@patch('insights.client.config.get_version_info')
def test_core_collect_default(get_version_info):
    '''
    Verify that _core_collect_default() returns
    the correct True/False value depending on
    the conditions
    '''
    # RPM version is older than 3.1.0
    get_version_info.return_value = {'client_version': '3.0.13-1'}
    assert not _core_collect_default()
    conf = InsightsConfig()
    assert not conf.core_collect

    # RPM version is 3.1.0
    get_version_info.return_value = {'client_version': '3.1.0'}
    assert _core_collect_default()
    conf = InsightsConfig()
    assert conf.core_collect

    # RPM version is newer than 3.1.0
    get_version_info.return_value = {'client_version': '3.1.1'}
    assert _core_collect_default()
    conf = InsightsConfig()
    assert conf.core_collect

@patch('insights.client.config.sys.argv', [sys.argv[0], "--status"])
def test_command_line_parse_twice():
    '''
    Verify that running _load_command_line() twice does not
    raise an argparse error.

    Previously would raise a SystemExit due to argparse not
    being loaded with the correct options.
    '''
    c = InsightsConfig()
    c._load_command_line()
    c._load_command_line()
