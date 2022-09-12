import pytest
import doctest
from insights.tests import context_wrap
from insights.parsers import ibm_proc, SkipException
from insights.parsers.ibm_proc import IBMPpcLparCfg, IBMFirmwareLevel


PROC_PPC_LPARCFG = """
serial_number=IBM,123456789
system_type=IBM,8247-22L
""".strip()

PROC_IBM_FWL = """
FW950.30 (VL950_092)\x00
""".strip()

PROC_IBM_FWL_NG = """
FW950.30 VL950_092\x00
""".strip()


def test_ibm_proc():
    results = IBMPpcLparCfg(context_wrap(PROC_PPC_LPARCFG))
    assert results['system_type'] == '8247-22L'
    assert results['serial_number'] == '123456789'

    results = IBMFirmwareLevel(context_wrap(PROC_IBM_FWL))
    assert results.firmware_level == 'VL950_092'


def test_ibm_proc_empty():
    with pytest.raises(SkipException):
        IBMPpcLparCfg(context_wrap(''))

    with pytest.raises(SkipException):
        IBMFirmwareLevel(context_wrap(''))

    with pytest.raises(SkipException):
        IBMFirmwareLevel(context_wrap(PROC_IBM_FWL_NG))


def test_ibm_proc_doc_examples():
    env = {
        "ibm_mtm": IBMPpcLparCfg(context_wrap(PROC_PPC_LPARCFG)),
        "ibm_fwl": IBMFirmwareLevel(context_wrap(PROC_IBM_FWL))
    }
    failed, total = doctest.testmod(ibm_proc, globs=env)
    assert failed == 0
