import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import iris
from insights.tests import context_wrap


IRIS_RUNNING_1 = """

Configuration 'IRIS'   (default)
    directory:    /intersystems
    versionid:    2023.1.0.235.1com
    datadir:      /intersystems
    conf file:    iris.cpf  (SuperServer port = 1972, WebServer = 52773)
    status:       running, since Tue Jun 27 01:55:25 2023
    state:        ok
    product:      InterSystems IRIS

Configuration 'IRIS2'
    directory:    /intersystems2
    versionid:    2023.1.0.235.1com
    datadir:      /intersystems2
    conf file:    iris.cpf  (SuperServer port = 51773, WebServer = 52774)
    status:       running, since Thu Aug 10 02:47:27 2023
    state:        ok
    product:      InterSystems IRIS
""".strip()

IRIS_RUNNING_2 = """

Configuration 'IRIS'   (default)
    directory:    /intersystems
    versionid:    2023.1.0.235.1com
    datadir:      /intersystems
    conf file:    iris.cpf  (SuperServer port = 1972, WebServer = 52773)
    status:       running, since Tue Jun 27 01:55:25 2023
    state:        ok
    product:      InterSystems IRIS

Configuration 'IRIS2'
    directory:    /intersystems2
    versionid:    2023.1.0.235.1com
    datadir:      /intersystems2
    conf file:    iris.cpf  (SuperServer port = 51773, WebServer = 52774)
    status:       down, last used Thu Aug 10 07:21:10 2023
    state:        ok
    product:      InterSystems IRIS
""".strip()

IRIS_DOWN = """

Configuration 'IRIS'   (default)
    directory:    /intersystems
    versionid:    2023.1.0.235.1com
    datadir:      /intersystems
    conf file:    iris.cpf  (SuperServer port = 1972, WebServer = 52773)
    status:       down, last used Tue Jun 27 01:50:36 2023
    product:      InterSystems IRIS

Configuration 'IRIS2'
    directory:    /intersystems2
    versionid:    2023.1.0.235.1com
    datadir:      /intersystems2
    conf file:    iris.cpf  (SuperServer port = 51773, WebServer = 52774)
    status:       down, last used Thu Aug 10 07:21:10 2023
    state:        ok
    product:      InterSystems IRIS
""".strip()

IRIS_NO_CONTENT = """"""


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

