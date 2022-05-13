import doctest
import pytest

from insights.parsers import lpstat
from insights.parsers.lpstat import LpstatPrinters, LpstatProtocol, SkipException
from insights.tests import context_wrap


LPSTAT_P_OUTPUT = """
printer idle_printer is idle.  enabled since Fri 20 Jan 2017 09:55:50 PM CET
printer disabled_printer disabled since Wed 15 Feb 2017 12:01:11 PM EST -
    reason unknown
printer processing_printer now printing local_printer-1234.  enabled since Wed 15 Feb 2017 12:01:11 PM EST
"""

LPSTAT_P_OUTPUT_UKNOWN_STATE = """
printer unknown_printer may be jammed.  enabled since Fri 20 Jan 2017 09:55:50 PM CET
"""


LPSTAT_V_OUTPUT = """
device for test_printer1: ipp
device for test_printer2: ipp
device for savtermhpc: implicitclass:savtermhpc
device for A1: marshaA1:/tmp/A1
""".strip()

LPSTAT_V_OUTPUT_INVALID_1 = """
""".strip()

LPSTAT_V_OUTPUT_INVALID_2 = """
lpstat: Transport endpoint is not connected
""".strip()


def test_lpstat_parse():
    lpstat = LpstatPrinters(context_wrap(LPSTAT_P_OUTPUT))

    assert len(lpstat.printers) == 3

    idle_printer = lpstat.printers[0]
    disabled_printer = lpstat.printers[1]
    processing_printer = lpstat.printers[2]

    assert set(idle_printer) == set(['name', 'status']), \
        'Printer dict should contain (only) "name" and "status" keys'
    assert idle_printer['name'] == 'idle_printer'
    assert idle_printer['status'] == 'IDLE'

    assert set(disabled_printer) == set(['name', 'status']), \
        'Printer dict should contain (only) "name" and "status" keys'
    assert disabled_printer['name'] == 'disabled_printer'
    assert disabled_printer['status'] == 'DISABLED'

    assert set(processing_printer) == set(['name', 'status']), \
        'Printer dict should contain (only) "name" and "status" keys'
    assert processing_printer['name'] == 'processing_printer'
    assert processing_printer['status'] == 'PROCESSING'


def test_lpstat_parse_unknown_state():
    lpstat = LpstatPrinters(context_wrap(LPSTAT_P_OUTPUT_UKNOWN_STATE))

    assert len(lpstat.printers) == 1
    unknown_printer = lpstat.printers[0]

    assert set(unknown_printer) == set(['name', 'status']), \
        'Printer dict should contain (only) "name" and "status" keys'
    assert unknown_printer['name'] == 'unknown_printer'
    assert unknown_printer['status'] == 'UNKNOWN'


@pytest.mark.parametrize('status,expected_name', [
    ('IDLE', 'idle_printer'),
    ('DISABLED', 'disabled_printer'),
    ('PROCESSING', 'processing_printer'),
])
def test_lpstat_printer_names_by_status(status, expected_name):
    lpstat = LpstatPrinters(context_wrap(LPSTAT_P_OUTPUT))
    names = lpstat.printer_names_by_status(status)
    assert names == [expected_name]


def test_lpstat_protocol():
    lpstat_protocol = LpstatProtocol(context_wrap(LPSTAT_V_OUTPUT))
    assert lpstat_protocol["test_printer1"] == "ipp"
    assert lpstat_protocol["savtermhpc"] == "implicitclass"


def test_lpstat_protocol_invalid_state():
    with pytest.raises(SkipException) as exc:
        LpstatProtocol(context_wrap(LPSTAT_V_OUTPUT_INVALID_1))
    assert 'No Valid Output' in str(exc)

    with pytest.raises(SkipException) as exc:
        LpstatProtocol(context_wrap(LPSTAT_V_OUTPUT_INVALID_2))
    assert 'No Valid Output' in str(exc)


def test_lpstat_doc_examples():
    env = {
        'lpstat_printers': LpstatPrinters(context_wrap(LPSTAT_P_OUTPUT)),
        'lpstat_protocol': LpstatProtocol(context_wrap(LPSTAT_V_OUTPUT))
    }
    failed, total = doctest.testmod(lpstat, globs=env)
    assert failed == 0
