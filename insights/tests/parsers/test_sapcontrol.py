from insights.parsers import sapcontrol, SkipException, ParseException
from insights.parsers.sapcontrol import SAPControlSystemUpdateList
from insights.tests import context_wrap
import pytest
import doctest

RKS_STATUS = """
29.01.2019 01:20:36
GetSystemUpdateList
OK
hostname, instanceNr, status, starttime, endtime, dispstatus
vm37-39, 00, Running, 29.01.2019 00:00:02, 29.01.2019 01:10:11, GREEN
vm37-39, 02, Running, 29.01.2019 00:00:05, 29.01.2019 01:11:11, GREEN
vm37-39, 03, Running, 29.01.2019 00:00:05, 29.01.2019 01:12:36, GREEN
""".strip()

RKS_STATUS_AB1 = """
""".strip()

RKS_STATUS_AB2 = """
29.01.2019 01:20:26
GetSystemUpdateList
FAIL: NIECONN_REFUSED (Connection refused), NiRawConnect failed in plugin_fopen()
""".strip()

RKS_STATUS_AB3 = """
29.01.2019 01:20:36
GetSystemUpdateList
OK
hostname, instanceNr, status, starttime, endtime, dispstatus
""".strip()


def test_sapcontrol_rks_abnormal():
    with pytest.raises(SkipException):
        SAPControlSystemUpdateList(context_wrap(RKS_STATUS_AB1))
    with pytest.raises(ParseException):
        SAPControlSystemUpdateList(context_wrap(RKS_STATUS_AB2))
    with pytest.raises(SkipException):
        SAPControlSystemUpdateList(context_wrap(RKS_STATUS_AB3))


def test_sapcontrol_status():
    rks = SAPControlSystemUpdateList(context_wrap(RKS_STATUS))
    assert rks.is_running
    assert rks.is_green
    assert rks.data[0]['status'] == "Running"
    assert rks.data[1]['instanceNr'] == "02"
    assert rks.data[-1]['dispstatus'] == "GREEN"


def test_doc_examples():
    env = {
            'rks': SAPControlSystemUpdateList(context_wrap(RKS_STATUS)),
          }
    failed, total = doctest.testmod(sapcontrol, globs=env)
    assert failed == 0
