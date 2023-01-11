"""
SAP Trace Files  - Files ``/usr/sap/SID/SNAME/work/dev_*``
==========================================================

Parsers included in this module are:

SapDevDisp - Files ``/usr/sap/SID/SNAME/work/dev_disp``
-------------------------------------------------------

SapDevRd - Files ``/usr/sap/SID/SNAME/work/dev_rd``
---------------------------------------------------
"""
from insights.core import LogFileOutput
from insights.core.exceptions import ParseException
from insights.core.plugins import parser
from insights.specs import Specs


class SapDevTraceFile(LogFileOutput):
    """
    The Base class for parsing the SAP trace files.
    """

    def get_after(self, *args, **kwargs):
        """
        .. warning::
            The ``get_after`` function is not supported by this Parser because
            of the structure of the SAP trace files are totally different with
            the log files expected by the base class``LogFileOutput``.

        Raises:
            ParseException: Always raises ParseException.
        """
        raise ParseException("get_after() is not supported by this Parser.")

    @property
    def sid(self):
        """
        The SID of this trace file.
        """
        return self.file_path.lstrip('/').split('/')[2]

    @property
    def instance(self):
        """
        The instance name of this trace file.
        """
        return self.file_path.lstrip('/').split('/')[3]


@parser(Specs.sap_dev_disp)
class SapDevDisp(SapDevTraceFile):
    """
    This class reads the SAP trace files ``/usr/sap/SID/SNAME/work/dev_disp``

    Sample content of the file::

        ---------------------------------------------------
        trc file: "dev_disp", trc level: 1, release: "745"
        ---------------------------------------------------

        Sun Aug 18 17:17:45 2019
        TRACE FILE TRUNCATED ( pid =    16955 )

        sysno      00
        sid        RH1
        systemid   390 (AMD/Intel x86_64 with Linux)
        relno      7450
        patchlevel 0
        patchno    100
        intno      20151301
        make       multithreaded, Unicode, 64 bit, optimized
        profile    /usr/sap/RH1/SYS/profile/RH1_D00_vm37-39
        pid        16955

        Sun Aug 18 17:17:45 2019
        kernel runs with dp version 3000(ext=117000) (@(#) DPLIB-INT-VERSION-0+3000-UC)
        length of sys_adm_ext is 500 bytes

        Scheduler info
        --------------
        WP info
          #dia     = 10
          #btc     = 3
          #standby = 0
          #max     = 21
        General Scheduler info
          preemptionInfo.isActive           = true
          preemptionInfo.timeslice          = 500
          preemptionInfo.checkLoad          = true
        Prio Class High
          maxRuntime[RQ_Q_PRIO_HIGH]     = 600 sec
          maxRuntimeHalf[RQ_Q_PRIO_HIGH] = 300 sec
        Running requests[RQ_Q_PRIO_NORMAL] = 0
        Running requests[RQ_Q_PRIO_LOW] = 0

        *** WARNING => DpHdlDeadWp: wp_adm slot for W7 has no pid [dpxxwp.c     1353]
        DpSkipSnapshot: last snapshot created at Sun Aug 18 17:15:25 2019, skip new snapshot
        *** WARNING => DpHdlDeadWp: wp_adm slot for W8 has no pid [dpxxwp.c     1353]
        DpSkipSnapshot: last snapshot created at Sun Aug 18 17:15:25 2019, skip new snapshot
        *** WARNING => DpHdlDeadWp: wp_adm slot for W9 has no pid [dpxxwp.c     1353]

        Sun Aug 18 17:17:45 2019
        DpSkipSnapshot: last snapshot created at Sun Aug 18 17:17:45 2019, skip new snapshot
        DpCheckSapcontrolProcess: sapcontrol with pid 1479 terminated
        *** WARNING => DpRequestProcessingCheck: potential request processing problem detected (14. check) [dpxxwp.c     4633]

    Examples:
        >>> type(dev_disp)
        <class 'insights.parsers.sap_dev_trace_files.SapDevDisp'>
        >>> dev_disp.file_path == '/usr/sap/RH1/D00/work/dev_disp'
        True
        >>> dev_disp.sid == 'RH1'
        True
        >>> dev_disp.instance == 'D00'
        True
        >>> len(dev_disp.get("WARNING"))
        4
    """
    pass


