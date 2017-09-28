from insights.parsers.smbstatus import SmbstatusS, Smbstatusp
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
