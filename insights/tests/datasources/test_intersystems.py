import pytest

from mock.mock import patch
from insights.core.exceptions import SkipComponent
from insights.parsers.iris import IrisList, IrisCpf
from insights.specs.datasources.intersystems import iris_working_configuration, iris_working_messages_log
from insights.tests import context_wrap


IRIR_LIST = """

Configuration 'IRIS'   (default)
    directory:    /intersystems
    versionid:    2023.1.0.235.1com
    datadir:      /intersystems
    conf file:    iris.cpf  (SuperServer port = 1972, WebServer = 52773)
    status:       running, since Tue Sep 12 09:49:54 2023
    state:        ok
    product:      InterSystems IRIS

Configuration 'IRIS2'
    directory:    /intersystems2
    versionid:    2023.1.0.235.1com
    datadir:      /intersystems2
    conf file:    iris.cpf  (SuperServer port = 51773, WebServer = 52774)
    status:       running, since Tue Sep 12 09:50:05 2023
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

[config]
bbsiz=-1
console=,
""".strip()

IRIS_CPF_2 = """
[ConfigFile]
Product=IRIS2
Version=2023.1

[Databases]
IRISSYS=/intersystems2/mgr/
IRISLIB=/intersystems/mgr2/irislib/
IRISTEMP=/intersystems/mgr2/iristemp/
IRISLOCALDATA=/intersystems2/mgr/irislocaldata/
IRISAUDIT=/intersystems2/mgr/irisaudit/
ENSLIB=/intersystems2/mgr/enslib/
USER=/intersystems2/mgr/user/

[Namespaces]
%SYS=IRISSYS
USER=USER

[config]
bbsiz=-1
console=,
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


@patch("os.path.isfile", return_value=True)
def test_iris_working_configuration(m_isfile):
    iris_list_info = IrisList(context_wrap(IRIR_LIST))
    broker = {IrisList: iris_list_info}
    result = iris_working_configuration(broker)
    assert set(result) == set(["/intersystems/iris.cpf", "/intersystems2/iris.cpf"])


def test_iris_working_configuration_no_file():
    iris_list_info = IrisList(context_wrap(IRIR_LIST))
    broker = {IrisList: iris_list_info}
    with pytest.raises(SkipComponent) as e:
        iris_working_configuration(broker)
    assert 'SkipComponent' in str(e)


@patch("os.path.isfile", return_value=True)
def test_iris_working_messages_log(m_isfile):
    iris_cpf_info = IrisCpf(context_wrap(IRIS_CPF))
    iris_cpf_info_2 = IrisCpf(context_wrap(IRIS_CPF_2))
    broker = {IrisCpf: [iris_cpf_info, iris_cpf_info_2]}
    result = iris_working_messages_log(broker)
    assert set(result) == set(['/intersystems/mgr/messages.log', '/intersystems2/mgr/messages.log'])


def test_iris_working_messages_log_no_file():
    iris_cpf_info = IrisCpf(context_wrap(IRIS_CPF))
    iris_cpf_info_2 = IrisCpf(context_wrap(IRIS_CPF_2))
    broker = {IrisCpf: [iris_cpf_info, iris_cpf_info_2]}
    with pytest.raises(SkipComponent) as e:
        iris_working_messages_log(broker)
    assert 'SkipComponent' in str(e)