@parser(Specs.sap_dev_rd)
class SapDevRd(SapDevTraceFile):
    """
    This class reads the SAP trace files ``/usr/sap/SID/SNAME/work/dev_rd``

    Sample content of the file::

        ---------------------------------------------------
        trc file: "dev_rd", trc level: 1, release: "745"
        ---------------------------------------------------
        systemid   390 (AMD/Intel x86_64 with Linux)
        relno      7450
        patchlevel 0
        patchno    100
        intno      20151301
        make       multithreaded, Unicode, 64 bit, optimized
        pid        16982

        Thu Jul 18 02:59:37 2019
        gateway (version=745.2015.12.21 (with SSL support))
        Bind service  (socket) to port
        GwPrintMyHostAddr: my host addresses are :
        *
        * SWITCH TRC-LEVEL from 1 to 1
        *
        ***LOG S00=> GwInitReader, gateway started ( 16982) [gwxxrd.c     1820]
        systemid   390 (AMD/Intel x86_64 with Linux)
        relno      7450
        patchlevel 0
        patchno    100
        intno      20151301
        make       multithreaded, Unicode, 64 bit, optimized
        pid        16982

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

        ********** SERVER SNAPSHOT 2727 - begin **********

        -----------------------
        --- SYS TABLE DUMP ----
        -----------------------
        +------+-------+----------------------+-----------------+------------+-------+--------------------------+
        | Indx | State | Hostname             | Addr            | Port / TP  | Type  | Last-Request             |
        +------+-------+----------------------+-----------------+------------+-------+--------------------------+
        |    4 | CONNE | vm37-39              | 127.0.0.1       | IGS.RH1    | REGIS | Mon Aug 19 05:15:15 2019 |
        |    3 | CONNE | vm37-39              | 127.0.0.1       | IGS.RH1    | REGIS | Mon Aug 19 05:15:15 2019 |
        |    2 | CONNE | vm37-39              | 127.0.0.1       | IGS.RH1    | REGIS | Mon Aug 19 05:15:15 2019 |
        |    1 | CONNE | vm37-39              | 127.0.0.1       | IGS.RH1    | REGIS | Mon Aug 19 05:15:15 2019 |
        |    0 | CONNE | vm37-39.gsslab.pek2. | 10.72.37.39     | sapgw00    | LOCAL | Wed Aug  7 22:58:50 2019 |
        +------+-------+----------------------+-----------------+------------+-------+--------------------------+
        -----------------------
        --- GWTBL TABLE DUMP --
        -----------------------
        +------+-------+----------------------+-----------------+------------+-------+--------------------------+
        | Indx | State | Hostname             | Addr            | Port       | Type  | Last-Request             |
        +------+-------+----------------------+-----------------+------------+-------+--------------------------+
        |    0 | CONNE | vm37-39.gsslab.pek2. | 10.72.37.39     | sapgw00    | LOCAL | Wed Aug  7 22:58:50 2019 |
        +------+-------+----------------------+-----------------+------------+-------+--------------------------+

        ********** SERVER SNAPSHOT 2727 - end ************

    Examples:
        >>> type(dev_rd)
        <class 'insights.parsers.sap_dev_trace_files.SapDevRd'>
        >>> dev_rd.file_path == '/usr/sap/RH2/D03/work/dev_rd'
        True
        >>> dev_rd.sid == 'RH2'
        True
        >>> dev_rd.instance == 'D03'
        True
        >>> len(dev_rd.get("CCMS:"))
        6
    """
    pass
