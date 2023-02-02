import doctest
import pytest

from insights.core.exceptions import ParseException, SkipComponent
from insights.parsers import smbstatus
from insights.parsers.smbstatus import SmbstatusS, Smbstatusp, Statuslist
from insights.tests import context_wrap

SMBSTATUSS = """

Service      pid     Machine       Connected at                     Encryption   Signing
---------------------------------------------------------------------------------------------
share_test1  12668   10.66.208.149 Wed Sep 27 10:33:55 AM 2017 CST  -            -
share_test2  12648   10.66.208.159 Wed Sep 27 11:33:55 AM 2017 CST  -            -
share_test3  13628   10.66.208.169 Wed Sep 27 12:33:55 AM 2017 CST  -            -

"""

SMBSTATUSP = """

Samba version 4.6.2
PID     Username     Group        Machine                                   Protocol Version  Encryption           Signing
----------------------------------------------------------------------------------------------------------------------------------------
12668   testsmb       zjjsmb       10.66.208.149 (ipv4:10.66.208.149:44376)  SMB2_02           -                    -
12648   test2smb      test2smb     10.66.208.159 (ipv4:10.66.208.159:24376)  SMB2_02           -                    -
13628   test3smb      test3smb     10.66.208.169 (ipv4:10.66.208.169:34376)  SMB2_02           -                    -
"""

SMBSTATUSS_EXP = """

xService      pid     Machine       Connected at                     Encryption   Signing
---------------------------------------------------------------------------------------------
share_test1  12668   10.66.208.149 Wed Sep 27 10:33:55 AM 2017 CST  -            -
share_test2  12648   10.66.208.159 Wed Sep 27 11:33:55 AM 2017 CST  -            -
share_test3  13628   10.66.208.169 Wed Sep 27 12:33:55 AM 2017 CST  -            -

"""

SMBSTATUSP_EXP1 = """
Can't open sessionid.tdb
"""

SMBSTATUSP_EXP2 = """
"""

SMBSTATUSP_DOC = """
Samba version 4.6.2
PID     Username     Group        Machine                                   Protocol Version  Encryption           Signing
--------------------------------------------------------------------------------------------------------------------------
12668   testsmb       testsmb       10.66.208.149 (ipv4:10.66.208.149:44376)  SMB2_02           -                    -
"""

SMBSTATUSS_DOC = """
Service      pid     Machine       Connected at                     Encryption   Signing
----------------------------------------------------------------------------------------
share_test   13668   10.66.208.149 Wed Sep 27 10:33:55 AM 2017 CST  -            -
"""


def test_smbstatuss():
    smbstatuss = SmbstatusS(context_wrap(SMBSTATUSS))
    assert smbstatuss.data[2]["pid"] == '13628'
    assert smbstatuss.data[1]["Connected_at"] == 'Wed Sep 27 11:33:55 AM 2017 CST'
    assert smbstatuss.data[1]["Encryption"] == '-'
    for result in smbstatuss:
        if result["Service"] == "share_test1":
            assert result["pid"] == "12668"


def test_smbstatusp():
    smbstatusp = Smbstatusp(context_wrap(SMBSTATUSP))
    assert smbstatusp.data[2]["Username"] == 'test3smb'
    assert smbstatusp.data[1]["Protocol_Version"] == 'SMB2_02'
    assert smbstatusp.data[1]["Signing"] == '-'
    for result in smbstatusp:
        if result["PID"] == "12668":
            assert result["Username"] == "testsmb"


def test_statuslist_empty_exp():
    with pytest.raises(SkipComponent) as pe:
        Statuslist(context_wrap(''))
        assert "Empty content." in str(pe)


def test_statuslist_exp():
    with pytest.raises(ParseException) as pe:
        Statuslist(context_wrap("Can't open sessionid.tdb"))
        assert "Can't open sessionid.tdb" in str(pe)


def test_smbstatusS_exp():
    with pytest.raises(ParseException) as pe:
        SmbstatusS(context_wrap(SMBSTATUSS_EXP))
        assert "Cannot find the header line." in str(pe)


def test_smbstatusp_exp():
    with pytest.raises(ParseException) as pe:
        Smbstatusp(context_wrap(SMBSTATUSP_EXP1))
        assert "Cannot find the header line." in str(pe)

    with pytest.raises(SkipComponent) as pe:
        Smbstatusp(context_wrap(SMBSTATUSP_EXP2))
        assert "Empty content." in str(pe)


def test_smbstatus_doc():
    env = {
        'SmbstatusS': SmbstatusS,
        'smbstatuss_info': SmbstatusS(context_wrap(SMBSTATUSS_DOC)),
        'Smbstatusp': Smbstatusp,
        'smbstatusp_info': Smbstatusp(context_wrap(SMBSTATUSP_DOC))
    }
    failed, total = doctest.testmod(smbstatus, globs=env)
    assert failed == 0
