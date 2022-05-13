from insights.tests import context_wrap
from insights.parsers.auditctl_status import AuditctlStatus
from insights.parsers import ParseException
import pytest

NORMAL_AUDS_RHEL6 = """
AUDIT_STATUS: enabled=1 flag=1 pid=1483 rate_limit=0 backlog_limit=8192 lost=3 backlog=0
""".strip()

NORMAL_AUDS_RHEL7 = """
enabled 1
failure 1
pid 947
rate_limit 0
backlog_limit 320
lost 0
backlog 0
loginuid_immutable 1 locked
""".strip()

BLANK_INPUT_SAMPLE = """
""".strip()

BAD_INPUT_SAMPLE = """
Unknown: type=0, len=0
""".strip()

BAD_INPUT_MIX = """
Unknown: type=0, len=0
enabled 1
""".strip()


def test_normal_auds_rhel6():
    auds = AuditctlStatus(context_wrap(NORMAL_AUDS_RHEL6))
    assert "enabled" in auds
    assert "loginuid_immutable" not in auds
    assert auds['pid'] == 1483


def test_normal_auds_rhel7():
    auds = AuditctlStatus(context_wrap(NORMAL_AUDS_RHEL7))
    assert "loginuid_immutable" in auds
    assert auds['loginuid_immutable'] == "1 locked"
    assert auds['failure'] == 1
    assert auds.get('nonexists') is None


def test_auds_blank_input():
    ctx = context_wrap(BLANK_INPUT_SAMPLE)
    with pytest.raises(ParseException) as sc:
        AuditctlStatus(ctx)
    assert "Input content is empty." in str(sc)


def test_auds_bad_input():
    auds = AuditctlStatus(context_wrap(BAD_INPUT_SAMPLE))
    assert auds.data == {}


def test_auds_bad_input_mix():
    auds = AuditctlStatus(context_wrap(BAD_INPUT_MIX))
    assert "enabled" in auds
