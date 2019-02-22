from insights.parsers import sapcontrol, SkipException, ParseException
from insights.parsers.sapcontrol import SAPControlSystemUpdateList
from insights.tests import context_wrap
import pytest
import doctest

RKS_STATUS = """
[
 {"hostname":"vm37-39","instanceNr":"00","status":"Running","starttime":"29.01.201900:00:02","endtime":"29.01.201901:10:11","dispstatus":"GREEN"},
 {"hostname":"vm37-39","instanceNr":"02","status":"Running","starttime":"29.01.201900:00:05","endtime":"29.01.201901:11:11","dispstatus":"GREEN"},
 {"hostname":"vm37-39","instanceNr":"03","status":"Running","starttime":"29.01.201900:00:05","endtime":"29.01.201901:12:36","dispstatus":"GREEN"}
]
""".strip()

RKS_STATUS_AB1 = """
""".strip()


RKS_STATUS_AB2 = """
29.01.2019 01:20:26
GetSystemUpdateList
FAIL: NIECONN_REFUSED (Connection refused), NiRawConnect failed in plugin_fopen()
""".strip()


def test_sapcontrol_rks_abnormal():
    with pytest.raises(SkipException):
        SAPControlSystemUpdateList(context_wrap(RKS_STATUS_AB1))
    with pytest.raises(ParseException):
        SAPControlSystemUpdateList(context_wrap(RKS_STATUS_AB2))


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
