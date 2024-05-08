import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import db2
from insights.parsers.db2 import Db2ls
from insights.tests import context_wrap


DB2LS_A_C = """
#PATH:VRMF:FIXPACK:SPECIAL:INSTALLTIME:INSTALLERUID
/opt/ibm/db2/V11.5:11.5.6.0:0 ::Fri Jan 14 20:20:07 2022 CST :0
/opt/ibm/db2/V11.5_01:11.5.7.0:0 ::Fri Feb 11 10:34:51 2022 CST :0
"""

DB2LS_A_C_EMPTY1 = ""
DB2LS_A_C_EMPTY2 = "#PATH:VRMF:FIXPACK:SPECIAL:INSTALLTIME:INSTALLERUID"


DB2_CONFIGURATION_USER = """

       Database Configuration for Database TESTD1

 Database configuration release level                    = 0x1500
 Database release level                                  = 0x1500

 Update to database level pending                        = NO (0x0)
 Database territory                                      = US
 Database code page                                      = 1208
 Database code set                                       = UTF-8
 Database country/region code                            = 1
 Database collating sequence                             = IDENTITY
 Alternate collating sequence              (ALT_COLLATE) =
 Database page size                                      = 4096

 Statement concentrator                      (STMT_CONC) = OFF

 Discovery support for this database       (DISCOVER_DB) = ENABLE

 Restrict access                                         = NO
 Default query optimization class         (DFT_QUERYOPT) = 5
 Degree of parallelism                      (DFT_DEGREE) = 1
 Continue upon arithmetic exceptions   (DFT_SQLMATHWARN) = NO
 Default refresh age                   (DFT_REFRESH_AGE) = 0
 Default maintained table types for opt (DFT_MTTB_TYPES) = SYSTEM
 Number of frequent values retained     (NUM_FREQVALUES) = 10
 Number of quantiles retained            (NUM_QUANTILES) = 20

 Decimal floating point rounding mode  (DECFLT_ROUNDING) = ROUND_HALF_EVEN

 DECIMAL arithmetic mode                (DEC_ARITHMETIC) =
 Large aggregation                   (LARGE_AGGREGATION) = NO

 Backup pending                                          = NO

 All committed transactions have been written to disk    = YES
 Rollforward pending                                     = NO
 Restore pending                                         = NO
 Control file recovery path       (CTRL_FILE_RECOV_PATH) =
 Encrypted database                                      = NO
 Procedural language stack trace        (PL_STACK_TRACE) = NONE
 HADR SSL certificate label             (HADR_SSL_LABEL) =
 HADR SSL Hostname Validation        (HADR_SSL_HOST_VAL) = OFF

 BUFFPAGE size to be used by optimizer   (OPT_BUFFPAGE) = 0
 LOCKLIST size to be used by optimizer   (OPT_LOCKLIST) = 0
 MAXLOCKS size to be used by optimizer   (OPT_MAXLOCKS) = 0
 SORTHEAP size to be used by optimizer   (OPT_SORTHEAP) = 0
""".strip()

DB2_CONFIGURATION_USER_EMPTY = ""

DB2_CONFIGURATION_USER_INCORRECT = """

       Database Configuration for Database TESTD1

""".strip()


DB2_MANAGER_CONFIGURATION = """

          Database Manager Configuration

     Node type = Enterprise Server Edition with local and remote clients

 Database manager configuration release level            = 0x1500

 CPU speed (millisec/instruction)             (CPUSPEED) = 3.306409e-07
 Communications bandwidth (MB/sec)      (COMM_BANDWIDTH) = 1.000000e+02

 Max number of concurrently active databases     (NUMDB) = 32
 Federated Database System Support           (FEDERATED) = NO
 Transaction processor monitor name        (TP_MON_NAME) =

 Default charge-back account           (DFT_ACCOUNT_STR) =

 Java Development Kit installation path       (JDK_PATH) = /home/dbp/sqllib/java/jdk64

 Diagnostic error capture level              (DIAGLEVEL) = 3
 Notify Level                              (NOTIFYLEVEL) = 3
 Diagnostic data directory path               (DIAGPATH) = /home/dbp/sqllib/db2dump/ $m
 Current member resolved DIAGPATH                        = /home/dbp/sqllib/db2dump/DIAG0000/
 Alternate diagnostic data directory path (ALT_DIAGPATH) =
 Current member resolved ALT_DIAGPATH                    =
 Size of rotating db2diag & notify logs (MB)  (DIAGSIZE) = 0

 Default database monitor switches
   Buffer pool                         (DFT_MON_BUFPOOL) = OFF
   Lock                                   (DFT_MON_LOCK) = OFF
   Sort                                   (DFT_MON_SORT) = OFF
 WLM dispatcher min. utilization (%) (WLM_DISP_MIN_UTIL) = 5

 Communication buffer exit library list (COMM_EXIT_LIST) =
 Current effective arch level         (CUR_EFF_ARCH_LVL) = V:11 R:5 M:9 F:0 I:0 SB:0
 Current effective code level         (CUR_EFF_CODE_LVL) = V:11 R:5 M:9 F:0 I:0 SB:0

 Keystore type                           (KEYSTORE_TYPE) = NONE
 Keystore location                   (KEYSTORE_LOCATION) =

 Path to python runtime                    (PYTHON_PATH) =
 Path to R runtime                              (R_PATH) =

 Multipart upload part size            (MULTIPARTSIZEMB) = 100
""".strip()

