import pytest
import doctest
from insights.tests import context_wrap
from insights.parsers import SkipException, db2
from insights.parsers.db2 import Db2ls

DB2LS_A_C = """
#PATH:VRMF:FIXPACK:SPECIAL:INSTALLTIME:INSTALLERUID
/opt/ibm/db2/V11.5:11.5.6.0:0 ::Fri Jan 14 20:20:07 2022 CST :0
/opt/ibm/db2/V11.5_01:11.5.7.0:0 ::Fri Feb 11 10:34:51 2022 CST :0
"""

DB2LS_A_C_EMPTY1 = ""
DB2LS_A_C_EMPTY2 = "#PATH:VRMF:FIXPACK:SPECIAL:INSTALLTIME:INSTALLERUID"


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

    with pytest.raises(SkipException):
        Db2ls(context_wrap(DB2LS_A_C_EMPTY1))
    with pytest.raises(SkipException):
        Db2ls(context_wrap(DB2LS_A_C_EMPTY2))


def test_db2ls_doc_examples():
    env = {'db2ls': Db2ls(context_wrap(DB2LS_A_C))}
    failed, total = doctest.testmod(db2, globs=env)
    assert failed == 0
