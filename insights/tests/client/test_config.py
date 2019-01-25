import pytest
from io import TextIOWrapper, BytesIO
from insights.client.config import InsightsConfig, DEFAULT_OPTS
from mock.mock import patch


@patch('insights.client.config.ConfigParser.open')
def test_config_load(open_):
    open_.return_value = TextIOWrapper(
        BytesIO(b'[insights-client]\nusername=AMURO'))
    c = InsightsConfig()
    c.load_config_file()
    assert c.username == 'AMURO'


@patch('insights.client.config.ConfigParser.open')
def test_config_load_legacy(open_):
    open_.return_value = TextIOWrapper(
        BytesIO(b'[redhat-access-insights]\nusername=BRIGHT'))
    c = InsightsConfig()
    c.load_config_file()
    assert c.username == 'BRIGHT'


@patch('insights.client.config.ConfigParser.open')
def test_config_load_legacy_ignored(open_):
    open_.return_value = TextIOWrapper(
        BytesIO(b'[insights-client]\nusername=CASVAL\n'
                b'[redhat-access-insights]\nusername=SAYLA'))
    c = InsightsConfig()
    c.load_config_file()
    assert c.username == 'CASVAL'


@patch('insights.client.config.ConfigParser.open')
def test_config_load_section_error(open_):
    # defaults on incorrect conf
    open_.return_value = TextIOWrapper(
        BytesIO(b'aFUHAEFJhFhlAFJKhnfjeaf\nusername=RAMBA'))
    c = InsightsConfig()
    c.load_config_file()
    assert c.username == DEFAULT_OPTS['username']['default']


@patch('insights.client.config.ConfigParser.open')
def test_config_load_value_error(open_):
    # defaults on incorrect conf
    open_.return_value = TextIOWrapper(
        BytesIO(b'[insights-client]\nhttp_timeout=ZGOK'))
    c = InsightsConfig()
    c.load_config_file()
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
    c.load_env()
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
        c.load_env()