[SqlSysDatatypes]
BIGINT=%Library.BigInt
BIGINT(%1)=%Library.BigInt
BINARY=%Library.Binary(MAXLEN=1)
BINARY VARYING=%Library.Binary(MAXLEN=1)
CLOB=%Stream.GlobalCharacter
DATE=%Library.Date
DATETIME=%Library.DateTime
DATETIME2=%Library.DateTime
DEC=%Library.Numeric(MAXVAL=999999999999999,MINVAL=-999999999999999,SCALE=0)
DEC(%1)=%Library.Numeric(MAXVAL=<|'$$maxval^%apiSQL(%1,0)'|>,MINVAL=<|'$$minval^%apiSQL(%1,0)'|>,SCALE=0)
DEC(%1,%2)=%Library.Numeric(MAXVAL=<|'$$maxval^%apiSQL(%1,%2)'|>,MINVAL=<|'$$minval^%apiSQL(%1,%2)'|>,SCALE=%2)
DECIMAL=%Library.Numeric(MAXVAL=999999999999999,MINVAL=-999999999999999,SCALE=0)
DECIMAL(%1)=%Library.Numeric(MAXVAL=<|'$$maxval^%apiSQL(%1,0)'|>,MINVAL=<|'$$minval^%apiSQL(%1,0)'|>,SCALE=0)
DECIMAL(%1,%2)=%Library.Numeric(MAXVAL=<|'$$maxval^%apiSQL(%1,%2)'|>,MINVAL=<|'$$minval^%apiSQL(%1,%2)'|>,SCALE=%2)
DOUBLE=%Library.Double
DOUBLE PRECISION=%Library.Double
""".strip()

IRIS_MESSAGES_LOG = """
06/26/23-08:02:17:828 (144145) 0 [Generic.Event] Allocated 495MB shared memory
06/26/23-08:02:17:828 (144145) 0 [Generic.Event] 32MB global buffers, 80MB routine buffers, 64MB journal buffers, 4MB buffer descriptors, 300MB heap, 5MB ECP, 9MB miscellaneous
06/26/23-08:02:17:831 (144145) 0 [Crypto.IntelSandyBridgeAESNI] Intel Sandy Bridge AES-NI instructions detected.
06/26/23-08:02:17:831 (144145) 0 [SIMD] SIMD optimization level: DEFAULT X86
06/26/23-08:02:17:903 (144145) 0 [WriteDaemon.UsingWIJFile] Using WIJ file: /intersystems/mgr/IRIS.WIJ
06/26/23-08:02:17:903 (144145) 0 [Generic.Event] No journaling info from prior system
06/26/23-08:02:17:903 (144145) 0 [WriteDaemon.CreatingNewWIJ] Creating a new WIJ file
06/26/23-08:02:18:104 (144145) 0 [WriteDaemon.CreatedNewWIJ] New WIJ file created
06/26/23-08:02:18:110 (144145) 0 [Generic.Event]
Startup of InterSystems IRIS [IRIS for UNIX (Red Hat Enterprise Linux 8 for x86-64) 2023.1 (Build 235.1) Fri Jun 2 2023 13:26:47 EDT]
        in ../bin/
        with mgr: /intersystems/mgr
        with wij: /intersystems/mgr/IRIS.WIJ
        from: /intersystems/mgr/
  OS=[Linux], version=[#1 SMP Fri Sep 30 11:45:06 EDT 2022], release=[4.18.0-425.3.1.el8.x86_64], machine=[x86_64]
  nodename=[rhel8].
  numasyncwijbuf: 2, wdwrite_asyncio_max: 64, wijdirectio: on, synctype: 3
  System Initialized.
06/26/23-08:02:18:136 (144182) 0 [WriteDaemon.Started] Write daemon started.
06/26/23-08:02:18:281 (144200) 0 [Database.MountedRW] Mounted database /intersystems/mgr/ (SFN 0) read-write.
06/26/23-08:02:18:317 (144207) 0 [Utility.Event] Starting ^INSTALL procedure
""".strip()


def test_iris_list():
    iris_running = iris.IrisList(context_wrap(IRIS_RUNNING_1))
    assert len(iris_running) == 2
    assert iris_running[0]['status'] == 'running, since Tue Jun 27 01:55:25 2023'
    assert iris_running.default['status'] == 'running, since Tue Jun 27 01:55:25 2023'
    assert 'state' in iris_running[0]
    assert iris_running.is_running

    iris_running2 = iris.IrisList(context_wrap(IRIS_RUNNING_2))
    assert len(iris_running2) == 2
    assert iris_running2[0]['status'] == 'running, since Tue Jun 27 01:55:25 2023'
    assert iris_running2[1]['status'] == 'down, last used Thu Aug 10 07:21:10 2023'
    assert 'state' in iris_running2[0]
    assert iris_running2.is_running

    iris_down = iris.IrisList(context_wrap(IRIS_DOWN))
    assert len(iris_down) == 2
    assert iris_down[0]['status'] == 'down, last used Tue Jun 27 01:50:36 2023'
    assert 'state' not in iris_down[0]
    assert not iris_down.is_running


def test_fail():
    with pytest.raises(SkipComponent) as e:
        iris.IrisList(context_wrap(IRIS_NO_CONTENT))
    assert "The result is empty" in str(e)


def test_iris_cpf():
    iris_cpf = iris.IrisCpf(context_wrap(IRIS_CPF))
    assert "Databases" in iris_cpf
    assert iris_cpf.get("Databases", "IRISSYS") == "/intersystems/mgr/"
    assert iris_cpf.get("SqlSysDatatypes", "DEC") == "%Library.Numeric(MAXVAL=999999999999999,MINVAL=-999999999999999,SCALE=0)"


def test_iris_messages_log():
    log = iris.IrisMessages(context_wrap(IRIS_MESSAGES_LOG))
    assert len(log.get('Generic.Event')) == 4
    assert len(log.get('shared memory')) == 1


def test_doc_examples():
    env = {
        'iris_info': iris.IrisList(context_wrap(IRIS_RUNNING_1)),
        'iris_cpf': iris.IrisCpf(context_wrap(IRIS_CPF)),
        'iris_log': iris.IrisMessages(context_wrap(IRIS_MESSAGES_LOG)),
    }
    failed, total = doctest.testmod(iris, globs=env)
    assert failed == 0