DB2_MANAGER_CONFIGURATION_EMPTY = ""

DB2_MANAGER_CONFIGURATION_INCORRECT = """

          Database Manager Configuration

""".strip()

db2_databases_configuration_path = "insights_commands/runuser_-l_dbp_-c_db2_get_database_configuration_for_TESTD1"
db2_database_manager_path = "insights_commands/runuser_-l_dbp_-c_db2_-c_db2_get_dbm_cfg"


def test_db2ls():
    db2ls = Db2ls(context_wrap(DB2LS_A_C))
    assert len(db2ls) == 2
    assert db2ls[0]['PATH'] == '/opt/ibm/db2/V11.5'
    assert db2ls[0]['VRMF'] == '11.5.6.0'
    assert db2ls[0]['FIXPACK'] == '0'
    assert db2ls[0]['SPECIAL'] == ''
    assert db2ls[0]['INSTALLTIME'] == 'Fri Jan 14 20:20:07 2022 CST'
    assert db2ls[0]['INSTALLERUID'] == '0'
    assert db2ls[1]['PATH'] == '/opt/ibm/db2/V11.5_01'
    assert db2ls[1]['VRMF'] == '11.5.7.0'
    assert db2ls[1]['FIXPACK'] == '0'
    assert db2ls[1]['SPECIAL'] == ''
    assert db2ls[1]['INSTALLTIME'] == 'Fri Feb 11 10:34:51 2022 CST'
    assert db2ls[1]['INSTALLERUID'] == '0'

    with pytest.raises(SkipComponent):
        Db2ls(context_wrap(DB2LS_A_C_EMPTY1))
    with pytest.raises(SkipComponent):
        Db2ls(context_wrap(DB2LS_A_C_EMPTY2))


def test_db2_databases_configuration():
    db2_configuration_user = db2.Db2DatabaseConfiguration(context_wrap(DB2_CONFIGURATION_USER, path=db2_databases_configuration_path))
    assert db2_configuration_user["Database configuration release level"] == "0x1500"
    assert db2_configuration_user["user"] == "dbp"
    assert db2_configuration_user["db_name"] == "TESTD1"

    with pytest.raises(SkipComponent) as e:
        db2.Db2DatabaseConfiguration(context_wrap(DB2_CONFIGURATION_USER_EMPTY, path=db2_databases_configuration_path))
    assert "The result is empty" in str(e)

    with pytest.raises(SkipComponent) as e:
        db2.Db2DatabaseConfiguration(context_wrap(DB2_CONFIGURATION_USER_INCORRECT, path=db2_databases_configuration_path))
    assert "The format is incorrect" in str(e)


def test_db2_database_manager():
    db2_manager_configuration = db2.Db2DatabaseManager(context_wrap(DB2_MANAGER_CONFIGURATION, path=db2_database_manager_path))
    assert db2_manager_configuration["Max number of concurrently active databases     (NUMDB)"] == "32"
    assert db2_manager_configuration["user"] == "dbp"

    with pytest.raises(SkipComponent) as e:
        db2.Db2DatabaseManager(context_wrap(DB2_MANAGER_CONFIGURATION_EMPTY, path=db2_database_manager_path))
    assert "The result is empty" in str(e)

    with pytest.raises(SkipComponent) as e:
        db2.Db2DatabaseManager(context_wrap(DB2_MANAGER_CONFIGURATION_INCORRECT, path=db2_database_manager_path))
    assert "The format is incorrect" in str(e)


def test_doc_examples():
    env = {
        'db2databaseconfiguration': db2.Db2DatabaseConfiguration(context_wrap(DB2_CONFIGURATION_USER, path=db2_databases_configuration_path)),
        'db2databasemanager': db2.Db2DatabaseManager(context_wrap(DB2_MANAGER_CONFIGURATION, path=db2_database_manager_path)),
        'db2ls': Db2ls(context_wrap(DB2LS_A_C))
    }
    failed, total = doctest.testmod(db2, globs=env)
    assert failed == 0
