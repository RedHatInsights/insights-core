import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import iris
from insights.tests import context_wrap


IRIS_RUNNING = """

Configuration 'IRIS'   (default)
    directory:    /intersystems
    versionid:    2023.1.0.235.1com
    datadir:      /intersystems
    conf file:    iris.cpf  (SuperServer port = 1972, WebServer = 52773)
    status:       running, since Tue Jun 27 01:55:25 2023
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

[Map.USER]
Global_EnsDICOM.Dictionary=ENSLIB
Global_EnsEDI.Description=USER
Global_EnsEDI.Description("X","X12")=ENSLIB
Global_IRIS.MsgNames("Workflow")=ENSLIB
Global_IRIS.MsgNames("tahoma,verdana")=ENSLIB
Routine_Ens*=ENSLIB
Package_CSPX.Dashboard=ENSLIB
Package_Ens=ENSLIB
Package_EnsLib=ENSLIB
Package_EnsPortal=ENSLIB

[MirrorMember]
AgentAddress=
AsyncMemberGUID=
AsyncMemberType=0
AsyncUseSystemPurgeInterval=0
JoinMirror=0
SystemName=
ValidatedMember=0
VirtualAddressInterface=

[Journal]
AlternateDirectory=/intersystems/mgr/journal/
BackupsBeforePurge=2
CompressFiles=1
CurrentDirectory=/intersystems/mgr/journal/
DaysBeforePurge=2
FileSizeLimit=1024
FreezeOnError=0
JournalFilePrefix=
JournalcspSession=0

[Startup]
CallinHalt=1
CallinStart=1
CliSysName=
DBSizesAllowed=8192
WebServerURLPrefix=
ZSTU=1

[WorkQueues]
Default=
SQL=

[Gateways]
%DotNet Server=.NET,53372,%Gateway_Object,N6.0
%IntegratedML Server=ML,53572,%Gateway_ML
%JDBC Server=JDBC,53772,%Gateway_SQL,,,,,,,0
%Java Server=Java,53272,%Gateway_Object
%Python Server=Python,53472,%Gateway_Object
%R Server=R,53872,%Gateway_Object
%XSLT Server=XSLT,53672,%Gateway_Object,,,,,,,0

[DeviceSubTypes]
C-ANSI=80^#,$C(27,91,72,27,91,74)^25^$C(8)^W $C(27,91)_(DY+1)_";"_(DX+1)_"H" S $X=DX,$Y=DY^$C(27,91,74)^$C(27,91,75)^$C(27,91,72,27,91,74)^$C(8,32,8)
C-IRIS Terminal=80^#,$C(27,91,72,27,91,74)^24^$C(8)^W $C(27,91)_(DY+1)_";"_(DX+1)_"H" S $X=DX,$Y=DY^$C(27,91,74)^$C(27,91,75)^$C(27,91,72,27,91,74)^$C(8,32,8)
C-TV925=80^#,$C(27,44)^24^$C(8)^W $C(27,61,DY+32,DX+32) S $X=DX,$Y=DY^^^$C(27,44)^$C(8,32,8)
C-VT100=80^#,$C(27,91,72,27,91,74)^24^$C(8)^W $C(27,91)_(DY+1)_";"_(DX+1)_"H" S $X=DX,$Y=DY^$C(27,91,74)^$C(27,91,75)^^
C-VT101W=132^#,$C(27,91,72,27,91,74)^14^$C(8)^W $C(27,91)_(DY+1)_";"_(DX+1)_"H" S $X=DX,$Y=DY^$C(27,91,74)^$C(27,91,75)^^
C-VT132=132^#,$C(27,91,72,27,91,74)^24^$C(8)^W $C(27,91)_(DY+1)_";"_(DX+1)_"H" S $X=DX,$Y=DY^$C(27,91,74)^$C(27,91,75)^^
C-VT220=80^#,$C(27,91,72,27,91,74)^24^$C(8)^W $C(27,91)_(DY+1)_";"_(DX+1)_"H" S $X=DX,$Y=DY^$C(27,91,74)^$C(27,91,75)^$C(27,91,72,27,91,74)^$C(8,32,8)
C-VT240=80^#,$C(27,91,72,27,91,74)^24^$C(8)^W $C(27,91)_(DY+1)_";"_(DX+1)_"H" S $X=DX,$Y=DY^$C(27,91,74)^$C(27,91,75)^$C(27,91,72,27,91,74)^$C(8,32,8)
C-VT52=80^#,$C(27,72)^24^$C(8)^W $C(27,89,DY+32,DX+32) S $X=DX,$Y=DY^^^^
M/UX=255^#^66^$C(8)^^^^^
MAIL=132^#^11^$C(8)^^^^^
P-DEC=132^#^66^$C(8)^^^^^
PK-DEC=150^#^66^$C(8)^^^^^
PK-QUME=150^#^66^$C(8)^^^^^

[Devices]
0=0^TRM^C-IRIS Terminal^^^^Principal device^
2=2^SPL^PK-DEC^^^^Spool LA120^
47=47^MT^M/UX^^("auv":0:2048)^^Magnetic tape^
48=48^MT^M/UX^^("avl":0:2048)^^Magnetic tape^
57=57^BT^M/UX^^("auv":0:2048)^^Magnetic tape^
58=58^BT^M/UX^^("avl":0:2048)^^Magnetic tape^
SPOOL=2^SPL^PK-DEC^^^^Spool LA120^
TERM=0^TRM^C-IRIS Terminal^^^^Windows Console^
|LAT|=0^TRM^C-VT220^^^^Principal device^
|PRN|=|PRN|^OTH^P-DEC^^"W"^^Windows Printer^
|TNT|=0^TRM^C-VT220^^^^Principal device^
|TRM|=0^TRM^C-IRIS Terminal^^^^Windows Console^

[MagTapes]
47=/dev/st0
48=/dev/st1
49=/dev/st0l
50=/dev/st1l
51=/dev/st0a
52=/dev/st1a
53=/dev/st0m
54=/dev/st1m
55=/dev/nst0
56=/dev/nst1
57=/dev/st0
58=/dev/st1
59=/dev/st0l
60=/dev/st1l
61=/dev/st0a
62=/dev/st1a

[config]
LibPath=
MaxServerConn=1
MaxServers=2
Path=
PythonPath=
bbsiz=-1
console=,
errlog=500
globals=0,0,600,0,0,0
gmheap=0
history=500
ijcbuff=512
ijcnum=16
jrnbufs=64
locksiz=0
memlock=0
netjob=1
nlstab=50
overview=Linux/x86-64~UNIX
pijdir=
routines=0
targwijsz=0
udevtabsiz=24576
wijdir=
zfheap=0,0

[Miscellaneous]
AsyncDisconnectErr=0
AsynchError=1
BreakMode=1
CollectResourceStats=0
DisconnectErr=0
ZDateNull=0
ZaMode=0

[ECP]
ClientReconnectDuration=1200
ClientReconnectInterval=5
ServerTroubleDuration=60

[Cluster]
CommIPAddress=
JoinCluster=0

[LicenseServers]
LOCAL=127.0.0.1,4002

[Monitor]
SNMPEnabled=0

[IO]
File=^%X364
MagTape=^%XMAG
Other=^%X364
Terminal=^%X364

[SQL]
ANSIPrecedence=1
AdaptiveMode=1
AllowRowIDUpdate=0
AutoParallel=1
DropDelete=1
ECPSync=0
ExtrinsicFunctions=0
FastDistinct=1
IdKey=1
IdTrxFrom=~ `!@#$%^&*()_+-=[]\{}|;':",./<>?
IdTrxTo=
LockThreshold=1000
LockTimeout=10
TODATEDefaultFormat=DD MON YYYY
TimePrecision=0

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

[Telnet]
DNSLookup=ON
Port=23

[Conversions]
LastConvertTime=2023-07-20 08:58:29
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
    iris_running = iris.IrisList(context_wrap(IRIS_RUNNING))
    assert iris_running['name'] == "IRIS"
    assert iris_running['status'] == "running, since Tue Jun 27 01:55:25 2023"
    assert 'state' in iris_running
    assert iris_running.is_running

    iris_down = iris.IrisList(context_wrap(IRIS_DOWN))
    assert iris_down['name'] == "IRIS"
    assert iris_down['status'] == "down, last used Tue Jun 27 01:50:36 2023"
    assert 'state' not in iris_down
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
    # assert len(list(log.get_after(datetime(2023, 6, 26, 8, 2, 18)))) == 5


def test_doc_examples():
    env = {
        'iris_info': iris.IrisList(context_wrap(IRIS_RUNNING)),
        'iris_cpf': iris.IrisCpf(context_wrap(IRIS_CPF)),
        'iris_log': iris.IrisMessages(context_wrap(IRIS_MESSAGES_LOG)),
    }
    failed, total = doctest.testmod(iris, globs=env)
    assert failed == 0
