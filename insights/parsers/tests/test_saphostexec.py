from insights.parsers import saphostexec, SkipException
from insights.parsers.saphostexec import SAPHostExecStatus, SAPHostExecVersion
from insights.tests import context_wrap
import pytest
import doctest

STATUS_DOC = """
saphostexec running (pid = 9159)
sapstartsrv running (pid = 9163)
saposcol running (pid = 9323)
""".strip()

STATUS_ABNORMAL = """
saphostexec running (pid = 9159)
sapstartsrv run (pid = 9163)
saposcol (pid = 9323)
""".strip()

VER_DOC = """
*************************** Component ********************
/usr/sap/hostctrl/exe/saphostexec: 721, patch 1011, changelist 1814854, linuxx86_64, opt (Jan 13 2018, 04:43:56)
/usr/sap/hostctrl/exe/sapstartsrv: 721, patch 1011, changelist 1814854, linuxx86_64, opt (Jan 13 2018, 04:43:56)
/usr/sap/hostctrl/exe/saphostctrl: 721, patch 1011, changelist 1814854, linuxx86_64, opt (Jan 13 2018, 04:43:56)
/usr/sap/hostctrl/exe/xml71d.so: 721, patch 1011, changelist 1814854, linuxx86_64, opt (Jan 13 2018, 01:12:10)
**********************************************************
--------------------
SAPHOSTAGENT information
--------------------
kernel release                721
kernel make variant           721_REL
compiled on                   Linux GNU SLES-9 x86_64 cc4.1.2  for linuxx86_64
compiled for                  64 BIT
compilation mode              Non-Unicode
compile time                  Jan 13 2018 04:40:52
patch number                  33
latest change number          1814854
---------------------
supported environment
---------------------
operating system
Linux 2.6
Linux 3
Linux
""".strip()

SHA_STOP = """
saphostexec stopped
""".strip()


def test_saphostexec_status_abnormal():
    with pytest.raises(SkipException) as s:
        SAPHostExecStatus(context_wrap(STATUS_ABNORMAL))
    assert "Incorrect status: 'sapstartsrv run (pid = 9163)'" in str(s)
    assert "Incorrect status: 'saposcol (pid = 9,23)'" not in str(s)


def test_saphostexec_status():
    sha_status = SAPHostExecStatus(context_wrap(STATUS_DOC))
    assert sha_status.is_running is True
    assert sha_status.services['saphostexec'] == '9159'
    assert 'saposcol' in sha_status

    sha_status = SAPHostExecStatus(context_wrap(SHA_STOP))
    assert sha_status.is_running is False
    assert sha_status.services == {}
    assert 'saposcol' not in sha_status


def test_saphostexec_version():
    sha_ver = SAPHostExecVersion(context_wrap(VER_DOC))
    assert sha_ver.components['saphostexec'].version == '721'
    assert sha_ver.components['saphostexec'].patch == '1011'
    assert sha_ver.components['xml71d.so'].changelist == '1814854'
    assert 'abc' not in sha_ver


def test_doc_examples():
    env = {
            'sha_status': SAPHostExecStatus(context_wrap(STATUS_DOC)),
            'sha_version': SAPHostExecVersion(context_wrap(VER_DOC)),
          }
    failed, total = doctest.testmod(saphostexec, globs=env)
    assert failed == 0
