import pytest

try:
    from unittest.mock import patch, mock_open
    builtin_open = "builtins.open"
except Exception:
    from mock import patch, mock_open
    builtin_open = "__builtin__.open"

from os import path
from insights.core import filters
from insights.core.exceptions import SkipComponent
from insights.parsers.iris import IrisList, IrisCpf
from insights.specs import Specs
from insights.specs.datasources.intersystems import iris_working_configuration, iris_working_messages_log
from insights.tests import context_wrap


IRIR_LIST = """

Configuration 'IRIS'   (default)
    directory:    /intersystems
    versionid:    2023.1.0.235.1com
    datadir:      /intersystems
    conf file:    iris.cpf  (SuperServer port = 1972, WebServer = 52773)
    status:       running, since Wed Jul 19 02:37:46 2023
    state:        ok
    product:      InterSystems IRIS
""".strip()


IRIS_CPF = """
[ConfigFile]
Product=IRIS
Version=2023.1

[Databases]
IRISSYS=/intersystems/mgr/
IRISLIB=/intersystems/mgr/irislib/
IRISTEMP=/intersystems/mgr/iristemp/
IRISLOCALDATA=/intersystems/mgr/irislocaldata/
IRISAUDIT=/intersystems/mgr/irisaudit/
ENSLIB=/intersystems/mgr/enslib/
USER=/intersystems/mgr/user/

[Namespaces]
%SYS=IRISSYS
USER=USER
""".strip()


RAW_MESSAGES = """
06/26/23-08:02:17:828 (144145) 0 [Generic.Event] Allocated 495MB shared memory
06/26/23-08:02:17:828 (144145) 0 [Generic.Event] 32MB global buffers, 80MB routine buffers, 64MB journal buffers, 4MB buffer descriptors, 300MB heap, 5MB ECP, 9MB miscellaneous
06/26/23-08:02:17:831 (144145) 0 [Crypto.IntelSandyBridgeAESNI] Intel Sandy Bridge AES-NI instructions detected.
06/26/23-08:02:17:831 (144145) 0 [SIMD] SIMD optimization level: DEFAULT X86
06/26/23-08:02:17:903 (144145) 0 [WriteDaemon.UsingWIJFile] Using WIJ file: /intersystems/mgr/IRIS.WIJ
06/26/23-08:02:17:903 (144145) 0 [Generic.Event] No journaling info from prior system
06/26/23-08:02:17:903 (144145) 0 [WriteDaemon.CreatingNewWIJ] Creating a new WIJ file
06/26/23-08:02:18:104 (144145) 0 [WriteDaemon.CreatedNewWIJ] New WIJ file created
06/26/23-08:02:18:110 (144145) 0 [Generic.Event]
""".strip()


FILTERED_MESSAGES = """
06/26/23-08:02:17:828 (144145) 0 [Generic.Event] Allocated 495MB shared memory
06/26/23-08:02:17:828 (144145) 0 [Generic.Event] 32MB global buffers, 80MB routine buffers, 64MB journal buffers, 4MB buffer descriptors, 300MB heap, 5MB ECP, 9MB miscellaneous
06/26/23-08:02:17:903 (144145) 0 [Generic.Event] No journaling info from prior system
06/26/23-08:02:18:110 (144145) 0 [Generic.Event]
""".strip()


def setup_function(func):
    if Specs.iris_messages_log in filters._CACHE:
        del filters._CACHE[Specs.iris_messages_log]
    if Specs.iris_messages_log in filters.FILTERS:
        del filters.FILTERS[Specs.iris_messages_log]

    if func is test_iris_working_messages_log:
        filters.add_filter(Specs.iris_messages_log, ["Generic.Event"])
    if func is test_iris_working_messages_log_no_match_filter:
        filters.add_filter(Specs.iris_messages_log, ["test_no_match_filter"])
    if func is test_iris_working_messages_log_no_filter:
        filters.add_filter(Specs.iris_messages_log, [])


@patch("insights.specs.datasources.intersystems.open", new_callable=mock_open, read_data=IRIS_CPF)
@patch("os.path.isfile", return_value=True)
def test_iris_working_configuration(m_open, m_isfile):
    iris_list_info = IrisList(context_wrap(IRIR_LIST))
    broker = {IrisList: iris_list_info}
    result = iris_working_configuration(broker)
    assert result.content == IRIS_CPF.splitlines()
    assert result.relative_path == path.join(path.dirname(__file__), '/intersystems/iris.cpf')


@patch("insights.specs.datasources.intersystems.open", new_callable=mock_open, read_data=IRIS_CPF)
def test_iris_working_configuration_no_file(m_open):
    iris_list_info = IrisList(context_wrap(IRIR_LIST))
    broker = {IrisList: iris_list_info}
    with pytest.raises(SkipComponent) as e:
        iris_working_configuration(broker)
    assert 'SkipComponent' in str(e)


@patch("insights.specs.datasources.intersystems.open", new_callable=mock_open, read_data=RAW_MESSAGES)
@patch("os.path.isfile", return_value=True)
def test_iris_working_messages_log(m_open, m_isfile):
    iris_cpf_info = IrisCpf(context_wrap(IRIS_CPF))
    broker = {IrisCpf: iris_cpf_info}
    result = iris_working_messages_log(broker)
    assert result.content == FILTERED_MESSAGES.splitlines()
    assert result.relative_path == path.join(path.dirname(__file__), '/intersystems/mgr/messages.log')


@patch("insights.specs.datasources.intersystems.open", new_callable=mock_open, read_data=RAW_MESSAGES)
def test_iris_working_messages_log_no_file(m_open):
    iris_cpf_info = IrisCpf(context_wrap(IRIS_CPF))
    broker = {IrisCpf: iris_cpf_info}
    with pytest.raises(SkipComponent) as e:
        iris_working_messages_log(broker)
    assert 'SkipComponent' in str(e)


@patch("insights.specs.datasources.intersystems.open", new_callable=mock_open, read_data=RAW_MESSAGES)
@patch("os.path.isfile", return_value=True)
def test_iris_working_messages_log_no_match_filter(m_open, m_isfile):
    iris_cpf_info = IrisCpf(context_wrap(IRIS_CPF))
    broker = {IrisCpf: iris_cpf_info}
    result = iris_working_messages_log(broker)
    assert result.content == []
    assert result.relative_path == path.join(path.dirname(__file__), '/intersystems/mgr/messages.log')


@patch("insights.specs.datasources.intersystems.open", new_callable=mock_open, read_data=RAW_MESSAGES)
@patch("os.path.isfile", return_value=True)
def test_iris_working_messages_log_no_filter(m_open, m_isfile):
    iris_cpf_info = IrisCpf(context_wrap(IRIS_CPF))
    broker = {IrisCpf: iris_cpf_info}
    with pytest.raises(SkipComponent) as e:
        iris_working_messages_log(broker)
    assert 'SkipComponent' in str(e)
