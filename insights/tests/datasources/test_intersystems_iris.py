import pytest
from mock.mock import Mock

try:
    from unittest.mock import patch, mock_open
    builtin_open = "builtins.open"
except Exception:
    from mock import patch, mock_open
    builtin_open = "__builtin__.open"

from os import path
from insights.core import filters
from insights.core.exceptions import SkipComponent
from insights.parsers.iris import IrisList
from insights.specs import Specs
from insights.specs.datasources.intersystems_iris import iris_working_configuration, iris_working_messages_log
from insights.tests import context_wrap


with open(path.join(path.dirname(__file__), 'iris.cpf'), 'r') as conf:
    CPF_RESULT = conf.read()

with open(path.join(path.dirname(__file__), 'iris_raw_messages.log'), 'r') as conf:
    LOG_INPUT = conf.read()

with open(path.join(path.dirname(__file__), 'iris_filtered_messages.log'), 'r') as conf:
    LOG_RESULT = conf.read()


IRIR_LIST = """

Configuration 'IRIS'   (default)
	directory:    {}
	versionid:    2023.1.0.235.1com
	datadir:      /intersystems
	conf file:    iris.cpf  (SuperServer port = 1972, WebServer = 52773)
	status:       running, since Wed Jul 19 02:37:46 2023
	state:        ok
	product:      InterSystems IRIS
""".strip()


CPF_RELATIVE_PATH = 'insights_commands/iris_cpf'
LOG_RELATIVE_PATH = 'insights_commands/iris_messages_log'

def setup_function(func):
    if Specs.intersystems_iris_messages_log_filter in filters._CACHE:
        del filters._CACHE[Specs.intersystems_iris_messages_log_filter]
    if Specs.intersystems_iris_messages_log_filter in filters.FILTERS:
        del filters.FILTERS[Specs.intersystems_iris_messages_log_filter]

    if func is test_iris_working_messages_log:
        filters.add_filter(Specs.intersystems_iris_messages_log_filter, ["Generic.Event"])
    # if func is test_iris_working_messages_log_no_match_filter:
    #     filters.add_filter(Specs.intersystems_iris_messages_log_filter, ["test_no_match_filter"])
    # if func is test_iris_working_messages_log_no_filter:
    #     filters.add_filter(Specs.intersystems_iris_messages_log_filter, [])


def test_iris_working_configuration():
    iris_list_info = IrisList(context_wrap(IRIR_LIST.format(path.dirname(__file__))))
    broker = {IrisList: iris_list_info}
    result = iris_working_configuration(broker)
    assert result.content == CPF_RESULT.splitlines()
    assert result.relative_path == CPF_RELATIVE_PATH


def test_iris_working_configuration_no_file():
    iris_list_info = IrisList(context_wrap(IRIR_LIST.format("/intersystems")))
    broker = {IrisList: iris_list_info}
    with pytest.raises(SkipComponent) as e:
        iris_working_configuration(broker)
    assert 'No such file' in str(e)


def mocked_open(self, file, **kwargs):
    if file=='/intersystems/mgr/messages.log':
        return LOG_INPUT
    return open(self, file, **kwargs)


def mocked_open2(self, file, **kwargs):
    if file == "/intersystems/mgr/messages.log":
        return mock_open(read_data=LOG_INPUT)(self, file, **kwargs)
    return open(self, file, **kwargs)


@patch("insights.specs.datasources.intersystems_iris.open", new=mocked_open2)
@patch("os.path.isfile", return_value=True)
def test_iris_working_messages_log(m_isfile):
    iris_list_info = IrisList(context_wrap(IRIR_LIST.format(path.dirname(__file__))))
    broker = {IrisList: iris_list_info}
    result = iris_working_messages_log(broker)


# def test_iris_working_messages_log_no_match_filter():
#
#
# def test_iris_working_messages_log_no_filter():