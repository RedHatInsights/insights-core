import pytest
import doctest
from insights.parsers import sap_dev_trace_files, ParseException
from insights.parsers.sap_dev_trace_files import SapDevDisp, SapDevRd
from insights.tests import context_wrap

SAP_DEV_DISP = """
---------------------------------------------------
trc file: "dev_disp", trc level: 1, release: "745"
---------------------------------------------------

*** WARNING => DpHdlDeadWp: wp_adm slot for W7 has no pid [dpxxwp.c     1353]
DpSkipSnapshot: last snapshot created at Sun Aug 18 17:15:25 2019, skip new snapshot
*** WARNING => DpHdlDeadWp: wp_adm slot for W8 has no pid [dpxxwp.c     1353]
DpSkipSnapshot: last snapshot created at Sun Aug 18 17:15:25 2019, skip new snapshot
*** WARNING => DpHdlDeadWp: wp_adm slot for W9 has no pid [dpxxwp.c     1353]

Sun Aug 18 17:17:45 2019
DpSkipSnapshot: last snapshot created at Sun Aug 18 17:17:45 2019, skip new snapshot
DpCheckSapcontrolProcess: sapcontrol with pid 1479 terminated
*** WARNING => DpRequestProcessingCheck: potential request processing problem detected (14. check) [dpxxwp.c     4633]
""".strip()

SAP_DEV_RD = """
---------------------------------------------------
trc file: "dev_rd", trc level: 1, release: "745"
---------------------------------------------------
Thu Jul 18 02:59:37 2019
gateway (version=745.2015.12.21 (with SSL support))
gw/reg_no_conn_info = 1
* SWITCH TRC-RESOLUTION from 1 to 1
gw/sim_mode : set to 0
gw/logging : ACTION=Ss LOGFILE=gw_log-%y-%m-%d SWITCHTF=day MAXSIZEKB=100
NI buffering enabled
CCMS: initialize CCMS Monitoring for ABAP instance with J2EE addin.

Thu Jul 18 02:59:38 2019
CCMS: Initialized monitoring segment of size 60000000.
CCMS: Initialized CCMS Headers in the shared monitoring segment.
CCMS: Checking Downtime Configuration of Monitoring Segment.

Thu Jul 18 02:59:39 2019
CCMS: AlMsUpload called by wp 1002.
CCMS: AlMsUpload successful for /usr/sap/RH1/D00/log/ALMTTREE (542 MTEs).

Thu Jul 18 02:59:40 2019
GwIInitSecInfo: secinfo version = 2
GwIRegInitRegInfo: reg_info file /usr/sap/RH1/D00/data/reginfo not found
""".strip()


SapDevDisp.keep_scan('warning_lines', "WARNING")
SapDevRd.keep_scan('ccms', "CCMS:")
DISP_PATH = '/usr/sap/RH1/D00/work/dev_disp'
RD_PATH = '/usr/sap/RH2/D03/work/dev_rd'


def test_dev_disp():
    dev_disp = SapDevDisp(context_wrap(SAP_DEV_DISP, path=DISP_PATH))
    assert len(dev_disp.warning_lines) == len(dev_disp.get("WARNING"))
    assert dev_disp.sid == DISP_PATH.split('/')[3]
    assert dev_disp.instance == DISP_PATH.split('/')[4]
    with pytest.raises(ParseException):
        dev_disp.get_after()


def test_dev_rd():
    dev_rd = SapDevRd(context_wrap(SAP_DEV_RD, path=RD_PATH))
    assert len(dev_rd.ccms) == len(dev_rd.get("CCMS:"))
    assert dev_rd.sid == RD_PATH.split('/')[3]
    assert dev_rd.instance == RD_PATH.split('/')[4]
    with pytest.raises(ParseException):
        dev_rd.get_after()


def test_dev_docs():
    env = {
        "dev_disp": SapDevDisp(context_wrap(SAP_DEV_DISP, path=DISP_PATH)),
        "dev_rd": SapDevRd(context_wrap(SAP_DEV_RD, path=RD_PATH))
    }
    failed, total = doctest.testmod(sap_dev_trace_files, globs=env)
    assert failed == 0
